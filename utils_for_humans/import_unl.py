'''
This script is used to import a UNL produced by:
    https://github.com/jscottbranson/rippled-unl-parser
and convert it so that it can be imported to the "dict_converter.py" script in this directory.
'''

import json

UNL_FILE = "xahau_unl.json"
SERVERS_FILE = "xahau_servers.json"
OUTPUT_FILE = "to_monitor.py"

with open(UNL_FILE, "r") as f:
    unl = json.load(f)
with open(SERVERS_FILE, "r") as f:
    servers = json.load(f)

VALIDATORS = []
for validator in unl['mappings']:
    VALIDATORS.append({'master_key': validator, 'server_name': unl['mappings'][validator]})

SERVERS = []
for server in servers:
    SERVERS.append(server)

with open(OUTPUT_FILE, "w") as f:
    f.write("SERVERS = [\n")
    for server in servers:
        f.write("    " + str(server) + ",\n")
    f.write("]\n\n")
    f.write("VALIDATORS = [\n")
    for validator in VALIDATORS:
        f.write("    " + json.dumps(validator) + ",\n")
    f.write("]")
