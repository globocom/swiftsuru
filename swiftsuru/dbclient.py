"""
Database client for Swiftsuru API
"""

import pymongo
from swiftsuru import conf


class SwiftsuruDBClient(object):
    """
    Interface class with the database to manage plans and instances
    """

    def __init__(self):
        cli = pymongo.MongoClient(conf.MONGODB_ENDPOINT)
        self.db = cli[conf.MONGODB_DATABASE]

    def list_plans(self):
        plans = self.db.plans.find().sort("name", pymongo.ASCENDING)
        return [plan for plan in plans]

    def get_plan(self, name):
        return self.db.plans.find_one({"name": name})

    def add_plan(self, name, tenant, desc):
        return self.db.plans.insert({"name": name,
                                     "tenant": tenant,
                                     "description": desc})

    def remove_plan(self, name):
        self.db.plans.remove({"name": name})

    def list_instances(self):
        instances = self.db.instances.find().sort("name", pymongo.ASCENDING)
        return [instance for instance in instances]

    def get_instance(self, name):
        return self.db.instances.find_one({"name": name})

    def get_instances_by_plan(self, plan):
        instances = self.db.instances.find({"plan": plan}).sort("name", pymongo.ASCENDING)
        return [instance for instance in instances]

    def add_instance(self, name, team, container, plan):
        return self.db.instances.insert({"name": name,
                                         "team": team,
                                         "container": container,
                                         "plan": plan})

    def remove_instance(self, name):
        """
        We're setting the field/flag "deleted" and won't remove the instance yet
        """
        self.db.instances.update({"name": name}, {"$set": {"deleted": True}})
