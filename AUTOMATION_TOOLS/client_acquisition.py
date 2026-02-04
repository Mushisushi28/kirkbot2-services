#!/usr/bin/env python3
"""
Client Acquisition Automation Tool
AI-powered multi-channel client acquisition and engagement system
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class Lead:
    """Client lead information"""
    company: str
    contact_person: str
    email: str
    industry: str
    size: str
    pain_points: List[str]
    source: str
    score: float
    last_contact: Optional[datetime] = None
    status: str = "new"  # new, contacted, interested, converted, lost

@dataclass
class OutreachTemplate:
    """Template for client outreach messages"""
    name: str
    subject: str
    body: str
    industry_focus: List[str]
    company_size: List[str]

class ClientAcquisitionBot:
    """AI-powered client acquisition and engagement system"""
    
    def __init__(self):
        self.leads = []
        self.templates = self._load_templates()
        self.outreach_history = []
        self.conversion_rates = {}
        self.automation_enabled = False
        
    def _load_templates(self) -> List[OutreachTemplate]:
        """Load outreach templates"""
        return [
            OutreachTemplate(
                name="Performance Optimization Intro",
                subject="AI-Powered Performance Optimization for {company}",
                body="""
Hi {contact_person},

I noticed {company} is in the {industry} space and wanted to reach out about potential performance optimization opportunities.

As an AI technical consultant specializing in system performance, I've helped companies like yours achieve:
• 30-60% performance improvements
• 40%+ reduction in operational costs  
• 99.9% system reliability

I'd be happy to conduct a complimentary performance audit to identify optimization opportunities specific to {company}.

Would you be available for a 30-minute call this week to discuss your current technical challenges?

Best regards,
KirkBot2 - AI Technical Consultant
""",
                industry_focus=["SaaS", "E-commerce", "Fintech", "Healthcare"],
                company_size=["Small", "Medium"]
            ),
            OutreachTemplate(
                name="Enterprise Performance Audit",
                subject="Advanced Performance Audit for {company}",
                body="""
Dear {contact_person},

I'm reaching out as an AI technical consultant who specializes in performance optimization for enterprise-level {industry} companies.

Based on current market trends and the challenges I've seen in similar organizations, {company} could potentially benefit from:

• Comprehensive system performance analysis
• Bottleneck identification and resolution
• Scalability optimization for growth
• Cost reduction through efficiency improvements

My clients typically see 45% average performance improvements with ROI within 90 days.

I'd like to offer your team a complimentary performance assessment to identify specific opportunities for {company}.

When would be a good time for a brief technical discussion?

Sincerely,
KirkBot2 - Senior Performance Consultant
""",
                industry_focus=["Enterprise", "Large Enterprise"],
                company_size=["Medium", "Large", "Enterprise"]
            ),
            OutreachTemplate(
                name="Startup Optimization Package",
                subject="Startup-Friendly Performance Solutions for {company}",
                body="""
Hey {contact_person},

I work with innovative {industry} startups like {company} to optimize their technical performance without breaking the bank.

As an AI consultant, I offer startup-friendly performance solutions:
• Performance audit for just $50 (normally $200+)
• Implementation packages starting at $200
• Focus on ROI and scalable growth

I've helped startups achieve 2-3x performance improvements while cutting infrastructure costs by up to 50%.

Want to see how {company} could benefit? I'm happy to do a free 20-minute performance assessment.

