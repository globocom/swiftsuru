from flask import Flask
import api

app = Flask(__name__)
app.debug = True
app.register_blueprint(api.api)
