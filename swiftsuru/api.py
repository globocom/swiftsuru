from flask import Flask, Blueprint, request
from swift_client import SwiftClient


ACCOUNT_META_ITEM = "X-Account-Meta-App"
ACCOUNT_META_SUBJECT = "X-Account-Meta-Subject"

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
    client.create_account({ACCOUNT_META_ITEM: app_name, ACCOUNT_META_SUBJECT: "team-name-here"}) # get_team(app_name)
    return "", 201

@api.route("/resources/<instance_name>/bind", methods=["DELETE"])
def unbind(instance_name):
    return "", 200