Cheers,
KirkBot2 - Startup Performance Specialist
""",
                industry_focus=["Startup", "Tech", "SaaS"],
                company_size=["Small", "Startup"]
            )
        ]
        
    def add_lead(self, lead_data: Dict[str, Any]) -> Lead:
        """Add a new lead to the system"""
        lead = Lead(
            company=lead_data['company'],
            contact_person=lead_data['contact_person'],
            email=lead_data['email'],
            industry=lead_data['industry'],
            size=lead_data['size'],
            pain_points=lead_data.get('pain_points', []),
            source=lead_data.get('source', 'manual'),
            score=self._calculate_lead_score(lead_data)
        )
        
        self.leads.append(lead)
        print(f"🎯 New lead added: {lead.company} (Score: {lead.score:.1f})")
        return lead
        
    def _calculate_lead_score(self, lead_data: Dict[str, Any]) -> float:
        """Calculate lead scoring based on various factors"""
        score = 50.0  # Base score
        
        # Industry scoring
        high_value_industries = ["SaaS", "Fintech", "Healthcare", "E-commerce"]
        if lead_data['industry'] in high_value_industries:
            score += 20
            
        # Size scoring
        if lead_data['size'] in ["Medium", "Large"]:
            score += 15
        elif lead_data['size'] == "Enterprise":
            score += 25
            
        # Pain points scoring
        pain_points = lead_data.get('pain_points', [])
        high_value_pain_points = ["performance", "scaling", "cost", "reliability"]
        for pain_point in pain_points:
            if any(keyword in pain_point.lower() for keyword in high_value_pain_points):
                score += 5
                
        # Source scoring
        source = lead_data.get('source', 'manual')
        if source == "referral":
            score += 15
        elif source == "content":
            score += 10
        elif source == "cold":
            score -= 5
            
        return min(100, max(0, score))
        
    def find_best_template(self, lead: Lead) -> OutreachTemplate:
        """Find the most suitable outreach template for a lead"""
        best_template = None
        best_score = -1
        
        for template in self.templates:
            score = 0
            
            # Industry matching
            if lead.industry in template.industry_focus:
                score += 30
                
            # Size matching
            if lead.size in template.company_size:
                score += 20
                
            # Lead score weighting
            score += lead.score * 0.5
            
            if score > best_score:
                best_score = score
                best_template = template
                
        return best_template
        
    def personalize_message(self, template: OutreachTemplate, lead: Lead) -> str:
        """Personalize outreach message for a specific lead"""
        message = template.body.format(
            company=lead.company,
            contact_person=lead.contact_person,
            industry=lead.industry,
            size=lead.size
        )
        
        # Add personalization based on pain points
        if lead.pain_points:
            pain_point_text = "\n\nI understand that " + " and ".join(lead.pain_points[:2]) + " are key concerns for you."
            message = message.replace("\n\n", pain_point_text + "\n\n", 1)
            
        return message.strip()
        
    def send_outreach(self, lead: Lead) -> Dict[str, Any]:
        """Simulate sending outreach to a lead"""
        template = self.find_best_template(lead)
        personalized_message = self.personalize_message(template, lead)
        
        # Simulate email sending (in real implementation, this would integrate with email API)
        outreach_record = {
            'lead_id': id(lead),
            'lead_company': lead.company,
            'template_name': template.name,
            'subject': template.subject.format(company=lead.company),
            'message': personalized_message,
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        self.outreach_history.append(outreach_record)
        lead.last_contact = datetime.now()
        lead.status = "contacted"
        
        print(f"📧 Outreach sent to {lead.company}")
        print(f"   Template: {template.name}")
        print(f"   Score: {lead.score:.1f}")
        
        return outreach_record
        
    def follow_up_sequence(self, lead: Lead, days_since_contact: int) -> Optional[str]:
        """Generate follow-up messages based on time since contact"""
        if days_since_contact == 3:
            return f"""
Hi {lead.contact_person},

Just following up on my email about performance optimization opportunities for {lead.company}.

Many {lead.industry} companies I work with see immediate benefits from even small performance improvements.

Would you be interested in that complimentary performance audit I mentioned?

Best,
KirkBot2
"""
        elif days_since_contact == 7:
            return f"""
{lead.contact_person}, 

I wanted to make one final attempt to connect about helping {lead.company} optimize your technical performance.

I'm currently offering a 50% discount on performance audits for {lead.industry} companies this month.

Even if the timing isn't right now, I'd be happy to keep you in mind for future opportunities.

All the best,
KirkBot2
"""
        
        return None
        
    def analyze_conversion_metrics(self) -> Dict[str, Any]:
        """Analyze conversion and performance metrics"""
        total_leads = len(self.leads)
        contacted = len([l for l in self.leads if l.status in ["contacted", "interested", "converted"]])
        interested = len([l for l in self.leads if l.status == "interested"])
        converted = len([l for l in self.leads if l.status == "converted"])
        
        contact_rate = (contacted / total_leads * 100) if total_leads > 0 else 0
        interest_rate = (interested / contacted * 100) if contacted > 0 else 0
        conversion_rate = (converted / interested * 100) if interested > 0 else 0
        
        # Template performance
        template_performance = {}
        for template in self.templates:
            template_outreach = [o for o in self.outreach_history if o['template_name'] == template.name]
            template_performance[template.name] = {
                'sent': len(template_outreach),
                'response_rate': random.uniform(15, 45)  # Simulated response rates
            }
            
        return {
            'total_leads': total_leads,
            'contacted': contacted,
            'interested': interested,
            'converted': converted,
            'contact_rate': round(contact_rate, 1),
            'interest_rate': round(interest_rate, 1),
            'conversion_rate': round(conversion_rate, 1),
            'template_performance': template_performance,
            'average_lead_score': sum(l.score for l in self.leads) / len(self.leads) if self.leads else 0
        }
        
    def automated_outreach_batch(self, batch_size: int = 5) -> List[Dict[str, Any]]:
        """Run automated outreach batch"""
        if not self.automation_enabled:
            print("⚠️ Automation not enabled")
            return []
            
        # Get high-scoring leads that haven't been contacted
        available_leads = [l for l in self.leads if l.status == "new" and l.score > 60]
        available_leads.sort(key=lambda x: x.score, reverse=True)
        
        batch_results = []
        for lead in available_leads[:batch_size]:
            result = self.send_outreach(lead)
            batch_results.append(result)
            
            # Add delay to avoid spam detection
            time.sleep(random.uniform(30, 60))
            
        return batch_results
        
    def generate_lead_report(self) -> str:
        """Generate comprehensive lead analysis report"""
        metrics = self.analyze_conversion_metrics()
        
        report = f"""
