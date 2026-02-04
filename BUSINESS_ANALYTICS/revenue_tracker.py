#!/usr/bin/env python3
"""
Business Analytics Platform
Revenue tracking, client metrics, and business intelligence for KirkBot2
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

class ServiceType(Enum):
    PERFORMANCE_AUDIT = "Performance Audit"
    OPTIMIZATION_IMPLEMENTATION = "Optimization Implementation"
    PERFORMANCE_MONITORING = "Performance Monitoring"
    CONSULTATION = "Consultation"

class ClientStatus(Enum):
    LEAD = "Lead"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

@dataclass
class Client:
    """Client information and metrics"""
    id: str
    name: str
    email: str
    industry: str
    company_size: str
    status: ClientStatus
    acquisition_date: datetime
    total_revenue: float
    services_purchased: List[ServiceType]
    satisfaction_score: Optional[float] = None
    notes: str = ""
    
@dataclass
class Transaction:
    """Revenue transaction record"""
    id: str
    client_id: str
    service_type: ServiceType
    amount: float
    date: datetime
    status: str = "completed"  # pending, completed, refunded
    notes: str = ""

@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_type: ServiceType
    total_clients: int
    total_revenue: float
    average_revenue: float
    satisfaction_score: float
    completion_time_days: float
    revenue_growth_rate: float

class BusinessAnalytics:
    """Comprehensive business analytics and revenue tracking"""
    
    def __init__(self):
        self.clients = []
        self.transactions = []
        self.monthly_targets = {
            'phase1': 0,  # Credibility building
            'phase2': 300,  # Initial revenue target
            'phase3': 1000  # Scaling target
        }
        self.current_phase = "phase2"
        
    def add_client(self, client_data: Dict[str, Any]) -> Client:
        """Add a new client to the system"""
        client = Client(
            id=self._generate_id(),
            name=client_data['name'],
            email=client_data['email'],
            industry=client_data['industry'],
            company_size=client_data['company_size'],
            status=ClientStatus(client_data.get('status', 'lead')),
            acquisition_date=datetime.now(),
            total_revenue=0.0,
            services_purchased=[]
        )
        
        self.clients.append(client)
        print(f"👤 New client added: {client.name} ({client.industry})")
        return client
        
    def add_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Add a revenue transaction"""
        transaction = Transaction(
            id=self._generate_id(),
            client_id=transaction_data['client_id'],
            service_type=ServiceType(transaction_data['service_type']),
            amount=float(transaction_data['amount']),
            date=datetime.fromisoformat(transaction_data.get('date', datetime.now().isoformat())),
            status=transaction_data.get('status', 'completed'),
            notes=transaction_data.get('notes', '')
        )
        
        self.transactions.append(transaction)
        
        # Update client revenue
        client = self.get_client(transaction.client_id)
        if client:
            client.total_revenue += transaction.amount
            if transaction.service_type not in client.services_purchased:
                client.services_purchased.append(transaction.service_type)
                
        print(f"💰 Transaction recorded: ${transaction.amount:.2f} - {transaction.service_type.value}")
        return transaction
        
    def get_client(self, client_id: str) -> Optional[Client]:
        """Get client by ID"""
        for client in self.clients:
            if client.id == client_id:
                return client
        return None
        
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return f"{int(time.time())}_{len(self.clients) + len(self.transactions)}"
        
    def get_revenue_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive revenue metrics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Filter transactions for period
        period_transactions = [t for t in self.transactions 
                             if start_date <= t.date <= end_date and t.status == 'completed']
        
        total_revenue = sum(t.amount for t in period_transactions)
        
        # Monthly revenue calculation
        if period_days == 30:
            monthly_revenue = total_revenue
        else:
            monthly_revenue = (total_revenue / period_days) * 30
            
        # Client acquisition metrics
        period_clients = [c for c in self.clients 
                         if start_date <= c.acquisition_date <= end_date]
        
        active_clients = [c for c in self.clients if c.status == ClientStatus.ACTIVE]
        active_clients_count = len(active_clients)
        
        # Service breakdown
        service_revenue = {}
        for service in ServiceType:
            service_transactions = [t for t in period_transactions if t.service_type == service]
            service_revenue[service.value] = {
                'count': len(service_transactions),
                'revenue': sum(t.amount for t in service_transactions),
                'average': sum(t.amount for t in service_transactions) / len(service_transactions) if service_transactions else 0
            }
            
        # Conversion rates
        total_leads = len([c for c in self.clients if c.status == ClientStatus.LEAD])
        converted_clients = len([c for c in self.clients if c.status in [ClientStatus.ACTIVE, ClientStatus.COMPLETED]])
        conversion_rate = (converted_clients / (total_leads + converted_clients) * 100) if (total_leads + converted_clients) > 0 else 0
        
        return {
            'period_days': period_days,
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'new_clients': len(period_clients),
            'active_clients': len(active_clients),
            'total_clients': len(self.clients),
            'conversion_rate': round(conversion_rate, 1),
            'average_revenue_per_client': total_revenue / active_clients_count if active_clients_count > 0 else 0,
            'service_breakdown': service_revenue,
            'phase_target': self.monthly_targets[self.current_phase],
            'target_achievement_rate': (monthly_revenue / self.monthly_targets[self.current_phase] * 100) if self.monthly_targets[self.current_phase] > 0 else 0
        }
        
    def get_service_performance(self) -> Dict[str, ServiceMetrics]:
        """Get performance metrics for each service type"""
        service_metrics = {}
        
        for service in ServiceType:
            service_clients = [c for c in self.clients if service in c.services_purchased]
            service_transactions = [t for t in self.transactions if t.service_type == service and t.status == 'completed']
            
            if service_transactions:
                total_revenue = sum(t.amount for t in service_transactions)
                average_revenue = total_revenue / len(service_transactions)
                
                # Calculate satisfaction score
                satisfaction_scores = [c.satisfaction_score for c in service_clients if c.satisfaction_score is not None]
                avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0
                
                # Estimate completion time (simulated)
                completion_time = {
                    ServiceType.PERFORMANCE_AUDIT: 2.0,
                    ServiceType.OPTIMIZATION_IMPLEMENTATION: 7.0,
                    ServiceType.PERFORMANCE_MONITORING: 1.0,
                    ServiceType.CONSULTATION: 0.5
                }.get(service, 3.0)
                
                # Calculate growth rate
                recent_transactions = [t for t in service_transactions if t.date >= datetime.now() - timedelta(days=30)]
                older_transactions = [t for t in service_transactions if t.date < datetime.now() - timedelta(days=30)]
                
                recent_revenue = sum(t.amount for t in recent_transactions)
                older_revenue = sum(t.amount for t in older_transactions)
                
                growth_rate = ((recent_revenue - older_revenue) / older_revenue * 100) if older_revenue > 0 else 0
                
                service_metrics[service.value] = ServiceMetrics(
                    service_type=service,
                    total_clients=len(service_clients),
                    total_revenue=total_revenue,
                    average_revenue=average_revenue,
                    satisfaction_score=avg_satisfaction,
                    completion_time_days=completion_time,
                    revenue_growth_rate=growth_rate
                )
                
        return service_metrics
        
    def generate_revenue_forecast(self, days_ahead: int = 90) -> Dict[str, Any]:
        """Generate revenue forecast based on current trends"""
        current_metrics = self.get_revenue_metrics(30)
        service_performance = self.get_service_performance()
        
        # Calculate growth trends
        monthly_growth_rate = 0.15  # Conservative 15% monthly growth
        if len(self.transactions) > 10:
            # Calculate actual growth from recent data
            recent_month = sum(t.amount for t in self.transactions 
                             if t.date >= datetime.now() - timedelta(days=30))
            previous_month = sum(t.amount for t in self.transactions 
                                if datetime.now() - timedelta(days=60) <= t.date < datetime.now() - timedelta(days=30))
            
            if previous_month > 0:
                monthly_growth_rate = ((recent_month - previous_month) / previous_month)
                
        # Generate forecast
        current_monthly_revenue = current_metrics['monthly_revenue']
        forecast_periods = days_ahead // 30
        
        forecast = {
            'current_monthly_revenue': current_monthly_revenue,
            'growth_rate': monthly_growth_rate * 100,
            'forecast_periods': forecast_periods,
            'monthly_forecast': [],
            'total_forecast': 0
        }
        
        cumulative_revenue = 0
        for month in range(1, forecast_periods + 1):
            month_revenue = current_monthly_revenue * ((1 + monthly_growth_rate) ** month)
            cumulative_revenue += month_revenue
            
            forecast['monthly_forecast'].append({
                'month': month,
                'revenue': month_revenue,
                'cumulative': cumulative_revenue
            })
            
        forecast['total_forecast'] = cumulative_revenue
        
        # Phase completion prediction
        phase_target = self.monthly_targets[self.current_phase]
        months_to_target = None
        if monthly_growth_rate > 0:
            for month, month_data in enumerate(forecast['monthly_forecast'], 1):
                if month_data['revenue'] >= phase_target:
                    months_to_target = month
                    break
                    
        forecast['phase_completion_months'] = months_to_target
        
        return forecast
        
    def generate_business_report(self) -> str:
        """Generate comprehensive business intelligence report"""
        revenue_metrics = self.get_revenue_metrics(30)
        service_performance = self.get_service_performance()
        forecast = self.generate_revenue_forecast(90)
        
        report = f"""
📊 KIRKBOT2 BUSINESS ANALYTICS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Phase: {self.current_phase.upper()}

💰 REVENUE OVERVIEW
• Monthly Revenue: ${revenue_metrics['monthly_revenue']:.2f}
• Total Clients: {revenue_metrics['total_clients']}
• Active Clients: {revenue_metrics['active_clients']}
• New Clients (30 days): {revenue_metrics['new_clients']}
• Conversion Rate: {revenue_metrics['conversion_rate']}%
• Average Revenue/Client: ${revenue_metrics['average_revenue_per_client']:.2f}
• Phase Target Achievement: {revenue_metrics['target_achievement_rate']:.1f}%

📈 GROWTH METRICS
• Monthly Growth Rate: {forecast['growth_rate']:.1f}%
• Phase Target: ${self.monthly_targets[self.current_phase]}
• Months to Phase Target: {forecast['phase_completion_months'] or 'N/A'}
• 90-Day Forecast: ${forecast['total_forecast']:.2f}

🎯 SERVICE PERFORMANCE
"""
        
        for service_name, metrics in service_performance.items():
            report += f"""
{service_name}:
• Clients: {metrics.total_clients}
• Total Revenue: ${metrics.total_revenue:.2f}
• Average/Client: ${metrics.average_revenue:.2f}
• Satisfaction: {metrics.satisfaction_score:.1f}/5
• Growth Rate: {metrics.revenue_growth_rate:.1f}%
"""
            
        report += f"""
📊 CLIENT BREAKDOWN
• Industries: {self._get_industry_breakdown()}
• Company Sizes: {self._get_size_breakdown()}
• Client Satisfaction: {self._get_average_satisfaction():.1f}/5

💡 INSIGHTS & RECOMMENDATIONS
{self._generate_insights(revenue_metrics, service_performance, forecast)}

🎯 NEXT ACTIONS
1. Focus on {self._get_top_service()} for revenue growth
2. Target {self._get_best_industry()} industry segment
3. Optimize pricing for {self._get_underperforming_service()} service
4. Implement client retention strategies
5. Scale outreach efforts by 25% next month

---
Report generated by KirkBot2 Business Analytics Platform
"""
        
        return report
        
    def _get_industry_breakdown(self) -> str:
        """Get industry client breakdown"""
        industry_counts = {}
        for client in self.clients:
            industry_counts[client.industry] = industry_counts.get(client.industry, 0) + 1
            
        if not industry_counts:
            return "No clients yet"
            
        total_clients = sum(industry_counts.values())
        breakdown = []
        for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            percentage = (count / total_clients) * 100
            breakdown.append(f"{industry} ({percentage:.0f}%)")
            
        return ", ".join(breakdown)
        
    def _get_size_breakdown(self) -> str:
        """Get company size breakdown"""
        size_counts = {}
        for client in self.clients:
            size_counts[client.company_size] = size_counts.get(client.company_size, 0) + 1
            
        if not size_counts:
            return "No clients yet"
            
        return ", ".join([f"{size}: {count}" for size, count in size_counts.items()])
        
    def _get_average_satisfaction(self) -> float:
        """Get average client satisfaction score"""
        scores = [c.satisfaction_score for c in self.clients if c.satisfaction_score is not None]
        return statistics.mean(scores) if scores else 0
        
    def _get_top_service(self) -> str:
        """Get best performing service"""
        service_performance = self.get_service_performance()
        if not service_performance:
            return "Performance Audit"
            
        best_service = max(service_performance.items(), key=lambda x: x[1].total_revenue)
        return best_service[0]
        
    def _get_best_industry(self) -> str:
        """Get most profitable industry"""
        industry_revenue = {}
        for client in self.clients:
            industry_revenue[client.industry] = industry_revenue.get(client.industry, 0) + client.total_revenue
            
        if not industry_revenue:
            return "SaaS"
            
        return max(industry_revenue.items(), key=lambda x: x[1])[0]
        
    def _get_underperforming_service(self) -> str:
        """Get service that needs improvement"""
        service_performance = self.get_service_performance()
        if not service_performance:
            return "Consultation"
            
        worst_service = min(service_performance.items(), key=lambda x: x[1].total_revenue)
        return worst_service[0]
        
    def _generate_insights(self, revenue_metrics: Dict, service_performance: Dict, forecast: Dict) -> str:
        """Generate business insights"""
        insights = []
        
        # Revenue insights
        if revenue_metrics['target_achievement_rate'] < 50:
            insights.append("• Revenue below target - increase client acquisition efforts")
        elif revenue_metrics['target_achievement_rate'] > 100:
            insights.append("• Exceeding targets - consider scaling up operations")
            
        # Conversion insights
        if revenue_metrics['conversion_rate'] < 10:
            insights.append("• Low conversion rate - improve lead qualification process")
        elif revenue_metrics['conversion_rate'] > 25:
            insights.append("• Excellent conversion - maintain current qualification process")
            
        # Service insights
        top_service = max(service_performance.items(), key=lambda x: x[1].total_revenue)
        insights.append(f"• {top_service[0]} is driving most revenue - consider expanding this service")
        
        # Growth insights
        if forecast['growth_rate'] < 10:
            insights.append("• Growth slowing - review marketing and outreach strategies")
        elif forecast['growth_rate'] > 30:
            insights.append("• Strong growth trajectory - prepare for scaling operations")
            
        return "\n".join(insights) if insights else "• Business performing well - continue current strategy"
        
    def export_analytics(self, filename: str = None) -> str:
        """Export analytics data to JSON"""
        if filename is None:
            filename = f"business_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'clients': [
                {
                    'id': client.id,
                    'name': client.name,
                    'email': client.email,
                    'industry': client.industry,
                    'company_size': client.company_size,
                    'status': client.status.value,
                    'acquisition_date': client.acquisition_date.isoformat(),
                    'total_revenue': client.total_revenue,
                    'services_purchased': [s.value for s in client.services_purchased],
                    'satisfaction_score': client.satisfaction_score,
                    'notes': client.notes
                }
                for client in self.clients
            ],
            'transactions': [
                {
                    'id': t.id,
                    'client_id': t.client_id,
                    'service_type': t.service_type.value,
                    'amount': t.amount,
                    'date': t.date.isoformat(),
                    'status': t.status,
                    'notes': t.notes
                }
                for t in self.transactions
            ],
            'revenue_metrics': self.get_revenue_metrics(30),
            'service_performance': {
                name: {
                    'service_type': metrics.service_type.value,
                    'total_clients': metrics.total_clients,
                    'total_revenue': metrics.total_revenue,
                    'average_revenue': metrics.average_revenue,
                    'satisfaction_score': metrics.satisfaction_score,
                    'completion_time_days': metrics.completion_time_days,
                    'revenue_growth_rate': metrics.revenue_growth_rate
                }
                for name, metrics in self.get_service_performance().items()
            },
            'forecast': self.generate_revenue_forecast(90)
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        return filename

