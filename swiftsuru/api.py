"""
Definition of routes and implementation of an API which provides:
- access to Swift through a service-interface plugable to Tsuru,
- according to specifications at:

http://docs.tsuru.io/en/0.5.3/services/api.html
http://docs.tsuru.io/en/0.5.3/services/build.html
"""
import json
import socket

from flask import Response, Blueprint, request, jsonify

from swiftsuru import utils, conf
from swiftsuru.keystone_client import KeystoneClient
from swiftsuru.swift_client import SwiftClient
from swiftsuru.dbclient import SwiftsuruDBClient

logger = utils.get_logger(__name__)
api = Blueprint("swift", __name__)


@api.route("/resources", methods=["POST"])
def add_instance():
    """
    Creates a service instance on Tsuru.

    - Creates a new User on Keystone
    - Creates a new Container on the Tenant chose by the plan
    - Grant r/w permission for the new user on this new container
    - Saves on MongoDB the Service Intances infos
    """
    try:
        db_cli = SwiftsuruDBClient()
    except Exception, err:
        err_msg = "Fail to connect to MongoDB: {}".format(err)
        logger.error(err_msg)

        return "Internal error: Failed to create instance", 500

    data = request.form

    plan = data.get("plan", "")
    plan = plan if not isinstance(plan, list) else plan[0]

    try:
        db_plan = db_cli.get_plan(plan)
        tenant = db_plan.get("tenant")
    except AttributeError:
        return "You must choose a valid plan", 500

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
        err_msg = 'Fail to create user on Keystone: {}'.format(err)
        logger.error(err_msg)

        return "Internal error: Failed to create instance", 500

    container_name = utils.generate_container_name()
    tenant_user = "{}:{}".format(tenant, username)
    headers = {
        "X-Container-Write": "{}".format(tenant_user),
        "X-Container-Read": ".r:*,{}".format(tenant_user)
    }

    try:
        client = SwiftClient(keystone)
        client.create_container(container_name, headers)
        # Container created to allow the use of undelete middleware
        client.create_container('.trash-{}'.format(container_name), headers)
    except Exception, err:
        # TODO: remove user created on Keystone
        err_msg = 'Fail to create container on Swift: {}'.format(err)
        logger.error(err_msg)

        return "Internal error: Failed to create instance", 500

    try:
        db_cli.add_instance(name, team, container_name,
                            plan, username, password)
    except Exception, err:
        # TODO: remove user created on Keystone
        # TODO: remove container created on Swift
        err_msg = 'Fail to add instance on MongoDB: {}'.format(err)
        logger.error(err_msg)

        return "Internal error: Failed to create instance", 500

    logger.info('service-add: Returning response status code <201>')
    return "", 201


@api.route("/resources/<instance_name>", methods=["DELETE"])
def remove_instance(instance_name):
    """
    Remove a Swift Service Instance from Tsuru.
    """
    try:
        db_cli = SwiftsuruDBClient()
    except Exception, err:
        err_msg = "Fail to connect to MongoDB: {}".format(err)
        logger.error(err_msg)

        return "Internal error: Failed to remove instance", 500

    db_cli.remove_instance(name=instance_name)
    return "", 200


def _bind(instance_name, app_host=None):

    ip = socket.gethostbyname(socket.gethostname())
    logger.info('Starting bind to instance <{}> at unit {}'.format(instance_name, ip))

    db_cli = SwiftsuruDBClient()
    instance = db_cli.get_instance(instance_name)

    if not instance:
        logger.info('Instance <{}> not found on MongoDB'.format(instance_name))
        return "Instance not found", 500

    container = instance.get("container")
    plan = instance.get("plan")

    db_plan = db_cli.get_plan(plan)
    tenant = db_plan.get("tenant")

    log_msg = 'Instance found: container={}, plan={}, tenant={}'
    logger.info(log_msg.format(container, plan, tenant))

    keystone = KeystoneClient(tenant=tenant)
    endpoints = keystone.get_storage_endpoints()

    if app_host:
        try:
            cors_url = utils.format_cors_url(app_host)

            client = SwiftClient(keystone)
            client.set_cors(container, cors_url)

            log_msg = 'CORS set on <{}> to <{}>'
            logger.debug(log_msg.format(container, app_host))
        except Exception, err:
            # TODO: remove user created on Keystone
            err_msg = 'Fail to set CORS to container on Swift: {}'.format(err)
            logger.error(err_msg)

            return "Internal error: Failed to bind instance", 500

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

    logger.info('Bind to <{}> finished'.format(instance_name))

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

    logger.info('bind-app: Returning response status code <{}>'.format(status_code))
    return response, status_code


@api.route("/resources/<instance_name>/bind", methods=["POST"])
def bind_unit(instance_name):
    """
    Binds a Tsuru unit to Swift, also adds a permit access on the used ACL.
    """
    response, status_code = _bind(instance_name)

    if conf.ENABLE_ACLAPI:
        unit_host = request.form.get("unit-host")

        logger.info('Starting ACL API for unit host <{}>'.format(unit_host))

        utils.permit_keystone_access(unit_host)
        utils.permit_swift_access(unit_host)
        utils.aclapi_cli().commit()

        logger.info('Finished ACL API for unit host <{}>'.format(unit_host))

    logger.info('bind-unit: Returning response status code <{}>'.format(status_code))
    return response, status_code


def _unbind(instance_name, app_host):
    """
    Removes app-host from the container CORS headers
    """
    ip = socket.gethostbyname(socket.gethostname())

    logger.info('Starting unbind to instance <{}> at unit {}'.format(instance_name, ip))

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
        cors_url = utils.format_cors_url(app_host)

        client = SwiftClient(keystone)
        client.unset_cors(container, cors_url)
    except Exception, err:
        # TODO: remove user created on Keystone
        err_msg = 'Fail to set CORS to container on Swift: {}'.format(err)
        logger.error(err_msg)

        return "Internal error: Failed to unbind app", 500

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

#@api.route("/resources/projects/users/plans")
def list_projects_users_and_plans():
    """
    List projects, users and plans and fix permissions 
    """
    db_cli = SwiftsuruDBClient()

    for instance in db_cli.list_instances_for_fix_permissions():
        instance = db_cli.get_instance(instance.get("name"))

        if not instance:
            logger.info('Instance <{}> not found on MongoDB'.format(instance))
            return "Instance not found", 500

        container = instance.get("container")
        user = instance.get("user")
        plan = instance.get("plan")
        db_plan = db_cli.get_plan(plan)
        tenant = db_plan.get("tenant")

        log_msg = 'Instance found: container={}, user={}, tenant={}'
        logger.info(log_msg.format(container, plan, tenant))

        keystone = KeystoneClient(tenant=tenant)
        endpoints = keystone.get_storage_endpoints()

    try:
        client_swift = SwiftClient(keystone)
        
        headers = {'X-Container-Read': + tenant +":" + user, 'X-Container-Write': tenant +":" + user }
        client_swift.create_container(self, ".trash-" + container, headers)
        
        logger.info("Sucess to fix permissions: " + to_str(headers) + " to container " + container)        
    except Exception, err:
        err_msg = 'Fail to set permission to container .trash on Swift: {}'.format(err)
        logger.error(err_msg)

        return "Internal error: Failed to fix permissions: " + to_str(headers) + "to container " + container, 500


    logger.info('Fix permission Only Sucess')

    content = 'Fix Permissions! Status: OK'

    return content, 200
