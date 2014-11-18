from os import environ

# Tsuru settings for running wsig
HOST = "0.0.0.0"
PORT = int(environ.get("PORT", "8888"))

# swift stuff needed to perform operations on it
AUTH_URL = environ.get("SWIFT_AUTH_URL", "http://127.0.0.1:8080/auth/v1")
USER = environ.get("SWIFT_USER", "test:tester")
KEY = environ.get("SWIFT_KEY", "testing")

# mongo settings
MONGODB_ENDPOINT = environ.get("MONGODB_ENDPOINT", "localhost:27017")
MONGODB_DATABASE = environ.get("MONGO_DATABASE", "swiftsuru")