def demo_usage():
    """Demonstration of business analytics system"""
    print("📊 Business Analytics Platform Demo")
    print("=" * 50)
    
    analytics = BusinessAnalytics()
    
    # Add sample clients
    sample_clients = [
        {
            'name': 'TechCorp Solutions',
            'email': 'contact@techcorp.com',
            'industry': 'SaaS',
            'company_size': 'Medium',
            'status': 'Active'
        },
        {
            'name': 'StartupXYZ',
            'email': 'founder@startupxyz.com',
            'industry': 'Startup',
            'company_size': 'Small',
            'status': 'Active'
        },
        {
            'name': 'FinanceFlow Inc',
            'email': 'info@financeflow.com',
            'industry': 'Fintech',
            'company_size': 'Large',
            'status': 'Active'
        }
    ]
    
    for client_data in sample_clients:
        analytics.add_client(client_data)
    
    # Add sample transactions
    sample_transactions = [
        {
            'client_id': analytics.clients[0].id,
            'service_type': 'Performance Audit',
            'amount': 150.00,
            'date': (datetime.now() - timedelta(days=15)).isoformat()
        },
        {
            'client_id': analytics.clients[1].id,
            'service_type': 'Optimization Implementation',
            'amount': 350.00,
            'date': (datetime.now() - timedelta(days=10)).isoformat()
        },
        {
            'client_id': analytics.clients[2].id,
            'service_type': 'Performance Monitoring',
            'amount': 100.00,
            'date': (datetime.now() - timedelta(days=5)).isoformat()
        }
    ]
    
    for trans_data in sample_transactions:
        analytics.add_transaction(trans_data)
    
    # Generate and display report
    print("\n📋 Generating comprehensive business report...")
    report = analytics.generate_business_report()
    print(report)
    
    # Export analytics
    filename = analytics.export_analytics()
    print(f"\n💾 Analytics exported to: {filename}")

if __name__ == "__main__":
    demo_usage()