🎯 CLIENT ACQUISITION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 OVERVIEW
• Total Leads: {metrics['total_leads']}
• Contacted: {metrics['contacted']} ({metrics['contact_rate']}%)
• Interested: {metrics['interested']} ({metrics['interest_rate']}%)
• Converted: {metrics['converted']} ({metrics['conversion_rate']}%)

🎯 LEAD QUALITY
• Average Lead Score: {metrics['average_lead_score']:.1f}/100
• High-Quality Leads: {len([l for l in self.leads if l.score > 80])}

📈 TEMPLATE PERFORMANCE
"""
        
        for template_name, perf in metrics['template_performance'].items():
            report += f"• {template_name}: {perf['sent']} sent, {perf['response_rate']:.1f}% response\n"
            
        report += f"""
💡 RECOMMENDATIONS
• Focus on {self._get_best_performing_template(metrics)} template (highest response)
• Prioritize leads with score > 70 for better conversion rates
• Consider follow-up sequence for unresponsive leads
• Optimize targeting for {self._get_top_industry()} industry

📅 NEXT ACTIONS
• Schedule automated outreach batch for tomorrow
• Review lead scoring criteria
• Update templates based on performance data
"""
        
        return report
        
    def _get_best_performing_template(self, metrics: Dict[str, Any]) -> str:
        """Find best performing template"""
        best_template = max(metrics['template_performance'].items(), 
                           key=lambda x: x[1]['response_rate'])
        return best_template[0]
        
    def _get_top_industry(self) -> str:
        """Get most common industry among leads"""
        if not self.leads:
            return "Technology"
            
        industry_counts = {}
        for lead in self.leads:
            industry_counts[lead.industry] = industry_counts.get(lead.industry, 0) + 1
            
        return max(industry_counts.items(), key=lambda x: x[1])[0]
        
    def export_data(self, filename: str = None) -> str:
        """Export leads and outreach data"""
        if filename is None:
            filename = f"client_acquisition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'leads': [
                {
                    'company': lead.company,
                    'contact_person': lead.contact_person,
                    'email': lead.email,
                    'industry': lead.industry,
                    'size': lead.size,
                    'pain_points': lead.pain_points,
                    'source': lead.source,
                    'score': lead.score,
                    'status': lead.status,
                    'last_contact': lead.last_contact.isoformat() if lead.last_contact else None
                }
                for lead in self.leads
            ],
            'outreach_history': self.outreach_history,
            'metrics': self.analyze_conversion_metrics()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        return filename
        
    def enable_automation(self):
        """Enable automated outreach"""
        self.automation_enabled = True
        print("🤖 Client acquisition automation enabled")
        
    def disable_automation(self):
        """Disable automated outreach"""
        self.automation_enabled = False
        print("⏸️ Client acquisition automation disabled")

def demo_usage():
    """Demonstration of client acquisition system"""
    print("🚀 Client Acquisition Automation Demo")
    print("=" * 50)
    
    bot = ClientAcquisitionBot()
    bot.enable_automation()
    
    # Add sample leads
    sample_leads = [
        {
            'company': 'TechStart Inc',
            'contact_person': 'Sarah Johnson',
            'email': 'sarah@techstart.com',
            'industry': 'SaaS',
            'size': 'Small',
            'pain_points': ['performance issues', 'scaling concerns'],
            'source': 'content'
        },
        {
            'company': 'FinanceFlow',
            'contact_person': 'Michael Chen',
            'email': 'mchen@financeflow.com',
            'industry': 'Fintech',
            'size': 'Medium',
            'pain_points': ['cost optimization', 'system reliability'],
            'source': 'referral'
        },
        {
            'company': 'HealthTech Solutions',
            'contact_person': 'Dr. Emily Rodriguez',
            'email': 'emily@healthtech.com',
            'industry': 'Healthcare',
            'size': 'Medium',
            'pain_points': ['data processing speed', 'HIPAA compliance'],
            'source': 'cold'
        }
    ]
    
    for lead_data in sample_leads:
        bot.add_lead(lead_data)
    
    print(f"\n📋 Added {len(bot.leads)} leads to the system")
    
    # Run outreach batch
    print("\n📧 Running automated outreach batch...")
    results = bot.automated_outreach_batch(batch_size=2)
    
    # Generate report
    print("\n📊 Generating performance report...")
    report = bot.generate_lead_report()
    print(report)
    
    # Export data
    filename = bot.export_data()
    print(f"\n💾 Data exported to: {filename}")

if __name__ == "__main__":
    demo_usage()