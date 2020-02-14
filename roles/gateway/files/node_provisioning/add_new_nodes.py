#!/usr/bin/python3 -u

##############################################################
# scans the new_nodes directory for marker files and starts
# the provisioning of those new nodes
##############################################################
import sys
import os
import copy
import re
import yaml
from typing import List
from python_hosts import Hosts, HostsEntry

# ToDo: add type hints to functions, see https://www.python.org/dev/peps/pep-0484/

# sample inventory object:
#{'all': {'children': {'gateway': {'hosts': {'localhost': {'ansible_connection': 'local'}}}, 'homek8s': {'children': {'masters': {'hosts': {'k8s-node-106': None}}, 'new_masters': {'hosts': {'k8s-node-106': None}}, 'nodes': {'hosts': None}, 'new_nodes': {'hosts': None}}, 'vars': {'ansible_user': 'homek8s', 'ansible_ssh_private_key_file': '/homek8s/id_rsa', 'ansible_become': True, 'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no'}}}, 'vars': {'ansible_python_interpreter': '/usr/bin/python3'}}}

def read_inventory(inventory_path):
  with open(inventory_path, 'r') as inventory_file:
    try:
      return yaml.safe_load(inventory_file)
    except yaml.YAMLError as exc:
      sys.exit('Could not read inventory file {} as valid yaml, exception: {}',format(inventory_file, exc))

def write_inventory(inventory, inventory_path):
  with open(inventory_path, 'w') as inventory_file:
    yaml.dump(inventory, inventory_file, default_flow_style=False)

def get_basedir():
  """Return the homek8s base dir on the gateway, default is /homek8s.
  
     This parameter is given as a CLI argument by the systemd service.
  """
  return sys.argv[1]

def get_nodes_for_homek8s_group(inventory, group_name) -> List[str]:
  """Return the nodes' names of the given group from the inventory as a list."""
  hosts_dict = inventory['all']['children']['homek8s']['children'][group_name]['hosts']
  if hosts_dict:
    return list(hosts_dict.keys())
  else:
    return []

def get_current_masters(inventory) -> List[str]:
  """Return the current masters' names (group 'masters') from the inventory as a list."""
  return get_nodes_for_homek8s_group(inventory, 'masters')

def get_new_masters(inventory) -> List[str]:
  """Return the new masters' names (group 'new_masters') from the inventory as a list."""
  return get_nodes_for_homek8s_group(inventory, 'new_masters')

def set_hosts_for_inventory_group(inventory, group, nodes):
  """Set the given list of nodes as hosts for the given group, e.g. 'new_masters' """
  #host entries in the inventory have to be dicts,
  #even when they don't have any values beneath (e.g. "vars:" in ansible inventory)
  group_hosts = { node : None for node in nodes }

  new_inventory = copy.deepcopy(inventory)
  new_inventory['all']['children']['homek8s']['children'][group]['hosts'] = group_hosts
  return new_inventory

def move_hosts_from_inventory_group_to_group(inventory, old_group, new_group):
  """Move the hosts from one inventory group to another, returning the new inventory dict (deep copy).
  
     The dict in the inventory parameter is not manipulated.
  """
  new_inventory = copy.deepcopy(inventory)
  old_group_hosts_dict = new_inventory['all']['children']['homek8s']['children'][old_group]['hosts']

  if new_inventory['all']['children']['homek8s']['children'][new_group]['hosts']:
    #add hosts from old group to new group
    new_inventory['all']['children']['homek8s']['children'][new_group]['hosts'].update(old_group_hosts_dict)
  else:
    #new group was empty, setting hosts dict directly
    new_inventory['all']['children']['homek8s']['children'][new_group]['hosts'] = old_group_hosts_dict

  new_inventory['all']['children']['homek8s']['children'][old_group]['hosts'] = {}
  return new_inventory
  

def get_current_nodes(inventory) -> List[str]:
  """Return the current nodes' names (group 'nodes') from the inventory as a list."""
  return get_nodes_for_homek8s_group(inventory, 'nodes')

def get_new_nodes(inventory) -> List[str]:
  """Return the new nodes' names (group 'new_nodes') from the inventory as a list."""
  return get_nodes_for_homek8s_group(inventory, 'new_nodes')

def gather_new_nodes_from_marker_files(new_node_marker_dir_path):
  """Return the new node names as list as indicated by the new-node marker files.
  
     This function simply returns a list of filenames in the new-node marker directory.
  """
  return os.listdir(new_node_marker_dir_path)

def remove_existing_nodes_from_new_node_list(new_nodes, current_nodes) -> List[str]:
  """Return a list of nodes minus the nodes (and masters) already in the inventory (groups 'nodes' and 'masters')."""
  return [node for node in new_nodes if node not in current_nodes]

