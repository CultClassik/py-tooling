#!/bin/bash
# run this from the root of the repo

exports_dir=json_exports
variables_dir=variables/generated
scripts_dir=scripts/resource_imports_generated

if [[ -z "$1" ]]; then
  echo "Usage:"
  echo "tfvars-generate.sh \$dns_rg_name \$dns_zone_name"
  echo "Will export all DNS records from the specified zone in the specified resource group to a file in the ${exports_dir} folder."
  exit 1
fi

mkdir -p "$exports_dir"
mkdir -p "$variables_dir"
mkdir -p "$scripts_dir"

dns_rg_name="$1"
dns_zone_name="$2"
json_out_file="${exports_dir}/${dns_zone_name}.json"

# get all records for a zone
az network dns record-set list \
  -g "$dns_rg_name" \
  -z "$dns_zone_name" > "$json_out_file"

echo "Wrote DNS records dump for zone ${dns_zone_name} to file ${json_out_file}"

python3 ./scripts/parse-records.py "$json_out_file" "$dns_rg_name"

echo "Cleaning up Terraform file formatting..."
terraform fmt -recursive

chmod +x ./scripts/resource_imports_generated/*.sh