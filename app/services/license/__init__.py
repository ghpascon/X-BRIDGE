from smartx_rfid.license import LicenseManager
from app.core import LICENSE_PATH
import logging

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArkDC8p171iYvIgrzXcHP
MznSFxdR8UwY0n6nq5cktAsesFoBMcGiE9uboUAXQ6/jvwm0AC5YFNBab3zLXeXE
In/DCnrDXSpkFJXWDpC/Dh4FM2zsLRcWgFUt4ZzTwyVFntM5q/Ah07GJ5V/dpntX
WmhuL9Y/b2SFzPToWbbCLXORkU5YzO5GY0Ddlmf7Dd9KuSt4TVNZmGeI8rAEYUND
b+uS4uYyYELE0lQ3T/WabP2KFlazF/J0fvtRouYy5BRt1kUAoeF52MtG0Vp7LBKW
S/7TE5ELzcXAHR5bJ5asqzpiYjacSpHcTPElZoMhpWhk61GrEyXIEqyE8PwourcA
2wIDAQAB
-----END PUBLIC KEY-----
"""

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
