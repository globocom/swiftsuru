import logging
import sys

from os import environ

# Swiftsuru settings
# DEBUG = environ.get("DEBUG", True)
DEBUG = True

# Logging
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
handler.setLevel(LOG_LEVEL)

LOG_HANDLER = handler

# Tsuru settings for running wsig
HOST = "0.0.0.0"
PORT = int(environ.get("PORT", "8888"))

# swift stuff needed to perform operations on it
AUTH_URL = environ.get("SWIFT_AUTH_URL", "http://127.0.0.1:8080/auth/v1")
USER = environ.get("SWIFT_USER", "test:tester")
KEY = environ.get("SWIFT_KEY", "testing")
SWIFT_API = environ.get("SWIFT_API", "http://127.0.0.1:35357")
SWIFT_API_HOST = SWIFT_API.split("://")[1].split(":")[0]
SWIFT_API_PORT = SWIFT_API.split("://")[1].split(":")[1].split("/")[0]

# mongo settings
MONGODB_ENDPOINT = environ.get("MONGODB_ENDPOINT", "127.0.0.1:27017")
MONGODB_DATABASE = environ.get("MONGODB_DATABASE", "swiftsuru")

# keystone settings
KEYSTONE_URL = environ.get("KEYSTONE_URL", "https://127.0.0.1:5000/v2.0")
KEYSTONE_HOST = KEYSTONE_URL.split("://")[1].split(":")[0]
KEYSTONE_PORT = KEYSTONE_URL.split("://")[1].split(":")[1].split("/")[0]
KEYSTONE_USER = environ.get("KEYSTONE_USER", "user")
KEYSTONE_VERSION = 2
KEYSTONE_PASSWORD = environ.get("KEYSTONE_PASSWORD", "password")
KEYSTONE_DEFAULT_ROLE = "_member_"
KEYSTONE_SSL_NO_VERIFY = environ.get("KEYSTONE_SSL_NO_VERIFY", True)

# aclapi settings
ACLAPI_URL = environ.get("ACLAPI_URL", "https://aclapi.com")
ACLAPI_USER = environ.get("ACLAPI_USER", "thatsme")
ACLAPI_PASS = environ.get("ACLAPI_PASS", "verysecurepass")
ENABLE_ACLAPI = environ.get("ENABLE_ACLAPI", True)
