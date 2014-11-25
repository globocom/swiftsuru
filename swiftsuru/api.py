
import json

from flask import Response, Blueprint, request

from swift_client import SwiftClient
from dbclient import SwiftsuruDBClient


ACCOUNT_META_ITEM = "X-Account-Meta-App"
ACCOUNT_META_SUBJECT = "X-Account-Meta-Subject"
CONTAINER_TEMPLATE_NAME = "assets"  # should we keep this?

api = Blueprint("swift", __name__)


@api.route("/resources", methods=["POST"])
def add_instance():
    return "", 201


@api.route("/resources", methods=["DELETE"])
def remove_instance():
    return "", 200


@api.route("/resources/<instance_name>/bind", methods=["POST"])
def bind(instance_name):
    app_host = request.form.get("app-host")
    app_name = app_host.split(".")[0]

    client = SwiftClient()
    client.create_container(CONTAINER_TEMPLATE_NAME, headers={"X-Container-Read": ".r:*"})
    return "", 201


@api.route("/resources/<instance_name>/bind", methods=["DELETE"])
def unbind(instance_name):
    return "", 200


@api.route("/healthcheck")
def healthcheck():
    return "WORKING", 200


@api.route("/resources/plans")
def list_plans():
    db_cli = SwiftsuruDBClient()
    plans = {}

    for plan in db_cli.list_plans():
        name = plan.get('name')
        plans[name] = plan.get("description", name)

    content = Response(json.dumps(plans), mimetype='application/json')
    return content, 200
