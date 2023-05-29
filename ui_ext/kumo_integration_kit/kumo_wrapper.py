import requests

from utilities.logger import ThreadLogger
from utilities.rest import RestConnection
from xui.kumo_integration_kit import utils
# from xui.kumo_integration_kit.constants import KUMO_WEB_HOST, KUMO_API_KEY

logger = ThreadLogger(__name__)

class KumoConnector(RestConnection):

    def __init__(self):
        super().__init__(None, None)
        self.base_url, self.pwd = utils.get_credentials_from_db()

    def __enter__(self):
        self.headers = {
            'Authorization': f'Bearer {self.pwd}',
            'Accept': "application/json",
            'web-host': self.base_url
        }
        return super().__enter__()

    def __getattr__(self, item):
        if item == 'get':
            return lambda path, params=None, **kwargs: self.get_handler(
                path, params, **kwargs)
        elif item == 'post':
            return lambda path, json, **kwargs: self.post_handler(
                path, json, **kwargs)

    def post_handler(self, path, json, **kwargs):
        headers = kwargs.get("headers", None)
        if headers:
            self.headers.update(headers)
        url = f'{self.base_url}{path}'
        return requests.post(url, headers=self.headers, json=json, **kwargs)

    def get_handler(self, path, params, **kwargs):
        headers = kwargs.get("headers", None)
        if headers:
            self.headers.update(headers)
        logger.info(self.headers)
        url = f'{self.base_url}{path}'
        return requests.get(url, headers=self.headers, params=params, **kwargs)
