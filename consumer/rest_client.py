import requests
from requests import Session, Response
from credentials import API_DOMAIN

# Simple API client designed to interact with Axon's Partner API
class ApiClient(object):
    def __init__(self, bearer_token_args: dict):
        self.bearer_token_args = bearer_token_args
        self.set_bearer_token(token=self.get_bearer_token(**bearer_token_args))
        print(f"Received authentication credentials from {API_DOMAIN}")

    def set_bearer_token(self, token):
        self.bearer_token = token

    def get_bearer_token(self, **kwargs):
        form_data = {
            "grant_type": "client_credentials",
            "partner_id": kwargs["partner_id"],
            "client_id": kwargs["client_id"],
            "client_secret": kwargs["client_secret"],
        }
        response = requests.post(
            f"https://{API_DOMAIN}/api/oauth2/token", data=form_data
        )
        if response.status_code != 200:
            raise Exception(
                f"Received invalid response code {response.status_code}:\n {response.content}"
            )
        return response.json()["access_token"]

    def retry(self, func, args, kwargs):
        response = func(*args, **kwargs)
        if response.status_code == 401:
            print("Got unauthorized, re-authenticating")
            self.set_bearer_token(token=self.get_bearer_token(**self.bearer_token_args))
            response = func(*args, **kwargs)
            return response
        return response

    def get(self, url, **kwargs) -> Response:
        kwargs["headers"] = {"Authorization": f"Bearer {self.bearer_token}"}
        return self.retry(requests.get, args=[url], kwargs=kwargs)

    def post(self, url, **kwargs) -> Response:
        kwargs["headers"] = {"Authorization": f"Bearer {self.bearer_token}"}
        return self.retry(requests.post, args=[url], kwargs=kwargs)
