import json
from flask import Response, Blueprint, request

from keystone_client import KeystoneClient
from swift_client import SwiftClient
from swiftsuru import utils, conf

ACCOUNT_META_ITEM = "X-Account-Meta-App"
ACCOUNT_META_SUBJECT = "X-Account-Meta-Subject"
CONTAINER_TEMPLATE_NAME = "assets"  # should we keep this?

api = Blueprint("swift", __name__)


@api.route("/resources", methods=["POST"])
def add_instance():
    data = request.form

    plan = data.get("plan", "")
    plan = plan if not isinstance(plan, list) else plan[0]

    if not plan:
        return "You must choose a plan", 500

    name = data["name"]
    name = name if not isinstance(name, list) else name[0]

    team = data["team"]
    team = team if not isinstance(team, list) else team[0]

    username = "{}_{}".format(team, name)
    password = utils.generate_password()

    keystone = KeystoneClient(tenant=plan)
    keystone.create_user(name=username,
                         password=password,
                         project_name=plan,
                         role_name=conf.KEYSTONE_DEFAULT_ROLE,
                         enabled=True)

    container_name = utils.generate_container_name()
    headers = {"X-Container-Write": "{}:{}".format(plan, username)}

    client = SwiftClient(keystone)
    client.create_container(container_name, headers)

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
    plan_list = utils.create_tsuru_plans_list()
    content = Response(json.dumps(plan_list), mimetype='application/json')
    return content, 200
