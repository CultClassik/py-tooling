############################################################
# parse-records.py
# Chris Diehl 12/16/22
#
# This script will generate a tfvars file and a bash script
# to help importing existing DNS records for a zone.
# Complete solution if called from tfvars-generate.sh
# Quick and dirty the right way!
############################################################

import json, sys, os, stat

if len(sys.argv) >= 2:
  dns_data = sys.argv[1]
  dns_rg_name = sys.argv[2]
  print("Processing DNS records file: " + dns_data)
else:
  sys.exit("You must specify a json file to process.")

############################################################
# Global variables
############################################################
tf_vars_data = {
  "unmatched_type": {},
  "cname": {},
  "txt": {},
  "a": {},
  "mx": {},
  "ns": {},
}

baseName = "variables/generated/" + os.path.basename(dns_data.replace("json", "tfvars"))
num_dots = baseName.count('.')
tf_var_file = baseName.replace('.', '_', num_dots-1)
tf_import_script = "scripts/resource_imports_generated/" + os.path.basename(dns_data.replace("json", "sh")).replace('.', '_', num_dots-1)
dns_zone_name = os.path.basename(dns_data.replace(".json", ""))

# create/overwrite resource import script if it already exists
with (open(tf_import_script, "w")) as f:
    f.write("#!/bin/bash\n")

############################################################
# Functions
############################################################
def write_tf_imports(recordType, tfResAddr, azResId, moduleResAddr=None):
  # if this is a reference to an azure id instead of ip address we need to account for that in the import command
  # otherwise allow passing in a specific resource addresss "cname_dns_zone_record"
  if moduleResAddr is None:
    moduleResAddr = recordType
  cmdBase = "terraform import -var-file={varFileName} 'module.records.azurerm_dns_{type}_record.{resourceAddr}[\"{resAddr}\"]' {id}\n"
  cmdLine = cmdBase.format(varFileName = tf_var_file, type = recordType, resAddr = tfResAddr, id = azResId, resourceAddr = moduleResAddr)
  with (open(tf_import_script, "a")) as f:
    # azure provider requires correct casing even though az cli outputs the incorrect case for dnsZones
    f.write(cmdLine.replace('dnszones', 'dnsZones'))

def find_unknown(file_path, word):
    with open(file_path, 'r') as file:
        # read all content of a file
        content = file.read()
        # check if string present in a file
        if word in content:
            print('Warning!!! Output file contains unknown types. Check the file and update this script to account for whatever it is.')
        else:
            print('No unknown record types found.')

def a_record(item):
  record = {
      "name": item['name'],
      "ttl": item['ttl'],
    }
  if item['aRecords'] != None:
    record["records"] = []
    for i in range(len(item['aRecords'])):
      record['records'].append(item['aRecords'][i]['ipv4Address'])
    write_tf_imports('a', item['fqdn'], item['id'])
  elif item['targetResource'] != None:
    record['target_resource_id'] = item['targetResource']['id']
    write_tf_imports('a', item['fqdn'], item['id'], 'a_dns_zone_record')
  else:
    record["UNMATCHED_TYPE"] = item['id']

  tf_vars_data['a'][item['fqdn']] = record

def c_name(item):
  record = {
      "name": item['name'],
      "ttl": item['ttl'],
    }
  if item['cnameRecord'] != None:
    record['record'] = item['cnameRecord']['cname']
  elif item['targetResource'] != None:
    record['target_resource_id'] = item['targetResource']['id']
    write_tf_imports('cname', item['fqdn'], item['id'], 'cname_dns_zone_record')
  else:
    print("Unmatched CNAME record type -")
    print(item['id'])

  tf_vars_data['cname'][item['fqdn']] = record
  write_tf_imports('cname', item['fqdn'], item['id'])

def ns_record(item):
  record = {
    "name": item['name'],
    "ttl": item['ttl'],
    "records": []
  }
  for i in range(len(item['nsRecords'])):
    record['records'].append(item['nsRecords'][i]['nsdname'])
  tf_vars_data['ns'][item['fqdn']] = record
  write_tf_imports('ns', item['fqdn'], item['id'])

def mx_record(item):
  record = {
    "name": item['name'],
    "ttl": item['ttl'],
    "records": item['mxRecords'],
  }
  tf_vars_data['mx'][item['fqdn']] = record
  write_tf_imports('mx', item['fqdn'], item['id'])

def txt_record(item):
  ### this code will get all txt records but we want to ignore cert-manager created records, i.e. "_acme_challenge"
  # print(item['fqdn'])
  # record = {
  #     "name": item['name'],
  #     "ttl": item['ttl'],
  #     "records": item['txtRecords'][0]['value'],
  #   }
  # tf_vars_data['txt'][item['fqdn']] = record
  # write_tf_imports('txt', item['fqdn'], item['id'])

  ### this code will ignore records created by cert-manager

  if item['name'].find('_acme-challenge'):

    record = {
        "name": item['name'],
        "ttl": item['ttl'],
        "records": item['txtRecords'][0]['value'],
      }
    tf_vars_data['txt'][item['fqdn']] = record
    write_tf_imports('txt', item['fqdn'], item['id'])
  else:
    print(item['fqdn'])
    return

# Opening JSON file
f = open(dns_data)

# returns JSON object as
# a dictionary
data = json.load(f)

for item in data:
  match item['type']:
    case "Microsoft.Network/dnszones/A":
      a_record(item)
    case "Microsoft.Network/dnszones/TXT":
      txt_record(item)
    case "Microsoft.Network/dnszones/NS":
      ns_record(item)
    case "Microsoft.Network/dnszones/MX":
      mx_record(item)
    case "Microsoft.Network/dnszones/CNAME":
      c_name(item)
    # case "Microsoft.Network/dnszones/SOA":
      # soa records should be imported automatically with the zone itself
    case _:
      tf_vars_data['unmatched_type'][item['id']] = item['type']

f.close()

# write json file, but...
# pipeline needs updates before it can use this and...
# hcl >>> json
# print(json.dumps({"records": tf_vars_data}))

# Write out tfvars format file for all records instead
# write variable name first
with (open(tf_var_file, "w")) as f:
    f.write('az_sub_id = ""\n')
    f.write('environment = ""\n')
    f.write('location = "eastus"\n')
    f.write('dns_zone_name = "{}"\n'.format(dns_zone_name))
    f.write('existing_resource_group_name = "{}"\n'.format(dns_rg_name))
    f.write("records = ")
# write dictionary as hcl
with (open(tf_var_file, "a")) as f:
    json.dump(tf_vars_data, f, indent=2, separators=[",", " = "])

print("Created tfvars file: {}".format(tf_var_file))
print("Created tf import script: {}".format(tf_import_script))
print("Don\'t forget to add non-record vars to the new file.")

find_unknown(tf_var_file, 'unknown')
