"""
Swiftsuru related services to Tsuru
"""
import pymongo
import os

from swiftsuru import conf

def create_tsuru_plans_list():

    try:
        mongo_cli = pymongo.MongoClient(conf.MONGODB_ENDPOINT)
    except pymongo.error.ConnectionFailure, err:
        print err
        return {}

    mongo_db = mongo_cli[conf.MONGODB_DATABASE]

    collection = mongo_db['plans']
    plans = collection.find().sort('name', pymongo.ASCENDING)

    result = {}

    for plan in plans:
        name = plan.get('name')
        result[name] = plan.get('description', name)

    return result

def generate_container_name():
    return os.urandom(3).encode('hex')
