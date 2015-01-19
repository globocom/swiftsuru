# Disable HTTPS verification warnings.
from requests.packages import urllib3
urllib3.disable_warnings()

from flask import Flask

from swiftsuru import conf, api, utils


app = Flask(__name__)

app.debug = conf.DEBUG
app.register_blueprint(api.api)

app.logger.addHandler(conf.LOG_HANDLER)
