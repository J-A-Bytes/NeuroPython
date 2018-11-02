"""
The neuro_call model contains the neuro_call function
"""
import os
import json
import requests
import urllib3



def neuro_call(port, service, method, requestbody, timeout=1200, retry=True):
    """
    The neuro_call function provides a way of making authorised calls to the Neuroverse api
    """
    token = os.environ['JUPYTER_TOKEN']
    if 'prd' in os.environ['NV_DOMAIN']:
        #this will need to be updated when the certificate expires
        domain = 'https://15ded47f-ef38-4ee3-b989-685820ca3d36.cloudapp.net'
    elif 'tst' in os.environ['NV_DOMAIN']:
        domain = 'https://neuroqa.d3s.com.au'
    elif 'sit' in os.environ['NV_DOMAIN']:
        domain = 'https://neurosit.d3s.com.au'
    elif 'dev' in os.environ['NV_DOMAIN']:
        domain = 'https://neurodev.d3s.com.au'
    else:
        domain = 'http://localhost'

    url = domain + ":8080/NeuroApi/" + port + "/" + service + "/api/"
    url += service.lower().replace("service", "") + "/" + method
    if domain == "http://localhost":
        url = domain + ":8082/NeuroApi/" + port + "/" + service
        url += "/api/" + service.lower().replace("service", "") + "/" + method
    msg_data = json.dumps(requestbody, default=lambda o: o.__dict__)
    msg_data_length = len(msg_data)
    headers = {'Content-Length' : str(msg_data_length), 'Token' : token}
    urllib3.disable_warnings()
    try:
        response = requests.post(url, headers=headers, data=msg_data, verify=False,
                                 timeout=timeout)
    except Exception as err:
        if retry:
            response = requests.post(url, headers=headers, data=msg_data, verify=False,
                                 timeout=timeout)
        else:
            raise err
    if response.status_code != 200:
        if retry:
            response = requests.post(url, headers=headers, data=msg_data, verify=False,
                                     timeout=timeout)
        if response.status_code != 200:
            if response.status_code == 401:
                raise Exception("""
                Session has expired:
                Log into Neuroverse and connect to your Notebooks session or
                reload the Notebooks page in Neuroverse
                """)
            elif response.status_code == 404:
                raise Exception("""
                Session has expired:
                Log into Neuroverse and connect to your Notebooks session or
                reload the Notebooks page in Neuroverse
                """)
            else:
                raise Exception('Neuroverse connection error: Http code ' + str(response.status_code))
    try:
        response_obj = response.json()
        errCode = response_obj["ErrorCode"]
    except Exception as err:
        if retry:
            response = requests.post(url, headers=headers, data=msg_data, verify=False,
                                     timeout=timeout)
            if response.status_code != 200:
                if response.status_code == 401:
                    raise Exception("""
                    Session has expired:
                    Log into Neuroverse and connect to your Notebooks session or
                    reload the Notebooks page in Neuroverse
                    """)
                elif response.status_code == 404:
                    raise Exception("""
                    Session has expired:
                    Log into Neuroverse and connect to your Notebooks session or
                    reload the Notebooks page in Neuroverse
                    """)
                else:
                    raise Exception('Neuroverse connection error: Http code ' + str(response.status_code))
            response_obj = response.json()
            errCode = response_obj["ErrorCode"]
        else:
            raise err
    if errCode is not 0:
        raise Exception("Neuroverse Error: " + response_obj["Error"])
    return response_obj
