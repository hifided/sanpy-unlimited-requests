import json
import requests
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanError


# list of proxies is stored in a hardcoded file "proxy.txt" in folder near your main.py
# proxy.txt structure: login:password@ip:port or ip:port
# Content example:
### proxy.txt ###
# usr1:123@111.222.333.44:8000
# 123.456.7.8:8080
# usr2:abc000@44.55.66.77:8000
#       ...
proxy_list_file = "proxy.txt"
# read proxies into list
def get_proxy_list():
    result = []
    try:
        with open(proxy_list_file, "r") as prf:
            result = prf.read().splitlines()   
            return result
    except EnvironmentError:
        print("Can't open file {}\n".format(proxy_file))
        return []
    except FileNotFoundError:
        print("Wrong file or file path: {}\n".format(proxy_file))
        return []
    else:
        print("Unknown file error\n")
        return []
# list of proxies
proxies = get_proxy_list()
# first try without proxy
proxy_struct = {}

# change proxy if previous stop working
def get_new_proxy():
    # first entry in the proxies list
    new_proxy = proxies[0]
    proxy_struct = {
        'http': f'http://{new_proxy}',
        'https': f'http://{new_proxy}'
    }
    print("try change proxy to " + str(new_proxy))
    # subfunction to move used proxy into the end of proxies list
    proxies.append(proxies.pop(0))
    return proxy_struct

def execute_gql(gql_query_str):
    global proxy_struct
    headers = {}
    response = ''
    # iterator over the number of proxy records in a "proxy.txt"
    counter = len(proxies)
    first_request_flag = 1
    
    if ApiConfig.api_key:
        headers = {'authorization': "Apikey {}".format(ApiConfig.api_key)}
    while counter > 0 or first_request_flag:
        first_request_flag = 0
        try:
            response = requests.post(
                SANBASE_GQL_HOST,
                json={'query': gql_query_str},
                headers=headers,
                proxies=proxy_struct)
        except requests.exceptions.RequestException as e:
            raise SanError('Error running query: ({})'.format(e))

        # status code 429 - request API limit, 404 - Not Found, 500 - Internal Server Error
        if counter > 0 and response.status_code in (404, 429, 500):
            # change proxy if error
            proxy_struct = get_new_proxy()
            # proxies list next step
            counter -= 1
            continue
        # status code 200 - success
        elif response.status_code == 200:
            return __handle_success_response__(response, gql_query_str)
        else:
            if __result_has_gql_errors__(response):
                error_response = response.json()['errors']['details']
            else:
                error_response = ''
            raise SanError(
                "Error running query. Status code: {}.\n {}\n {}".format(
                    response.status_code,
                    error_response,
                    gql_query_str))

    if __result_has_gql_errors__(response):
        error_response = response.json()['errors']['details']
    else:
        error_response = ''
    raise SanError(
        "Error running query. Status code: {}.\n {}\n {}".format(
            response.status_code,
            error_response,
            gql_query_str))

def get_response_headers(gql_query_str):
    headers = {}
    if ApiConfig.api_key:
        headers = {'authorization': "Apikey {}".format(ApiConfig.api_key)}

    try:
        response = requests.post(
            SANBASE_GQL_HOST,
            json={'query': gql_query_str},
            headers=headers)
    except requests.exceptions.RequestException as e:
        raise SanError('Error running query: ({})'.format(e))
    
    if response.status_code == 200:
        return response.headers
    else:
        if __result_has_gql_errors__(response):
            error_response = response.json()['errors']['details']
        else:
            error_response = ''
        raise SanError(
            "Error running query. Status code: {}.\n {}\n {}".format(
                response.status_code,
                error_response,
                gql_query_str))


def __handle_success_response__(response, gql_query_str):
    if __result_has_gql_errors__(response):
        raise SanError(
            "GraphQL error occured running query {} \n errors: {}".format(
                gql_query_str,
                response.json()['errors']))
    elif __exist_not_empty_result(response):
        return response.json()['data']
    else:
        raise SanError(
            "Error running query, the results are empty. Status code: {}.\n {}" .format(
                response.status_code,
                gql_query_str))


def __result_has_gql_errors__(response):
    return 'errors' in response.json().keys()


def __exist_not_empty_result(response):
    return 'data' in response.json().keys() and len(
        list(
            filter(
                lambda x: x is not None,
                response.json()['data'].values()))) > 0
