import requests
import settings
from django.core.cache import cache
from django.conf import settings as django_settings
import json


class C42APIProxy:
    """ A C42 API Proxy

    """
    def __init__(self):
        # The request object
        self.request_item = C42APIProxyRequest()
        # Setting the endpoints cache
        django_settings.configure(CACHES=settings.CACHE)

    def request(self, request_text):
        """ Performs a request to the C42 API Proxy

        :param request_text: the request text
        :return: the response to the request
        """
        # Reset the request
        self.request_item = C42APIProxyRequest()
        # Parse the request
        self.request_item.parse_request(request_text)
        # Check if request is valid
        if self.request_item.is_valid():
            self.request_item.process_request()
        # Request is invalid, so data should be None; check the status_code attribute through its getter
        return self.request_item.response.data

    def get_response(self):
        # Getter for the response
        return self.request_item.response.data

    def get_response_status_code(self):
        # Getter for the response status code
        return self.request_item.response.status_code

    def cache_clear(self):
        # Clearing the cache
        cache.clear()


class C42APIProxyRequest:
    """ A proxy request to the C42 API

        A distinct request class is implemented such that the proxy can be easily extended
        to perform other tasks and/or to be able to process multiple requests.
        The attributes names are self explanatory - check the README for more details.
    """
    def __init__(self):
        self.request_text = None
        self.command = None
        self.endpoint = None
        self.endpoint_param = None
        self.response = Response()
        self.headers = None
        self.from_cache = None

    def parse_request(self, request_text):
        """ Parsing the request text in order to get the required information

            The following request format is assumed:
                'command : uri'
            where 'uri' is of the following format:
                /endpoint/endpoint_param/
        """

        # The request is split based on the semicolon ':'
        request_split = request_text.split(':')

        # Get the command - the split should result in a list of length 2
        if len(request_split) == 2:
            self.command = request_split[0].strip()
            uri = request_split[1].strip('/ ')
        else:
            # Wrong decoded command so the response status code is set to "bad request"
            # TODO: check the HTTP standard (for all the below cases, not just this one)
            self.response.status_code = 400
            return

        # Get the endpoint - we split the uri based on the '/'
        uri_split = uri.split('/')
        # The split should result in a list of length 2
        if len(uri_split) == 2:
            self.endpoint = uri_split[0]
            self.endpoint_param = uri_split[1]
        else:
            # Wrong decoded command so the response status code is set to "bad request"
            self.response.status_code = 400
            return

        # The headers are assumed constant for now
        self.headers = settings.HEADERS

    def is_valid(self):
        """ Checking if the request is of a valid format

        :return: True if request is valid and False otherwise
        """
        # Check if the command is among the valid ones
        if self.command not in settings.VALID_COMMANDS:
            self.response.status_code = 400
            return False
        # Check if the endpoint is among the valid ones
        if self.endpoint not in settings.VALID_ENDPOINTS:
            self.response.status_code = 400
            return False
        return True

    def process_request(self):
        """ Processing the request

            Currently the request can be only an endpoint. Django's simple low-level cache API is employed. The cache
            key is unique, being formed by combining the endpoint and its parameter ('events-with-subscriptions' with
            the EVENT_ID in our case).
        """

        # Try to get the request response from the cache
        cache_value = cache.get(self.endpoint + self.endpoint_param)
        if cache_value is None:
            # Not found in cache, thus do the processing
            if self.endpoint == 'events-with-subscriptions':
                self.events_with_subscriptions()
            # Add the request response to the cache
            cache.set(self.endpoint + self.endpoint_param, self.response, settings.CACHE_TIMEOUT)
            # Updating the from_cache attribute
            self.from_cache = False
        else:
            # Found in cache, thus take it from there
            self.response = cache_value
            # NOTE: the cache should be updated when requests with changing commands (such as DELETE) are processed
            self.from_cache = True

    def events_with_subscriptions(self):
        """ Actual endpoint implementation

            The C42 API is accessed through the two different requests. The responses are combined only
            if the received responses are valid, i.e., the status_code == 200
        """
        if self.command == 'GET':
            # TODO: make it easier to add more fields in the combination through some configuration in settings.py

            # Get the event details (including title) from the C42 API
            # The URI is taken from settings.py - preparation for the configuration and allows for easy testing
            c42_api_uri = settings.ENDPOINTS[self.endpoint][0].format(self.endpoint_param)
            c42_api_request_event = self.c42_api_request(c42_api_uri, self.headers)

            # Get the event subscriptions (participants, including the name) from the C42 API
            c42_api_uri = settings.ENDPOINTS[self.endpoint][1].format(self.endpoint_param)
            c42_api_request_event_subscriptions = self.c42_api_request(c42_api_uri, headers=self.headers)

            # only if both C42 API responses are successful proceed further
            if c42_api_request_event.status_code == c42_api_request_event_subscriptions.status_code == 200:
                c42_api_request_event_data = c42_api_request_event.data
                c42_api_request_event_subscriptions_data = c42_api_request_event_subscriptions.data

                # Combining the results
                # TODO: add some checks (perhaps try except) to be sure that the json values are present
                response_data = {}
                response_data['id'] = c42_api_request_event_data['data'][0]['id']
                response_data['title'] = c42_api_request_event_data['data'][0]['title']
                response_data['names'] = []
                for d in c42_api_request_event_subscriptions_data['data']:
                    response_data['names'].append(d['subscriber']['first_name'])

                self.response.data = json.dumps(response_data)
                self.response.status_code = 200
            else:
                self.response.data = None
                self.response.status_code = 401

    @staticmethod
    def c42_api_request(uri, headers):
        """ General request method to access the C42 API

            It could be transformed into a separate method, outside this class (it is static now)

        :param uri: the URI of the request
        :param headers: the API headers
        :return: the response - should be checked for validity
        """
        response = Response()
        try:
            request = requests.get(uri, headers=headers)
        except requests.exceptions.MissingSchema:
            # TODO: check for other exceptions in the requests package and add them here if relevant
            response.data = None
            response.status_code = 'Invalid URI'
            # TODO: make this status code propagate at the output
        else:
            response.data = request.json()
            response.status_code = request.status_code
        return response

    def is_from_cache(self):
        # For testing purposes to know if the data was taken from the cache or not
        return self.from_cache

# TODO: Add the C42 API Proxy response special class


class Response:
    """ A general response class

    """
    def __init__(self):
        self.data = None
        self.status_code = None


def c42_api_request_example():
    """ Simple utilization example

        NOTE: Make sure that the TOKEN is correctly set in the settings.py file
    """

    # Starting the C42 API Proxy
    proxy = C42APIProxy()

    # Sending a request and gathering the response
    response = proxy.request("GET: /events-with-subscriptions/%s/" % settings.EVENT_ID)

    # Printing the request and the response
    print("c42apiproxy request:")
    print("GET: /events-with-subscriptions/%s/" % settings.EVENT_ID)
    print("c42apiproxy response:")
    print(response)

    # Getting the response status code if necessary
    response_status_code = str(proxy.get_response_status_code())

    # Printing the response status code
    print("c42apiproxy response status code: " + str(response_status_code))


if __name__ == '__main__':
    c42_api_request_example()
