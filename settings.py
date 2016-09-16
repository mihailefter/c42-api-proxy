VALID_COMMANDS = ['GET']
VALID_ENDPOINTS = ['events-with-subscriptions']
API_TOKEN = 'XXX'
EVENT_ID = 'XXX'

# C42 Headers
HEADERS = {
    'Accept': 'application/json',
    'Content-type': 'application/json',
    'Authorization': 'Token %s' % API_TOKEN
}

# Endpoints Django based cache configuration
CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
# The timeout value in seconds for the cache is 4.2 min = 252 s
CACHE_TIMEOUT = 252

# The URIs for the current endpoints
# TODO: to be extended as mentioned in the C42APIProxyRequest events_with_subscriptions() method
ENDPOINTS = {
    'events-with-subscriptions': [
        'https://demo.calendar42.com/api/v2/events/{0}/',
        'https://demo.calendar42.com/api/v2/event-subscriptions/?event_ids=[{0}]'
    ]
}
