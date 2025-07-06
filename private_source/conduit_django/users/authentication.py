import base64      #To encode/decode data to/from Base64 URL-safe strings (used in JWT).

import hashlib  #To provides hashing algorithsm like SHA256 
import hmac
import json
import time 

SECRET_KEY = 'vietanhnek'
ALGORITHM = 'HS256'

def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def base64url_decode(input_str):
    padding = '=' * (4 - len(input_str) % 4)
    return base64.urlsafe_b64decode(input_str + padding)

def encode_jwt(payload, secret=SECRET_KEY):
    header = {'alg': ALGORITHM, 'typ': 'JWT'}
    header_b64 = base64url_encode(json.dumps(header).encode())
    payload_b64 = base64url_encode(json.dumps(payload).encode())

    signature = hmac.new(
        secret.encode(),
        f'{header_b64}.{payload_b64}'.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64url_encode(signature)

    return f'{header_b64}.{payload_b64}.{signature_b64}'

def decode_jwt(token, secret=SECRET_KEY):
    try:
        header_b64, payload_b64, signature_b64 = token.split('.')
        signature_check = hmac.new(
            secret.encode(),
            f'{header_b64}.{payload_b64}'.encode(),
            hashlib.sha256
        ).digest()
        expected_signature = base64url_encode(signature_check)

        if not hmac.compare_digest(expected_signature, signature_b64):
            return None 
        
        payload = json.loads(base64url_decode(payload_b64))
        if payload.get('exp') < time.time():
            return None 
        
        return payload
    except Exception:
        return None 
