#!/usr/bin/python3 -u

##############################################################
# scans the new_nodes directory for marker files and starts
# the provisioning of those new nodes
##############################################################
import sys

def read_inventory(inventory_path):
  with open(inventory_path, 'r') as inventory_file:
    try:
      return yaml.safe_load(inventory_file))
    except yaml.YAMLError as exc:
      sys.exit('Could not read inventory file {} as valid yaml, exception: {}',format(inventory_file, exc))

def write_inventory(inventory, inventory_path):
  with open(inventory_path, 'w') as inventory_file:
    yaml.dump(inventory, inventory_file, default_flow_style=False)

import datetime
now = datetime.datetime.now()
print(now)