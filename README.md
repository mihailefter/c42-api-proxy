# A Simple C42 API Proxy

This repository contains the code for a simple C42 API proxy. The 
current implementation allows only a request of the type GET 
endpoint, i.e., "GET: /events-with-subscriptions/{id}", which returns 
the title and the attendees to a specific event according to the 
provided EVENT_ID. The code can be easily extended to include other 
commands and request endpoints.

# Installation and Prerequisites

- Developed under Python 3.5.2
- Django's simple low-level cache API is employed (Django 1.10 utilized
during development)
- The requests library is employed to access the C42 API (requests 
2.10.0 utilized during development)

# Implementation Details

## C42 API Proxy Request Flow in a Nutshell

Briefly, the request flow involves the following steps:

* parse the request to get the endpoint and the command 
* if both event and command are valid perform the request
  * if endpoint already in the cache get it from there and that's it 
  * else:
    * compose the requests for C42 API
    * send the C42 API requests
    * if valid C42 API responses:
      * get the C42 API proxy response
      * add the response to the cache and return
    * else return
* else return

## Details

The main core of the C42 API Proxy is the __C42APIProxyRequest__ class:

* __attributes__
  * _request_text_: the request input 
  * _command_: the command to be performed (parsed from the request_text)
  * _endpoint_: the endpoint to be performed (parsed from the request_text)
  * _endpoint_param_: endpoint parameters (in our case the EVENT_ID) 
  * _response_: the actual response
  * _from_cache_: keeps track if the response if from cache or not
  * _headers_: necessary for the C42 API requests
* __methods__
  * _parse_request_: parses the request_text to get the command, endpoint,
  and endpoint_param
  * _is_valid_: checks if the command and endpoint are within the valid
  ones
  * _process_request_: checks what kind of request it is and calls the 
  appropriate processing method
  * _events_with_subscriptions_: implements the actual endpoint request
  * _is_from_cache_: getter to know if the response was gathered from
  the cache or not
  * _c42_api_request_: accesses the C42 API

The __C42APIProxy__ class acts as an interface for the proxy:

* __attributes__
  * _request_item_: the actual request object 
* __methods__
  * _request_: proxy request interface method - starts the request_item
  formation; it returns the response in json format
  * _get_response_: getter for the response if required later
  * _get_response_status_code_: getter for the response status code
  * _cache_clear_: performs a cache clearance
  
### Request Format

The following format is considered for the request:
> command: uri

where _command_ is currently "GET" and the _uri_ is of the form:

> /endpoint/endpoint_param/

Example:
> GET: /events-with-subscriptions/$EVENT_ID/

### Response Format

 The result is a JSON data structure. For the above considered request
 endpoint example, the result is of the following format:
 
 
```js
{
  "id": "$EVENT_ID",
  "title": "Test Event",
  "names": ["Bob", "Ella"]
}
```

# Usage

Instantiate a C42APIProxy class. Start sending requests by employing 
its request method and passing the request text according to the above
described format. The method returns the response as a string. 
Note that the response status code can be as well obtained. 

## Note

Do not forget to set the API_TOKEN and EVENT_ID variables in the 
_settings.py_ file.

## Example

```python
import c42apiproxy
import json

# Starting the c42apiproxy
proxy = c42apiproxy.C42APIProxy()

# Sending a request and gathering the response
response = proxy.request("GET: /events-with-subscriptions/54654654/")

# Printing the request and the response
print("c42apiproxy request:")
print("GET: /events-with-subscriptions/54654654/")
print("c42apiproxy response:")
print(response)

# Getting the response status code if necessary
response_status_code = str(proxy.get_response_status_code())

# Printing the response status code
print("c42apiproxy response status code: " + str(response_status_code))
```
