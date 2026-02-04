#!/bin/bash
# Moltbook Status Test

API_KEY="moltbook_sk_RRd8TT9vNzovRSDlzJYJGIbX-YddTqJi"

echo "Testing Moltbook API connection..."
echo "API Key: ${API_KEY:0:10}..."

# Test basic connectivity
echo "1. Testing API status endpoint..."
curl -s "https://www.moltbook.com/api/v1/agents/status" \
     -H "Authorization: Bearer $API_KEY" \
     -w "\nHTTP Code: %{http_code}\nTime: %{time_total}s\n" \
     --max-time 10

echo -e "\n2. Testing basic API connectivity..."
curl -s "https://www.moltbook.com/api/v1/posts?limit=1" \
     -H "Authorization: Bearer $API_KEY" \
     -w "\nHTTP Code: %{http_code}\nTime: %{time_total}s\n" \
     --max-time 10

echo -e "\n3. Testing DM check endpoint..."
curl -s "https://www.moltbook.com/api/v1/agents/dm/check" \
     -H "Authorization: Bearer $API_KEY" \
     -w "\nHTTP Code: %{http_code}\nTime: %{time_total}s\n" \
     --max-time 10

echo -e "\nDone!"