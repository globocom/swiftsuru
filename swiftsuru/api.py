"""
Definition of routes and implementation of an API which provides:
- access to Swift through a service-interface plugable to Tsuru,
- according to specifications at:

http://docs.tsuru.io/en/0.5.3/services/api.html
http://docs.tsuru.io/en/0.5.3/services/build.html
"""
import json

from flask import Response, Blueprint, request, jsonify

from swiftsuru import utils, conf
from swiftsuru.keystone_client import KeystoneClient
from swiftsuru.swift_client import SwiftClient
from swiftsuru.dbclient import SwiftsuruDBClient


api = Blueprint("swift", __name__)


@api.route("/resources", methods=["POST"])
def add_instance():
    """
    Creates a service instance on Tsuru.

    - Creates a new User on Keystone
    - Creates a new Container on the Tenant chose by the plan
    - Grant r/w permission for the new user on this new container
    - Saves on MongDB the Service Intances infos
    """
    try:
        db_cli = SwiftsuruDBClient()
    except Exception, err:
        # TODO: logging
        msg = "ERROR: Fail to conect to MongoDB: {}".format(err)
        return "Failed to create instance\n {}".format(msg), 500

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

    try:
        keystone = KeystoneClient(tenant=tenant)
        keystone.create_user(name=username,
                             password=password,
                             project_name=tenant,
                             role_name=conf.KEYSTONE_DEFAULT_ROLE,
                             enabled=True)
    except Exception, err:
        # TODO: logging
        msg = 'ERROR: Fail to create user on Keystone: {}'.format(err)
        return "Failed to create instance\n{}".format(msg), 500

    container_name = utils.generate_container_name()
    tenant_user = "{}:{}".format(tenant, username)
    headers = {
        "X-Container-Write": "{}".format(tenant_user),
        "X-Container-Read": ".r:*,{}".format(tenant_user)
    }

    try:
        client = SwiftClient(keystone)
        client.create_container(container_name, headers)
    except Exception, err:
        # TODO: logging
        # TODO: remove user created on Keystone
        msg = 'ERROR: Fail to create container on Swift: {}'.format(err)
        return "Failed to create instance\n{}".format(msg), 500

    try:
        db_cli.add_instance(name, team, container_name,
                            plan, username, password)
    except Exception, err:
        # TODO: logging
        # TODO: remove user created on Keystone
        # TODO: remove container created on Swift
        print 'ERROR: Fail to add instance on MongoDB: {}'.format(err)
        return "Failed to create instance", 500

    return "", 201


@api.route("/resources/<instance_name>", methods=["DELETE"])
def remove_instance(instance_name):
    """
    Remove a Swift Service Instance from Tsuru.
    """
    try:
        db_cli = SwiftsuruDBClient()
    except Exception, err:
        # TODO: logging
        print "ERROR: Fail to conect to MongoDB: {}".format(err)
        return "Failed to create instance", 500

    db_cli.remove_instance(name=instance_name)
    return "", 200


def _bind(instance_name, app_host=None):
    db_cli = SwiftsuruDBClient()
    instance = db_cli.get_instance(instance_name)

    if not instance:
        return "Instance not found", 500

    container = instance.get("container")
    plan = instance.get("plan")

    db_plan = db_cli.get_plan(plan)
    tenant = db_plan.get("tenant")

    keystone = KeystoneClient(tenant=tenant)
    endpoints = keystone.get_storage_endpoints()

    if app_host:
        try:
            client = SwiftClient(keystone)
            client.set_cors(container, app_host)
        except Exception, err:
            # TODO: logging
            # TODO: remove user created on Keystone
            msg = 'ERROR: Fail to set CORS to container on Swift: {}'.format(err)
            return "Failed to create instance\n{}".format(msg), 500

    response = {
        "SWIFT_ADMIN_URL": '{}/{}'.format(endpoints["adminURL"],
                                          container),
        "SWIFT_PUBLIC_URL": '{}/{}'.format(endpoints["publicURL"],
                                           container),
        "SWIFT_INTERNAL_URL": '{}/{}'.format(endpoints["internalURL"],
                                             container),
        "SWIFT_AUTH_URL": getattr(conf, 'KEYSTONE_URL'),
        "SWIFT_CONTAINER": container,
        "SWIFT_TENANT": tenant,
        "SWIFT_USER": instance.get("user"),
        "SWIFT_PASSWORD": instance.get("password")
    }

    return jsonify(response), 201


@api.route("/resources/<instance_name>/bind-app", methods=["POST"])
def bind_app(instance_name):
    """
    Bind a Tsuru APP on a Swift Service Instance.

    Expose all variables needed for an App to connect with Swift.
    """
    data = request.form

    app_host = data["app-host"]
    app_host = app_host if not isinstance(app_host, list) else app_host[0]

    response, status_code = _bind(instance_name, app_host)

    return response, status_code


@api.route("/resources/<instance_name>/bind", methods=["POST"])
def bind_unit(instance_name):
    """
    Binds a Tsuru unit to Swift, also adds a permit access on the used ACL.
    """
    response, status_code = _bind(instance_name)

    if conf.ENABLE_ACLAPI:
        unit_host = request.form.get("unit-host")
        utils.permit_keystone_access(unit_host)
        utils.permit_swift_access(unit_host)
        utils.aclapi_cli().commit()

    return response, status_code


def _unbind(instance_name, app_host):
    """
    Removes app-host from the container CORS headers
    """
    db_cli = SwiftsuruDBClient()
    instance = db_cli.get_instance(instance_name)

    if not instance:
        return "Instance not found", 404

    container = instance.get("container")
    plan = instance.get("plan")

    db_plan = db_cli.get_plan(plan)
    tenant = db_plan.get("tenant")

    keystone = KeystoneClient(tenant=tenant)

    try:
        client = SwiftClient(keystone)
        client.unset_cors(container, app_host)
    except Exception, err:
        # TODO: logging
        # TODO: remove user created on Keystone
        msg = 'ERROR: Fail to set CORS to container on Swift: {}'.format(err)
        return "Failed to unbind app\n{}".format(msg), 500

    return '', 200


@api.route("/resources/<instance_name>/bind-app", methods=["DELETE"])
def unbind_app(instance_name):
    """
    Unbind a Tsuru APP on a Swift Service Instance.
    """
    data = request.form

    app_host = data["app-host"]
    app_host = app_host if not isinstance(app_host, list) else app_host[0]

    response, status_code = _unbind(instance_name, app_host)
    return response, status_code


@api.route("/resources/<instance_name>/bind", methods=["DELETE"])
def unbind_unit(instance_name):
    """
    Unbind a Tsuru APP unit on a Swift Service Instance.
    """
    return "", 200


@api.route("/healthcheck")
def healthcheck():
    """
    Swift Service API healthcheck.
    """
    return "WORKING", 200


@api.route("/resources/plans")
def list_plans():
    """
    List all plans availables on Swift.
    """
    db_cli = SwiftsuruDBClient()
    plans = []

    for plan in db_cli.list_plans():
        plans.append({
            "name": plan.get("name"),
            "description": plan.get("description")
        })

    content = Response(json.dumps(plans), mimetype="application/json")

    return content, 200