def remove_marker_files_for_nodes(nodes, new_node_marker_dir_path):
  """Remove new-node marker files for existing (i.e. already provisioned) nodes."""
  for node in nodes:
    try:
      os.remove(new_node_marker_dir_path + "/" + node)
    except OSError:
      pass

def get_master_count_in_hosts(etc_hosts):
  """Return the number of hosts entries matching k8s-master-X."""
  master_re = re.compile('k8s-master-\d+')
  return len([entry.names for entry in etc_hosts.entries if entry.names and list(filter(master_re.match, entry.names))])

def add_new_masters_to_etc_hosts(new_master_nodes):
  """Modify /etc/hosts entries for master nodes to add master-specific alias (k8s-master-X)."""
  etc_hosts = Hosts('/etc/hosts')
  master_count = get_master_count_in_hosts(etc_hosts)
  new_master_nodes_set = set(new_master_nodes)
  master_re = re.compile('k8s-master-\d+')
  for entry in etc_hosts.entries:
    #check if this hosts entry matches any new master nodes we want to modify
    if entry.names and not set(entry.names).isdisjoint(new_master_nodes_set):
      #check if this hosts entry already has any k8s-master-* names
      if not list(filter(master_re.match, entry.names)):
        master_count += 1
        entry.names.append('k8s-master-' + str(master_count))
      #endif
    #endif
  #endfor
  etc_hosts.write()

def add_new_master(base_dir, cleaned_new_nodes):
  """Add a new master to the homek8s cluster and return
     the list of new nodes WITHOUT the new master (i.e. the new nodes still left to be added as normal nodes).
  
     This includes selecting a new master from the new nodes, adding it to /etc/hosts,
     provisioning it with the homek8s ansible playbook and remove the new-node marker file.
  """
  inventory_path = base_dir + "/hosts.yml"
  inventory = read_inventory(inventory_path)
  new_masters = get_new_masters(inventory)
  if not new_masters:
    #first new_node will become new master
    new_masters = cleaned_new_nodes[0:1]

  inventory = set_hosts_for_inventory_group(inventory, 'new_masters', new_masters)
  write_inventory(inventory, inventory_path)

  #ToDo: provision new master
  
  # add new masters to /etc/hosts (e.g. "192.168.2.100 k8s-node-100 k8s-master-1")
  add_new_masters_to_etc_hosts(new_masters)

  inventory = move_hosts_from_inventory_group_to_group(inventory, 'new_masters', 'masters')
  write_inventory(inventory, inventory_path)

  remove_marker_files_for_nodes(new_masters, base_dir + "/data/new_nodes")

  new_nodes_without_new_masters = [ node for node in cleaned_new_nodes if node not in new_masters]
  return new_nodes_without_new_masters
#enddef

def add_new_nodes(base_dir, new_nodes_from_markers):
  """Add new nodes to the cluster."""
  inventory_path = base_dir + "/hosts.yml"
  inventory = read_inventory(inventory_path)
  new_nodes = get_new_nodes(inventory)
  if new_nodes:
    new_nodes = list(dict.fromkeys(new_nodes + new_nodes_from_markers))
  else:
    new_nodes = new_nodes_from_markers[:]

  inventory = set_hosts_for_inventory_group(inventory, 'new_nodes', new_nodes)
  write_inventory(inventory, inventory_path)

  #ToDo: provision new nodes

  inventory = move_hosts_from_inventory_group_to_group(inventory, 'new_nodes', 'nodes')
  write_inventory(inventory, inventory_path)

  remove_marker_files_for_nodes(new_nodes, base_dir + "/data/new_nodes")
#enddef

if __name__ == "__main__":
  inventory_path = get_basedir() + "/hosts.yml"
  inventory = read_inventory(inventory_path)
  current_masters = get_current_masters(inventory)
  current_nodes = get_current_nodes(inventory)
  new_nodes = gather_new_nodes_from_marker_files(get_basedir() + "/data/new_nodes")
  cleaned_new_nodes = remove_existing_nodes_from_new_node_list(new_nodes, current_masters + current_nodes)
  remove_marker_files_for_nodes(current_masters + current_nodes, get_basedir() + "/data/new_nodes")

  if not cleaned_new_nodes:
    print("No new nodes found for provisioning, exiting.")
    sys.exit(0)
  
  if not current_masters:
    cleaned_new_nodes = add_new_master(get_basedir(), cleaned_new_nodes)
  
  if cleaned_new_nodes:
    add_new_nodes(get_basedir(), cleaned_new_nodes)