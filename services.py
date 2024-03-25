
import requests
import json

API = 'https://elyssa.tsaas.tn/api'

INIT_REQ = {
    "type": "init",
    "pays": "tunisie"
}


def get_init():
    print('Initiliazing')
    response = requests.post(url=API, json=INIT_REQ)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print('init request failed, status code: ', response.status_code)
        return response.text
