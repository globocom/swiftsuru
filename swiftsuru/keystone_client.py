# -*- coding:utf-8 -*-
import re

from swiftsuru import conf
# import logging

# Mapping of V3 Catalog Endpoint_type to V2 Catalog Interfaces
# ENDPOINT_TYPE_TO_INTERFACE = {
#     'public': 'publicURL',
#     'internal': 'internalURL',
#     'admin': 'adminURL',
# }

if conf.KEYSTONE_VERSION == 3:
    from keystoneclient.v3 import client
else:
    from keystoneclient.v2_0 import client


# log = logging.getLogger(__name__)


class KeystoneClient(object):
    """ return an authenticated keystone client """

    def __init__(self, tenant):
        self.tenant = tenant
        self.conn = self._keystone_conn()

    def _keystone_conn(self):
        endpoint = getattr(conf, 'KEYSTONE_URL')
        insecure = getattr(conf, 'KEYSTONE_SSL_NO_VERIFY', False)

        conn = client.Client(username=conf.KEYSTONE_USER,
                             password=conf.KEYSTONE_PASSWORD,
                             tenant_name=self.tenant,
                             auth_url=endpoint,
                             insecure=insecure,
                             debug=conf.DEBUG)
        return conn

    # def _get_keystone_endpoint(self):
    #     interface = 'internal'

    #     if self.conn.user.is_superuser:
    #         interface = 'admin'

    #     service = self._get_service_from_catalog('identity')

    #     for endpoint in service['endpoints']:

    #         if conf.KEYSTONE_VERSION < 3:
    #             interface = ENDPOINT_TYPE_TO_INTERFACE.get(interface, '')

    #             return endpoint[interface]

    #         else:

    #             if endpoint['interface'] == interface:
    #                 return endpoint['url']

    def _get_service_from_catalog(self, service_type):
        catalog = self.conn.user.service_catalog

        if catalog:
            for service in catalog:
                if service['type'] == service_type:
                    return service

    def create_user(self, name=None, email=None, password=None,
                    project_name=None, enabled=None, domain=None, role_name=None):

        if project_name:
            project = self.project_get(project_name)

        if conf.KEYSTONE_VERSION < 3:
            user = self.conn.users.create(name, password=password, email=email,
                                    tenant_id=project.id, enabled=enabled)
        else:
            user = self.conn.users.create(name, password=password, email=email,
                                  project=project.id, enabled=enabled, domain=domain)

        # Assign role and project to user
        if project and role_name:
            role = self.role_get(role_name)

            # V2 a role '_member_' eh vinculada automaticamente
            if conf.KEYSTONE_VERSION > 2 or role.name != '_member_':
                self.add_user_role(user, project.name, role)

        return user

    def add_user_role(self, user=None, project=None, role=None):
        if conf.KEYSTONE_VERSION < 3:
            return self.conn.roles.add_user_role(user, role, project)
        else:
            return self.conn.roles.grant(role, user=user, project=project)

    def project_get(self, project_name):
        conn = self._project_manager()
        return conn.find(name=project_name)

    def role_get(self, role_name):
        return self.conn.roles.find(name=role_name)

    def _project_manager(self):
        if conf.KEYSTONE_VERSION < 3:
            return self.conn.tenants
        else:
            return self.conn.projects

    # TODO: Ajustar para ser compliance com v3
    # def get_admin_url(self):
    #     url = None
    #     endpoints = self.conn.service_catalog.get_endpoints()
    #     return str(endpoints['object-store'][0]['adminURL'])

    def get_storage_endpoints(self):
        endpoints = self.conn.service_catalog.get_endpoints()
        return endpoints['object-store'][0]
