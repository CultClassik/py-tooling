#!/bin/bash

zone_name=$1
rg_name=$2

# you will need to export the ARM variables first - ARM_TENANT_ID, ARM_SUBSCRIPTION_ID, ARM_CLIENT_ID, ARM_CLIENT_SECRET since Terraform will need them
# you'll also need to export the ARM_ACCESS_KEY as long as we're still using it - see README.md in the repo root for more info

export TF_VAR_git_repo=https://gitlab.com/verituity/devops/azure-infrastructure/iac-azure-dns.git

zone_name_nodots=${zone_name//./_}
exports_dir=json_exports
variables_dir=variables/generated
scripts_dir=scripts/resource_imports_generated

more "${variables_dir}/${zone_name_nodots}.tfvars"
echo "Did you already check/finish the tfvars file? (${variables_dir}/${zone_name_nodots}.tfvars)"
echo "Namely ensure that environment and az_sub_id are populated."
read -t 10 -p "I am going to wait for 10 seconds in case you need to CTRL+C me ..."

# create the new terraform workspace
terraform workspace new "$zone_name_nodots"

# import the zone itself
terraform import -var-file="${variables_dir}/${zone_name_nodots}.tfvars" 'module.dns_zone.azurerm_dns_zone.zone[0]'  "/subscriptions/${ARM_SUBSCRIPTION_ID}/resourceGroups/${rg_name}/providers/Microsoft.Network/dnsZones/${zone_name}"

# import the dns records
"./scripts/resource_imports_generated/${zone_name_nodots}.sh"
read -t 10 -p "I am going to wait for 10 seconds in case you need to CTRL+C me ..."

# move the generated vars file into the variables dir so the pipeline can use it, and we know it's been imported
# this has to happen AFTER the import since the import script is looking for the vars in the variables/generated folder
mv "${variables_dir}/${zone_name_nodots}.tfvars" "variables/${zone_name_nodots}.tfvars"

# run a plan to verify no changes
terraform plan -var-file="variables/${zone_name_nodots}.tfvars"

echo "Remember to add and import the SOA record for the zone."
echo "Also remember to add the plan and apply stages for this new workspace (${zone_name_nodots}) in the ci yaml."