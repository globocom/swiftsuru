
import json

from flask import Response, Blueprint, request, jsonify

from keystone_client import KeystoneClient
from swift_client import SwiftClient
from swiftsuru import utils, conf

from dbclient import SwiftsuruDBClient


ACCOUNT_META_ITEM = "X-Account-Meta-App"
ACCOUNT_META_SUBJECT = "X-Account-Meta-Subject"
CONTAINER_TEMPLATE_NAME = "assets"  # should we keep this?

api = Blueprint("swift", __name__)


@api.route("/resources", methods=["POST"])
def add_instance():
    db_cli = SwiftsuruDBClient()

    data = request.form

    plan = data.get("plan", "")
    plan = plan if not isinstance(plan, list) else plan[0]

    if not plan:
        return "You must choose a plan", 500

    db_plan = db_cli.get_plan(plan)
    tenant = db_plan.get("tenant")

    if not tenant:
        return "Invalid plan", 500

    name = data["name"]
    name = name if not isinstance(name, list) else name[0]

    team = data["team"]
    team = team if not isinstance(team, list) else team[0]

    username = "{}_{}".format(team, name)
    password = utils.generate_password()

    keystone = KeystoneClient(tenant=tenant)
    keystone.create_user(name=username,
                         password=password,
                         project_name=tenant,
                         role_name=conf.KEYSTONE_DEFAULT_ROLE,
                         enabled=True)

    container_name = utils.generate_container_name()
    tenant_user = "{}:{}".format(tenant, username)
    headers = {
        "X-Container-Write": "{}".format(tenant_user),
        "X-Container-Read": ".r:*,{}".format(tenant_user)
    }

    client = SwiftClient(keystone)
    client.create_container(container_name, headers)

    db_cli.add_instance(name, team, container_name, plan, username, password)

    return "", 201


@api.route("/resources", methods=["DELETE"])
def remove_instance():
    return "", 200


@api.route("/resources/<instance_name>/bind", methods=["POST"])
def bind(instance_name):
    db_cli = SwiftsuruDBClient()
    instance = db_cli.get_instance(instance_name)
    container = instance.get("container")
    plan = instance.get("plan")

    db_plan = db_cli.get_plan(plan)
    tenant = db_plan.get("tenant")

    keystone = KeystoneClient(tenant=tenant)
    endpoints = keystone.get_storage_endpoints()

    url_template = '{}/{}'

    response = {
        "SWIFT_ADMIN_URL": url_template.format(endpoints["adminURL"], container),
        "SWIFT_PUBLIC_URL": url_template.format(endpoints["publicURL"], container),
        "SWIFT_INTERNAL_URL": url_template.format(endpoints["internalURL"], container),
        "SWIFT_AUTH_URL": getattr(conf, 'KEYSTONE_URL'),
        "SWIFT_USER": instance.get("user"),
        "SWIFT_PASSWORD": instance.get("password")
    }

    return jsonify(response), 201


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
