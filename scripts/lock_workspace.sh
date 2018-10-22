curl \
  --header "Authorization: Bearer $ATLAS_TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @config/lock_workspace.json \
  https://app.terraform.io/api/v2/workspaces/${1}/actions/lock
