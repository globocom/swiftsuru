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
        self._db = self.set_database()

    def set_connection(self):
        return pymongo.MongoClient(conf.MONGODB_ENDPOINT)

    def set_database(self):
        conn = self.set_connection()
        return conn[conf.MONGODB_DATABASE]

    def list_plans(self):
        plans = self._db.plans.find().sort("name", pymongo.ASCENDING)
        return [plan for plan in plans]

    def get_plan(self, name):
        return self._db.plans.find_one({"name": name})

    def add_plan(self, name, tenant, desc):
        return self._db.plans.insert({"name": name,
                                      "tenant": tenant,
                                      "description": desc})

    def remove_plan(self, name):
        self._db.plans.remove({"name": name})

    def list_instances(self):
        instances = self._db.instances.find().sort("name", pymongo.ASCENDING)
        return [instance for instance in instances]

    def get_instance(self, name):
        return self._db.instances.find_one({"name": name})

    def get_instances_by_plan(self, plan):
        instances = self._db.instances.find({"plan": plan}).sort("name", pymongo.ASCENDING)
        return [instance for instance in instances]

    def add_instance(self, name, team, container, plan, user, password):
        return self._db.instances.insert({"name": name,
                                          "team": team,
                                          "container": container,
                                          "plan": plan,
                                          "user": user,
                                          "password": password})

    def remove_instance(self, name):
        """
        We're setting the field/flag "deleted" and won't remove the instance yet
        """
        self._db.instances.update({"name": name}, {"$set": {"deleted": True}})
