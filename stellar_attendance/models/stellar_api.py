import json

import requests

STELLAR_URL = "https://rumytechnologies.com/rams/json_api"


class StellarAPI:
    def fetch_log(auth_user, auth_code, start_date, end_date, start_time="", end_time=""):
        data = {
            "operation": "fetch_log",
            "auth_user": auth_user,
            "auth_code": auth_code,
            "start_date": start_date,
            "end_date": end_date,
            "start_time": start_time,
            "end_time": end_time
        }
        post = json.loads(requests.post(STELLAR_URL, json=data).text)
        if post['log']:
            return post['log']
