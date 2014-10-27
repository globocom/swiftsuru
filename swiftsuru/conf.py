from os import environ

# swift stuff needed to perform operations on it
AUTH_URL=environ.get("SWIFT_AUTH_URL", "http://127.0.0.1:8080/auth/v1")
USER=environ.get("SWIFT_USER", "test:tester")
KEY=environ.get("SWIFT_KEY", "testing")
