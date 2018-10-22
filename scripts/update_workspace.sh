curl \
  --header "Authorization: Bearer $ATLAS_TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request PATCH \
  --data @config/workspace.json \
  https://app.terraform.io/api/v2/organizations/${1}/workspaces/workspace-2
»
