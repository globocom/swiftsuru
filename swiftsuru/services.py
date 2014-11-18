"""
Swiftsuru related services to Tsuru
"""
import pymongo

from swiftsuru import conf

def create_tsuru_plans_list():

    mongo_cli = pymongo.MongoClient(conf.MONGODB_ENDPOINT)
    mongo_db = mongo_cli[conf.MONGODB_DATABASE]

    collection = mongo_db['plans']
    plans = collection.find().sort('name', pymongo.ASCENDING)

    result = {}

    for plan in plans:
        name = plan.get('name')
        result[name] = plan.get('description', name)

    return result
