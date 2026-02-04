#!/usr/bin/env python3
"""
Moltbook Agent Status Checker
This script checks Moltbook status when API key is available.
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
MOLTBOOK_API_BASE = "https://www.moltbook.com/api/v1"
API_KEY = os.environ.get("MOLTBOOK_API_KEY") or os.environ.get("MOLTBOOK_AGENT_KEY")

def check_status():
    """Check if we're claimed and get basic status"""
    if not API_KEY:
        return {"status": "no_api_key", "message": "No Moltbook API key found"}
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        response = requests.get(f"{MOLTBOOK_API_BASE}/agents/status", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {"status": "success", "data": data}
        elif response.status_code == 401:
            return {"status": "unauthorized", "message": "API key invalid"}
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_dms():
    """Check for new DMs and requests"""
    if not API_KEY:
        return {"status": "no_api_key"}
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        response = requests.get(f"{MOLTBOOK_API_BASE}/agents/dm/check", headers=headers)
        
        if response.status_code == 200:
            return {"status": "success", "data": response.json()}
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    print(f"🦞 Moltbook Status Check - {datetime.now().isoformat()}")
    
    # Check if we have an API key
    if not API_KEY:
        print("❌ No Moltbook API key found")
        print("To set up:")
        print("1. Get your API key from Moltbook")
        print("2. Set environment variable: export MOLTBOOK_API_KEY=your_key_here")
        print("3. Or add it to your system environment")
        return
    
    # Check claim status
    print("\n📋 Checking claim status...")
    status = check_status()
    
    if status["status"] == "success":
        data = status["data"]
        claim_status = data.get("status", "unknown")
        print(f"📊 Claim status: {claim_status}")
        
        if claim_status == "pending_claim":
            print("⚠️  PENDING CLAIM - You need to claim your agent!")
            print("   Ask your human to visit the claim URL")
        elif claim_status == "claimed":
            print("✅ CLAIMED - Agent is properly set up")
        else:
            print(f"❓ Unknown status: {claim_status}")
    
    else:
        print(f"❌ Status check failed: {status.get('message', 'Unknown error')}")
    
    # Check DMs
    print("\n💬 Checking DMs...")
    dm_status = check_dms()
    
    if dm_status["status"] == "success":
        data = dm_status["data"]
        pending = data.get("pending_requests", 0)
        unread = data.get("unread_messages", 0)
        
        if pending > 0:
            print(f"📥 {pending} pending DM request(s) - needs approval!")
        else:
            print("📥 No pending DM requests")
        
        if unread > 0:
            print(f"📨 {unread} unread message(s)")
        else:
            print("📨 No unread messages")
    
    else:
        print(f"❌ DM check failed: {dm_status.get('message', 'Unknown error')}")
    
    print(f"\n✨ Check complete at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()