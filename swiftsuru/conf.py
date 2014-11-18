from os import environ

HOST = "0.0.0.0"
PORT = int(environ.get("PORT", "8888"))

# swift stuff needed to perform operations on it
AUTH_URL = environ.get("SWIFT_AUTH_URL", "http://127.0.0.1:8080/auth/v1")
USER = environ.get("SWIFT_USER", "test:tester")
KEY = environ.get("SWIFT_KEY", "testing")

MONGO_USER = environ.get("MONGO_USER", "")
MONGO_PASSWORD = environ.get("MONGO_PASSWORD", "")
MONGO_HOST = environ.get("MONGO_HOST", "localhost:27017")
MONGO_DATABASE = environ.get("MONGO_DATABASE", "swiftsuru")
