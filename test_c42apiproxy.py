import c42apiproxy
import settings
import time
import unittest

EVENT_ID = settings.EVENT_ID

# starting the C42 API Proxy
test_proxy = c42apiproxy.C42APIProxy()


class C42APIProxyTest(unittest.TestCase):

    def test_correct_run(self):
        # Attention: it considers that the requests to the C42 API were correctly performed
        test_proxy.request("GET: /events-with-subscriptions/%s/" % EVENT_ID)
        self.assertEqual(test_proxy.get_response_status_code(), 200)

    def test_invalid_endpoint_after_invalid_command(self):
        # The fact that the request was not reset was discovered through this test
        test_proxy.request("GET/: /events-with-subscriptions/%s/" % EVENT_ID)
        test_proxy.request("GET: /events-with-subscriptions//%s/" % EVENT_ID)
        self.assertEqual(test_proxy.request_item.response.status_code, 400)

    def test_invalid_command(self):
        test_proxy.request("GE_T/: /events-with-subscriptions/%s/" % EVENT_ID)
        self.assertEqual(test_proxy.get_response_status_code(), 400)

    def test_invalid_endpoint(self):
        test_proxy.request("GET: /events-with-subscript/ions/%s/" % EVENT_ID)
        self.assertEqual(test_proxy.get_response_status_code(), 400)

    def test_invalid_endpoint_param(self):
        test_proxy.request("GET: /events-with-subscript/ions/%sfds/" % EVENT_ID)
        self.assertEqual(test_proxy.get_response_status_code(), 400)

    def test_invalid_endpoint_uri(self):
        # Clearing the cache, otherwise the value might be gotten from there, thus breaking the test
        test_proxy.cache_clear()
        # Changing the global URI variable
        settings.ENDPOINTS['events-with-subscriptions'][0] = 'fdsfsdf'
        test_proxy.request("GET: /events-with-subscriptions/%s/" % EVENT_ID)
        settings.ENDPOINTS['events-with-subscriptions'][0] = 'https://demo.calendar42.com/api/v2/events/{0}/'
        self.assertEqual(test_proxy.get_response_status_code(), 401)
        return

    def test_from_cache(self):
        # Attention: it considers that the requests to the C42 API were correctly performed
        test_proxy.request("GET: /events-with-subscriptions/%s/" % EVENT_ID)
        test_proxy.request("GET: /events-with-subscriptions/%s/" % EVENT_ID)
        self.assertEqual(test_proxy.request_item.is_from_cache(), True)

    def test_not_from_cache(self):
        # Attention: it considers that the requests to the C42 API were correctly performed
        test_proxy.cache_clear()
        test_proxy.request("GET: /events-with-subscriptions/%s/" % EVENT_ID)
        self.assertEqual(test_proxy.request_item.is_from_cache(), False)

    def test_cache_timeout(self):
        # Attention: it considers that the requests to the C42 API were correctly performed
        test_proxy.cache_clear()
        # Changing the global CACHE_TIMEOUT variable to 1 second
        settings.CACHE_TIMEOUT = 1
        test_proxy.request("GET: /events-with-subscriptions/%s/" % EVENT_ID)
        # Sleeping for 3 seconds
        time.sleep(3)
        test_proxy.request("GET: /events-with-subscriptions/%s/" % EVENT_ID)
        settings.CACHE_TIMEOUT = 252
        self.assertEqual(test_proxy.request_item.is_from_cache(), False)


if __name__ == '__main__':
    unittest.main()
