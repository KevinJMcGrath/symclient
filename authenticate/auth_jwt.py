import jsonpickle
import jwt
import requests

from datetime import datetime, timedelta
from pathlib import Path

import endpoints


def generate_jwt(bot_username: str, private_key_path: str, use_legacy_crypto: bool = False):
    # GAE does not allow installation of the cryptography module
    # Thus, I need to provide a way to fall back to the legacy modules
    # required by pyJWT
    if use_legacy_crypto:
        from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
        jwt.unregister_algorithm('RS512')
        jwt.register_algorithm('RS512', RSAAlgorithm(RSAAlgorithm.SHA512))

    header = {
        "typ": "JWT",
        "alg": "RS512"
    }

    # Make sure you're using datetime.utcnow() and not datetime.now()
    payload = {
        "sub": bot_username,
        "exp": datetime.utcnow() + timedelta(minutes=5)
    }

    with open(Path(private_key_path), 'r') as keyfile:
        private_key = keyfile.read()

        return jwt.encode(payload, private_key, algorithm='RS512', headers=header)


def get_auth_token(endpoint, jwt_token):
    # This needs to be a string, or requests will use the wrong content type
    response = requests.post(endpoint, data=jsonpickle.encode(jwt_token, unpicklable=False))

    if response.status_code == 200:
        resp_json = response.json()
        return resp_json['token']

    response.raise_for_status()


def authenticate_bot(base_url: str, bot_username: str, private_key_path: str, use_legacy_crypto: bool = False):

    jwt_token = generate_jwt(bot_username, private_key_path, use_legacy_crypto)

    jwt_payload = {
        "token": jwt_token.decode('utf-8')
    }

    session_ep = base_url + endpoints.session_auth_jwt()
    km_ep = base_url + endpoints.km_auth_jwt()

    session_token = get_auth_token(session_ep, jwt_payload)
    km_token = get_auth_token(km_ep, jwt_payload)
    expires = datetime.now() + timedelta(days=7)

    return session_token, km_token, expires
