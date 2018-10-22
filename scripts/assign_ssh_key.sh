curl \
  --header "Authorization: Bearer $ATLAS_TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request PATCH \
  --data @config/ssh_key.json \
  https://app.terraform.io/api/v2/workspaces${1}/relationships/ssh-key
