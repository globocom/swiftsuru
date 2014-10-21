from flask import Flask, Blueprint


api = Blueprint("swift", __name__)

@api.route("/resources", methods=["POST"])
def add_instance():
    return "", 201

@api.route("/resources", methods=["DELETE"])
def remove_instance():
    return "", 200

@api.route("/resources/<instance_name>/bind", methods=["POST"])
def bind(instance_name):
    return "", 201

@api.route("/resources/<instance_name>/bind", methods=["DELETE"])
def unbind(instance_name):
    return "", 200
