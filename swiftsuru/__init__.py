import logging

from flask import Flask

from swiftsuru import conf, api


app = Flask(__name__)

app.debug = True
app.register_blueprint(api.api)

app.logger.addHandler(conf.LOG_HANDLER)
