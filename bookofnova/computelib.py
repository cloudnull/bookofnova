# ==============================================================================
# Copyright [2013] [Kevin Carter]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import json
import os
import traceback
import tempfile

# Local Imports
from bookofnova import connections, authentication, logger


class MissingValues(Exception):
    pass


class NovaCommands(object):
    def __init__(self, m_args, log_file=None, log_level='info', output=None):
        """
        Arguments passed through the system are looked at in a dictionary format
        Here is an example argument set needed for operation :
        m_args = {
          "os_user": None,
          "os_apikey": None,
          "os_auth_url": None,
          "os_rax_auth": None,
          "os_verbose": None,
          "os_password": None,
          "os_tenant": None,
          "os_region": None,
          "os_version": 'v2.0'}

        This supports both Private and Public Clouds, not all functions will be
        available. Functions available are dependant on your service catalog,
        provider and version of OpenStack.

        By Default the system will attempt to use the python standard logging
        module. The default behaviour is to log everything to stdout. If you
        provide a "log_file" the system will log to the file provided, if the
        file does not exist the system will attempt to create it. The default
        log level is "info" which can be overridden. If "output" is used the
        system will ignore the log level and simply use what is provided, which
        should be some form of logging system. This is useful when using your
        own logging methods.
        """
        self.m_args = m_args
        self.output = logger.load_in(log_file=log_file,
                                     log_level=log_level,
                                     output=output)
        if 'os_rax_auth' in self.m_args:
            if self.m_args['os_rax_auth']:
                self.m_args['os_rax_auth'] = self.m_args['os_rax_auth'].upper()
        self.connection = connections.Connections(m_args=m_args,
                                                  output=self.output)

    def auth(self):
        """
        Authenticate Against the NOVA API
        """
        self.output.info('Authenticating')
        auth = authentication.Authentication(m_args=self.m_args,
                                             output=self.output)
        data = auth.os_auth()
        self.m_args['token'] = data['token']
        return data

    def re_authenticate(self):
        """
        Updates the users token
        """
        self.output.info('Re-Authenticating')
        self.auth()

    def key_pair(self, key_name=None, key_path=tempfile.gettempdir()):
        """
        Build a Nova Key pair to use on boot for an instance.
        """
        self.output.info('Creating a Key File')
        path = '/os-keypairs'
        key_loc = '%s%s%s' % (key_path, os.sep, key_name)
        b_d = {"keypair": {"name": key_name}}
        pay_load = json.dumps(b_d)
        action = self.connection._post_action(path=path,
                                              args=self.m_args,
                                              body=pay_load)
        key_data = action['nova_resp']
        try:
            if 'keypair' in key_data:
                self.output.info('Key file has been Placed in "%s"' % key_loc)
                with open(key_loc, 'w+') as key_f:
                    key_f.write(key_data['keypair']['private_key'])
                    os.chmod(key_loc, 0400)
            return self.m_args
        except Exception:
            self.output.error(traceback.format_exc())
            self.m_args['nova_status'] = False
            return self.m_args
        return self.m_args

    def key_pair_destroy(self, key_name, key_loc=None):
        """
        Delete a Key Pair if you had set one. If you provide "key_loc" the
        Method will attempt to delete the file as found on your system. This is
        an Optional Argument. To use this method YOU will NEED to provide the
        name of the key that you would like to Delete, as represented by
        "key_name".
        """
        self.output.info('Destroying our Key File')
        path = '/os-keypairs/%s' % key_name
        action = self.connection._delete_action(path=path, args=self.m_args)
        self.m_args = action
        if key_loc:
            if os.path.isfile(key_loc):
                os.remove(key_loc)
        return self.m_args

    def key_pair_list(self):
        """
        List available Key Pairs
        """
        self.output.info('Providing a Key Pair List')
        path = '/os-keypairs'
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def list_quantum_networks(self):
        """
        List any network that we may have access to via Quantum
        """
        self.output.info('Checking to see if the network you specified Exists')
        path = '/os-networksv2'
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def builder(self, pay_load):
        """
        This method requires a "pay_load" which is a dictionary that has our
        servers build values in it. To build the instance you will NEED :

        "name", "imageRef", "flavorRef"

        However there are a lot of options that you can choose from. Here is
        an Example Payload :
        pay_load = {"name": "lynux for workgroups",
                    "imageRef": "12345678-abcd-0987-efgh-1234567890ab",
                    "flavorRef": "311",
                    "network_uuid": [uuid, uuid],
                    "rax_pub": True,
                    "rax_pri": True,
                    "inj_file": [{dst: src}, {dst: src}],
                    "key_name": "lynux",
                    "manual_disk": True,
                    "meta": [{key: value}, {key: value}]}

        Additional Options :

        "network_uuid" allows for Quantum Networking, IE RAX Public Cloud.
        You can specify the network you want to use. THe system will check
        the Netowrk for existance and then add it to the build. This is a
        standard list of UUIDs that you want to use for the networks.

        "rax_pub" and "rax_pri" are bolean values that allow for an instance to
        have public and private networking in the rackspace Public cloud. Bolean
        is a "True" or "False" Value. 

        "inj_file" allows for a file to be base64 encoded and injected on boot.
        this is a destination_on_new_instances=source_location variable.

        "key_name" allows for a SSH key to be injected on boot, This is an
        OPENSTACK only feature, IE NOT RAX Public Cloud.

        "manual_disk" is a bolean value to enable or disable the use of Managed
        disks for an Instance.

        "meta" is a used for metadata on an instance. To set metadata you will
        need to create a list of dictionaries where the "key" is the metadata
        key and the "value" is the metadata value.
        """
        self.output.debug('Building Boot Configuration, pay load == %s'
                          % pay_load)
        if not 'name' in pay_load:
            raise MissingValues('No Name given when attempting to boot')
        elif not 'imageRef' in pay_load:
            raise MissingValues('No Image Refernce given when attempting'
                                ' to boot')
        elif not 'flavorRef' in pay_load:
            raise MissingValues('No Flavor Reference given when attempting'
                                ' to boot')
        body = {"server": {"name": pay_load['name'],
                           "imageRef": pay_load['imageRef'],
                           "flavorRef": pay_load['flavorRef']}}

        # if a Rackspace Cloud Server add the default Networks
        if ('rackspace_auth' in self.m_args and
            self.m_args['rackspace_auth']):
            rax_pri = '11111111-1111-1111-1111-111111111111'
            prinet = {'uuid': rax_pri}
            rax_pub = '00000000-0000-0000-0000-000000000000'
            pubnet = {'uuid': rax_pub}

            networks = body['server']['networks'] = []
            # Allows the user to opt-out of a network
            if 'rax_pub' in pay_load or 'rax_pri' in pay_load:
                if pay_load['rax_pub']:
                    networks.append(pubnet)
                if pay_load['rax_pri']:
                    networks.append(prinet)
            else:
                for net in prinet, pubnet:
                    networks.append(net)

        # If quantum is used, and specified, use it.
        if 'network_uuid' in pay_load:
            if pay_load['network_uuid']:
                quantum_networks = self.list_quantum_networks()['nova_resp']
                if quantum_networks:
                    if not networks:
                        networks = body['server']['networks'] = []
                    for net in quantum_networks['networks']:
                        for net_uuid in pay_load['network_uuid']:
                            if net == net_uuid:
                                networks.append({'uuid': net})

        # Inject Files, This is generally limited to 5 injected files.
        if 'inj_file' in pay_load:
            if pay_load['inj_file']:
                personality = body['server']['personality'] = []
                for i_f in pay_load['inj_file']:
                    dst, src = i_f.split('=', 1)
                    loc_src = os.path.realpath(src)
                    if os.path.isfile(loc_src):
                        try:
                            with open(loc_src) as enc_src:
                                e_s = enc_src.read()
                            _encode = e_s.encode('base64')
                            inj_construct = {'path': dst.encode('utf-8'),
                                             'contents': _encode}
                            personality.append(inj_construct)
                        except Exception:
                            self.output.critical(traceback.format_exc())

        # Use an SSH key on boot for an instance
        if 'key_name' in pay_load:
            if pay_load['key_name']:
                keys = self.key_pair_list()['nova_resp']
                for key in keys['keypairs']:
                    if pay_load['key_name'] == key['keypair']['name']:
                        os_key = {"key_name": pay_load['key_name']}
                        body['server'].update(os_key)

        # Use meta data if specified
        if 'meta' in pay_load:
            if pay_load['meta']:
                meta_dict = {}
                for m_f in pay_load['meta']:
                    key, value = m_f.split('=', 1)
                    meta_dict.update({key: value})
                body['server']['metadata'] = meta_dict

        # Set a Manual Disk if specified
        if 'manual_disk' in pay_load:
            if pay_load['manual_disk']:
                os_manaul_disk = {'diskConfig': 'MANUAL'}
                body['server'].update(os_manaul_disk)

        build_body = json.dumps(body)
        if self.m_args['os_verbose']:
            self.output.debug('BUILD JSON DUMP\t:%s' % build_body)
        return build_body

    def booter(self, payload):
        """
        This method requires that you provide it a "name" for the server.
        """
        path = '/servers'
        action = self.connection._post_action(path=path,
                                              args=self.m_args,
                                              body=payload)
        self.m_args = action
        return self.m_args

    def confirm_revert_resize(self, server_id, confirm=True):
        """
        You can Confirm a resize of a server using this method. The method
        Confirms or reverts a resize action. By Default the method will confirm
        a resize for a server in a confirm Resize state.  However if you need to
        revert the resize action simply change "confirm" to "False" which will
        for the instance to be reverted.

        In order to confirm or revert a resize you will need to have the
        "server_id".
        """
        self.output.info('Performing confirmation on resize for %s,'
                         ' Confirm == %s' % (server_id, confirm))
        if confirm:
            payload = {"confirmResize": None}
        else:
            payload = {"revertResize": None}

        pay_load = json.dumps(payload)
        path = '/servers/%s/action' % server_id
        action = self.connection._post_action(path=path,
                                              args=self.m_args,
                                              body=pay_load)
        self.m_args = action
        return self.m_args

    def re_sizer(self, server_id, flavor):
        """
        You can resize a server using this method. The method allows for an
        instance to be resized with to any available size. Any flavor that you
        pass the instance will be looked up prior to the action being attempted.

        In order to resize a server you will need to have the "server_id" as
        well as the "flavor" size that you want to use.
        """
        self.output.info('Performing a resize on %s, New size == %s'
                         % (server_id, flavor))
        flavors = self.flavor_list()
        for flv in flavors['nova_resp']['flavors']:
            if flv['id'] == flavor:
                flavor_link = flv['id']
        pay_load = json.dumps({"resize": {"flavorRef": flavor_link}})

        path = '/servers/%s/action' % server_id
        action = self.connection._post_action(path=path,
                                              args=self.m_args,
                                              body=pay_load)
        self.m_args = action
        return self.m_args

    def re_booter(self, server_id, hard_reboot=True):
        """
        You can reboot a server using this method. The method allows for an
        instance to be reboot with either a HARD or SOFT reboot. By default
        "hard_reboot" is set to "True" however if you want to perform a soft
        reboot YOU will need to set "hard_reboot" to False.

        This requires that the user, YOU, to provide a server UUID as
        "server_id".
        """
        self.output.info('Performing a reboot on %s, Hard Reboot == %s'
                         % (server_id, hard_reboot))
        if hard_reboot:
            payload = {"reboot": {"type": 'HARD'}}
        else:
            payload = {"reboot": {"type": 'SOFT'}}

        pay_load = json.dumps(payload)
        path = '/servers/%s/action' % server_id
        action = self.connection._post_action(path=path,
                                              args=self.m_args,
                                              body=pay_load)
        self.m_args = action
        return self.m_args

    def server_list(self):
        """
        List out all of the servers that are in the REGION you specified when
        you authenticated.
        """
        self.output.info('Providing a list of Servers')
        path = '/servers'
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def server_list_detail(self):
        """
        List out all of the servers that are in the REGION you specified when
        you authenticated. 
        """
        self.output.info('Providing a Detailed List of Servers')
        path = '/servers/detail'
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def server_info(self, server_id):
        """
        This method will allow you to see detailed information on a specified
        instance.

        This requires that the user, YOU, to provide a server UUID as
        "server_id".
        """
        self.output.info('Providing Server Information on Instance ID %s'
                         % server_id)
        path = '/servers/%s' % server_id
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def image_list(self):
        """
        List out all of the images that you have available to you in the
        Openstack API in detail. Note that this only lists public images, there
        may be images that were made private which will not be shown with
        this command.
        """
        self.output.info('Providing an Image List')
        path = '/images'
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def image_list_detail(self):
        """
        List out all of the images that you have available to you in the
        Openstack API. Note that this only lists public images, there may be
        images that were made private which will not be shown with this command.
        """
        self.output.info('Providing an Image List')
        path = '/images/detail'
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def image_create(self, server_id, img_name, meta_data=None):
        """
        Create an Image of an Instance. Requires Instance UUID and the name of
        the Image you wish to create. Optionally you can add meta data to the
        image as well.
        """
        self.output.info('Creating an Image of Server ID %s => Image Name %s'
                         % (server_id, img_name))
        path = '/servers/%s/action' % server_id
        if meta_data:
            _pl = {"createImage": {"name": img_name, "metadata": meta_data}}
        else:
            _pl = {"createImage": {"name": img_name}}
        pay_load = json.dumps(_pl)
        action = self.connection._post_action(path=path,
                                              args=self.m_args,
                                              body=pay_load)
        self.m_args = action
        return self.m_args

    def image_info(self, image_id):
        """
        This method will allow you to see detailed information on a specified
        image.

        This requires that the user, YOU, to provide a image UUID as
        "image_id".
        """
        self.output.info('Providing Information on image ID %s'
                         % image_id)
        path = '/images/%s' % image_id
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def image_nuker(self, image_id):
        """
        Delete an image.

        This requires that the user, YOU, to provide a server UUID as
        "image_id".
        """
        self.output.info('Destroying Image ID "%s"' % image_id)
        path = '/images/%s' % image_id
        action = self.connection._delete_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def flavor_list_detail(self):
        """
        List out all of the flavors that you have available to you in the
        Openstack API. Note that this only lists public flavors, there may be
        flavors that were made private which will not be shown with this
        command.
        """
        self.output.info('Providing a Detailed Flavor List')
        path = '/flavors/detail'
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def flavor_list(self):
        """
        List out all of the flavors that you have available to you in the
        Openstack API. Note that this only lists public flavors, there may be
        flavors that were made private which will not be shown with this
        command.
        """
        self.output.info('Providing a list of Flavors')
        path = '/flavors'
        action = self.connection._get_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args

    def server_nuker(self, server_id):
        """
        Delete an instance.

        This requires that the user, YOU, to provide a server UUID as
        "server_id".
        """
        self.output.info('Destroying Server ID "%s"' % server_id)
        path = '/servers/%s' % server_id
        action = self.connection._delete_action(path=path, args=self.m_args)
        self.m_args = action
        return self.m_args
