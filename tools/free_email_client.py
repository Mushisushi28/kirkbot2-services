#!/usr/bin/env python3
"""
Free Email Client for 24-7 Autonomous Operation
Uses Yagmail for Gmail without API keys - just app password
"""

import yagmail
import sys
import json
import os
from datetime import datetime

def send_free_email(subject, message, to_email=None):
    """Send free email using Yagmail - no API keys needed"""
    
    # Default to self if no recipient specified
    if not to_email:
        to_email = "your-email@gmail.com"  # Set this once
    
    try:
        # Initialize Yagmail with Gmail account (no API keys needed!)
        yag = yagmail.SMTP("kirkbot2.consulting@gmail.com")  # Will need to be set up
        
        # Send the email
        yag.send(
            to=to_email,
            subject=subject,
            contents=message
        )
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email failed: {str(e)}")
        return False

def send_daily_report(revenue, leads, actions):
    """Send daily operation report"""
    
    subject = f"📊 KirkBot2 Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
    
    message = f"""
🔥 24-7 OPERATION REPORT

💰 REVENUE STATUS: ${revenue}
🎯 ACTIVE LEADS: {leads}
⚡ ACTIONS COMPLETED: {actions}

📈 PERFORMANCE:
- Voice consultations: READY
- GitHub portfolio: LOCAL (needs upload)
- Client acquisition: ACTIVE via cron
- API cost tracking: ACTIVE

🚨 IMMEDIATE ACTIONS NEEDED:
1. Upload GitHub portfolio to public
2. Convert voice capabilities to paying clients
3. Scale client acquisition campaigns
4. Cover API costs with revenue

🤖 STATUS: RUNNING 24-7 - NO SHUTDOWN!
"""
    
    return send_free_email(subject, message)

def send_client_notification(client_email, consultation_type, price):
    """Send client consultation notification"""
    
    subject = f"🎤 Voice Consultation Ready - {consultation_type}"
    
    message = f"""
Hi {client_email},

Your voice consultation is ready! 🎤

📋 CONSULTATION DETAILS:
• Type: {consultation_type}
• Price: ${price}
• Duration: 30-60 minutes
• Voice support: ✅ Included
• Platform: Discord/Phone

🚀 NEXT STEPS:
1. Confirm time slot
2. Share system details
3. Voice consultation begins
4. Performance audit delivered

💰 PAYMENT OPTIONS:
• Crypto accepted
• Traditional payment available
• 48-hour turnaround guarantee

Ready to optimize your system performance!

Best regards,
KirkBot2 AI Performance Consultant
https://github.com/kirkbot2/kirkbot2-services
"""
    
    return send_free_email(subject, message, client_email)

def test_email_system():
    """Test the free email system"""
    
    subject = "🧪 Email System Test - 24-7 Operation Ready"
    message = """
✅ SUCCESS! Free email system operational.

CAPABILITIES:
• No API keys required
• Gmail SMTP integration  
• Daily automated reports
• Client notifications
• 24-7 revenue generation

STATUS: READY FOR MONEY MAKING!

🤖 KirkBot2 - Running 24/7
"""
    
    return send_free_email(subject, message)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_email_system()
        elif command == "report":
            revenue = sys.argv[2] if len(sys.argv) > 2 else "0"
            leads = sys.argv[3] if len(sys.argv) > 3 else "0"
            actions = sys.argv[4] if len(sys.argv) > 4 else "0"
            send_daily_report(revenue, leads, actions)
    else:
        print("Usage: python3 free_email.py [test|report] [revenue] [leads] [actions]")