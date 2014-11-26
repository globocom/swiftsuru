from os import environ

# Swiftsuru settings
DEBUG = True

# Tsuru settings for running wsig
HOST = "0.0.0.0"
PORT = int(environ.get("PORT", "8888"))

# swift stuff needed to perform operations on it
AUTH_URL = environ.get("SWIFT_AUTH_URL", "http://127.0.0.1:8080/auth/v1")
USER = environ.get("SWIFT_USER", "test:tester")
KEY = environ.get("SWIFT_KEY", "testing")

# mongo settings
MONGODB_ENDPOINT = environ.get("MONGODB_ENDPOINT", "localhost:27017")
MONGODB_DATABASE = environ.get("MONGODB_DATABASE", "swiftsuru")

# keystone settings
KEYSTONE_URL = environ.get("KEYSTONE_URL", "https://auth.s3.dev.globoi.com:5000/v2.0")
KEYSTONE_USER = environ.get("KEYSTONE_USER", "storm")
KEYSTONE_VERSION = 2
KEYSTONE_PASSWORD = environ.get("KEYSTONE_PASSWORD", "storm")
KEYSTONE_DEFAULT_ROLE = "_member_"
KEYSTONE_SSL_NO_VERIFY = environ.get("KEYSTONE_SSL_NO_VERIFY", True)
