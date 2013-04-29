# NOTE: logging goes to standard out by default,
# The Output Varible is not needed unless you want to overide.

from bookofnova import computelib, connections

# Everything in this dictionary is a string, fill in the needed values.
m_args = {"os_user": 'YOU',
          "os_apikey": 'RANDOMNUMBERSANDTHINGS',
          "os_auth_url": None,
          "os_rax_auth": 'ALOCATION',
          "os_verbose": None,
          "os_password": None,
          "os_tenant": None,
          "os_region": None,
          "os_version": 'v2.0'}
# Tell the book of Nova that you are ready
nova = computelib.NovaCommands(m_args=m_args,
                               log_file=None,
                               log_level='info',
                               output=None)

# Authenticate Against the Nova API
nova.auth()

# Using Nova to show a list of all Instances
servers = nova.server_list()
print(servers)

# Using Nova to show a detailed list of all Instances
d_servers = nova.server_list_detail()
print(d_servers)

# Using Nova to show all of the images
images = nova.image_list()
print(images)

# Using Nova to show all of the Flavors
flavors = nova.flavor_list()
print(flavors)

# Using Nova to show all of the available Key Pairs
keys = nova.key_pair_list()
print(keys)

# Using Nova to show all of the Quantum Netowrks you have
nets = nova.list_quantum_networks()
print(nets)

# Building an Instance
pay_load = {"name": "lynux for workgroups",
            "imageRef": "a10eacf7-ac15-4225-b533-5744f1fe47c1",
            "flavorRef": "2",
            "manual_disk": True}
builder = nova.builder(pay_load)
print(builder)

# Now that we have a pay_load lets go build
new_server = nova.booter(builder)
print(new_server)

# And now we destroy what we created, but after a few seconds.
import time
time.sleep(5)

nuked_server = nova.server_nuker(new_server['nova_resp']['server']['id'])
print(nuked_server)
