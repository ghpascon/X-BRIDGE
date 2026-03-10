from smartx_rfid.license import LicenseManager
from app.core import LICENSE_PATH
import logging

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA00QgDyPjuscTBoWBnS1p
GReG6ysiK8eEel0BRGp4gv825GJf4LQkhdKXU78f+dh9cxIYKOlHOa2xXyTCHX2s
RbYIqaDxyop3tVoH+hZcB7oxijiyxhEYrm5Ev5Mh54nALAaP6FZJl+YHiX5OOgTu
5enor/YiYXnftzybd2S8Z6wGCDEmyRjZm03+OD3kJhuEC3l8vS6Iq0rl57CC0Jw8
2qrLJeWr6WFdQUJ6BnXjg4foA6wXdteNDU8ARh/whbd6ie3qHZzhcCncgNZqok4O
jjjIWQzhSOtKxg3DywiKAT0LIh9QReMIzLxcoSqi2LMgLbJANcrexsiJUeHEYx/l
oQIDAQAB
-----END PUBLIC KEY-----"""

# Load license string
try:
	with open(LICENSE_PATH, 'r') as f:
		LICENCE_STR = f.read()
except Exception as e:
	logging.error(f'Error loading license string: {e}')
	LICENCE_STR = None

# Initialize License Manager
license_manager = LicenseManager(
	public_key_pem=PUBLIC_KEY,
)
try:
	license_manager.load_license(LICENCE_STR)
	logging.info(f'License data: {license_manager.license_data}')
except Exception as e:
	logging.error(f'Error loading license: {e}')
