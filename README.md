# SANPY UNLIMITED REQUESTS
authentic Santiment API Python Client with requests limit overcome using proxy
_____________________________________

## How it works
From sanpy README.md we know that "you can provide an API key which gives access to the restricted metrics":
```python
import san
san.ApiConfig.api_key = "your-api-key-here"
```

So what about metrics do not required authentication to get?
As we can see in *graphql.py* the sanpy database is accessed using the post method
```python
response = requests.post(
                SANBASE_GQL_HOST,
                json={'query': gql_query_str},
                headers=headers)
```
So... if we cannot be blocked by a token (cause we didn't authenticated yet), it can only be done by blocking requests from our IP.
Lets use proxy to break the rules :)
_____________________________________

## How to use

### install
You can install sanpy-unlimited-requests from source code (similar to installing original sanpy)
````
git clone 
python3 setup.py install
````
``.egg`` with sanpy source code will appear in python packages folder (``/usr/local/lib/python3.*/dist-packages/`` for Linux)
Installation complete. Now python can see ``import san`` package

### use
1) Don't use ``san.ApiConfig.api_key`` authentication
2) Put proxy list file with the static name "proxy.txt" next to your main.py (or any other file where the sanpy is called)
"proxy.txt" contains raws with proxy config like ``login:password@ip:port`` or ``ip:port`` (if proxy server does not require authentication)  
"proxy.txt" example:
````
user1:passwd@111.222.333.44:8000
55.66.77.8:8080
````
Updated sanpy will retry request to the database through the proxy from ``proxy.txt`` every time it reaches the SANAPI request limit.




