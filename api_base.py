import jsonpickle

from .sym_session import Session


class APIBase:
    def __init__(self, current_session: Session):
        self.session = current_session

        self.api_base_url = self.session.config['api_host'] + ':' + self.session.config['api_port'] + '/'

    def get_endpoint(self, symphony_endpoint: str):
        return self.api_base_url + symphony_endpoint

    def post(self, endpoint: str, body):
        return self.rest_callout('post', endpoint, body)

    def get(self, endpoint: str):
        return self.rest_callout('get', endpoint)

    def rest_callout(self, method, endpoint, body_object=None):
        self.session.authenticate()

        response = None

        if method.lower() == 'get':
            response = self.session.http_session.get(endpoint, headers=self.session.get_rest_headers())
        elif method.lower() == 'post':
            body_str = jsonpickle.encode(body_object, unpicklable=False)
            response = self.session.http_session.post(endpoint, data=body_str, headers=self.session.get_rest_headers())
        # elif method.lower() == 'postv2':

        if response.status_code // 100 != 2:
            response.raise_for_status()

        return response.text
