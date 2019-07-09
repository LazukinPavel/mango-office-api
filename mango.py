import requests
import json

from datetime import datetime, timedelta

from .utils import encrypt_string


class MangoException(Exception):
    def __init__(self, error, *args, **kwargs):
        super(Exception).__init__(*args, **kwargs)
        self.error = error
        self.code = 422


class Mango(object):
    def __init__(self, vpbx_api_key, vpbx_api_salt):
        self.vpbx_api_key = vpbx_api_key
        self.vpbx_api_salt = vpbx_api_salt

    def _request_mango(self, path, params, csv_flag=False):
        base_url = 'https://app.mango-office.ru/vpbx/'
        url = base_url + path
        request_params = {**params}
        sign = self._get_sign(request_params)
        data = {
            'vpbx_api_key': self.vpbx_api_key,
            'sign': sign,
            'json': json.dumps(request_params),
        }
        try:
            if csv_flag:
                resp = requests.post(url, data=data).text
            else:
                resp = requests.post(url, data=data).json()
            return resp
        except Exception as exc:
            print(f'==== EXCEPTION {exc}')

    def _get_sign(self, request_params):
        json_request = json.dumps(request_params)
        sign = encrypt_string(f'{self.vpbx_api_key}{json_request}{self.vpbx_api_salt}')
        return sign

    def check_user(self, extension=None, flag='check'):
        path = 'config/users/request'
        request_params = {
            'extension': extension
        }
        resp = self._request_mango(path, request_params)
        if 'users' in resp:
            if flag == 'get':
                return resp['users']
            return True
        return False

    def check_stats(self):
        path = 'stats/request'
        date_to = datetime.now() + timedelta(hours=3)
        date_from = date_to - timedelta(days=1)
        date_to = int(date_to.timestamp())
        date_from = int(date_from.timestamp())

        request_params = {
            "date_from": date_from,
            "date_to": date_to,
        }

        get_key_response = self._request_mango(path, request_params)
        return self.get_stats(get_key_response)

    def get_stats(self, json_key):
        path = 'stats/result'
        resp = self._request_mango(path, json_key, csv_flag=True)
        return resp

        # TODO check is report ready? API response variants: 204 No content, 404 Not found, invalid key, 200 OK

    def get_user_info_dct(self, number):
        path = 'queries/user_info_by_dct_number'
        request_params = {
            'number': number
        }
        resp = self._request_mango(path, request_params)
        return resp
