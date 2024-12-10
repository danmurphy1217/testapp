from .client import _HttpClient

client = _HttpClient(limit_per_host=35)

# NOTE: when adding a new client, please be sure to instantiate it above
# and include it in the below list. Otherwise, it will not be initialized
# properly when the job or server starts running.
HTTP_CLIENTS: list[_HttpClient] = [
    client,
]