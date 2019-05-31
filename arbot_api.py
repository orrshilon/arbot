import requests
import logging


class ArbotApi(object):
    def __init__(self,
                 host,
                 email,
                 password=None,
                 token=None,
                 user_id=None,
                 box_id=None,
                 box_location=None) -> None:
        super().__init__()
        self._host = host
        self._email = email
        self._password = password
        self._token = token
        self._user_id = user_id
        self._box_id = box_id
        self._box_location = box_location
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)
        if not self._token:
            self.login()

    def login(self):
        path = 'user/{}/session'.format(self._email)
        data = {
            'password': self._password,
            'email': self._email
        }
        content = self._request('post', path, data=data)
        self._token = content['token']
        self._user_id = content['user']['id']
        self._box_id = content['user']['locationBox']['boxFk']
        self._box_location = content['user']['locationBox']['location']

    def get_schedule(self, date):
        path = 'scheduleByDateList/{}'.format(self._box_id)
        params = {
            'date': date,
            'userId': self._user_id
        }
        schedule = self._get_with_authentication(path, params=params)
        if 'סטודיו' in schedule:
            return schedule['סטודיו'][0]
        return schedule

    def get_membership(self):
        path = 'membership/{}'.format(self._user_id)
        memberships = self._get_with_authentication(path)
        if memberships:
            return memberships[0]
        return None

    def register_for_workout(self, membership_id, schedule_id):
        path = 'scheduleUser'
        data = {
            'userFk': self._user_id,
            'scheduleFk': schedule_id,
            'membrshipUserFk': membership_id
        }
        return self._post_with_authentication(path, data=data)

    def _post_with_authentication(self, path, params=None, data=None):
        return self._request_with_authentication('post', path, params=params, data=data)

    def _get_with_authentication(self, path, params=None):
        return self._request_with_authentication('get', path, params=params)

    def _request_with_authentication(self, method, path, params=None, data=None):
        headers = {'accessToken': self._token}
        return self._request(method, path, params, data, headers)

    def _request(self, method, path, params=None, data=None, headers=None):
        url = self._get_url(path)
        self._logger.info('requesting url {}'.format(url))
        r = requests.request(method, url, params=params, json=data, headers=headers)
        if r.status_code != 200:
            error = 'request {} failed with status code {} and content {}'.format(url, r.status_code, r.content)
            self._logger.error(error)
            raise Exception(error)
        return r.json()

    def _get_url(self, path):
        if self._host[-1] != '/':
            self._host += '/'
        return '{}{}'.format(self._host, path)
