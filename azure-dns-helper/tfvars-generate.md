* This script combined with parse-records.py will generate a tfvars file to managed a dns zone and records as well as a bash script to import those existing DNS resources.
* SOA records are not processed, they should be imported along with the zone itself but you should verify.

## Usage
```bash
az login

az account set -n <account name>

export ARM_SUBSCRIPTION_ID="3810f594-f91b-404a-b6eb-ebf9b9e4f62c" # diehlabs non-prod

export TF_VAR_git_repo=https://gitlab.com/diehlabs/devops/azure-dns/iac-azure-dns-diehlabsplatform &&\
export ZONE_NAME=dev.diehlabsplatform.com &&\
export ZONE_RG_NAME=dns-rg-diehlabsplatform-com

# "dev.diehlabsplatform.com" is the zone name to import
# "common" is the name of the existing RG where the zone exists
./scripts/tfvars-generate.sh "$ZONE_RG_NAME" "$ZONE_NAME"

# now check the tfvars file and populate any additional vars
# if you've already moved records from the primary zone, remove the subzone from the record name i.e. change the names from "api.dev" to "api"
code "variables/generated/${ZONE_NAME//./_}.tfvars"

# you will need to export the ARM variables first - ARM_TENANT_ID, ARM_CLIENT_ID, ARM_CLIENT_SECRET since Terraform will need them - this is the spn used to manage the DNS resources in the given subscription
# you'll also need to export the ARM_ACCESS_KEY as long as we're still using it - see README.md in the repo root for more info
# also note - this will run a 'more' on the vars file for you to review - hit space bar to scroll all the way thru, then it will wait for 10 sec in case you want to cancel
./scripts/tf-import.sh "$ZONE_NAME" "$ZONE_RG_NAME"

```


terraform state rm 'module.dns_zone.azurerm_dns_zone.zone[0]'
```bash
# if you forget to set some vars the first time around, this is the generic zone import command that the script uses - run it after seeing necessary env vars
terraform import -var-file="variables/${ZONE_NAME//./_}.tfvars" \
'module.dns_zone.azurerm_dns_zone.zone[0]' \
"/subscriptions/${ARM_SUBSCRIPTION_ID}/resourceGroups/${ZONE_RG_NAME}/providers/Microsoft.Network/dnsZones/${ZONE_NAME}"
```