#!/bin/bash
# Load all MVP agents into JARVIS registry
# Usage: ./load_agents.sh <tenant_slug> <api_token>

TENANT_SLUG=${1:-demo}
TOKEN=${2:-}
BASE_URL=${JARVIS_URL:-http://localhost:8000/api/v1}

echo "Loading JARVIS agents for tenant: $TENANT_SLUG"

for config in ../agents/*.json; do
    name=$(basename "$config" .json)
    echo "Registering agent: $name"
    
    if [ -n "$TOKEN" ]; then
        curl -s -X POST "$BASE_URL/agents/load-config" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"config_path\": \"$config\"}"
    else
        echo "Skipping $name (no token provided)"
    fi
    echo ""
done

echo "Agent loading complete"
