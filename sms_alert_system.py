"""
📱 FEATURE 9: Free SMS Alert System
- Sends alerts using free-tier Twilio API (or open-source alternative)
- Triggers based on ML-detected risk thresholds
- Respects user preferences and frequency
- Free & Open Source compatible
"""

import json
import pandas as pd
from datetime import datetime, timedelta

class SMSAlertSystem:
    """
    Manages SMS alerts for critical health situations
    """
    
    def __init__(self, use_free_tier=True):
        """
        Initialize SMS alert system
        
        Args:
            use_free_tier (bool): Use only free APIs/services
        """
        self.use_free_tier = use_free_tier
        self.alert_log = []
        self.user_preferences = {}
        self.rate_limit = {
            'max_alerts_per_day': 5,
            'min_hours_between_alerts': 2
        }
        
        if use_free_tier:
            print("✅ SMS Alert System configured for FREE services only")
            print("   Recommended: Twilio Free Tier (limited to verified numbers)")
            print("   Alternative: Open-source SMS gateways (requires setup)")
    
    def register_user(self, user_id, phone_number, alert_preferences=None):
        """
        Register user for SMS alerts
        
        Args:
            user_id (str): User identifier
            phone_number (str): Phone number (must be verified)
            alert_preferences (dict): {alert_level, frequency, opt_in}
        """
        self.user_preferences[user_id] = {
            'phone': phone_number,
            'alert_level': alert_preferences.get('alert_level', 'HIGH') if alert_preferences else 'HIGH',
            'frequency': alert_preferences.get('frequency', 'IMMEDIATE') if alert_preferences else 'IMMEDIATE',
            'opt_in': alert_preferences.get('opt_in', True) if alert_preferences else True,
            'registered_date': datetime.now().isoformat(),
            'last_alert_time': None
        }
        return {'status': 'success', 'message': f'User {user_id} registered for SMS alerts'}
    
    def check_rate_limit(self, user_id):
        """
        Check if user has exceeded alert rate limit
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if within limits, False otherwise
        """
        user_alerts = [a for a in self.alert_log if a['user_id'] == user_id]
        today_alerts = [a for a in user_alerts if pd.to_datetime(a['timestamp']).date() == datetime.now().date()]
        
        if len(today_alerts) >= self.rate_limit['max_alerts_per_day']:
            return False
        
        if user_alerts:
            last_alert_time = pd.to_datetime(user_alerts[-1]['timestamp'])
            hours_since = (datetime.now() - last_alert_time).total_seconds() / 3600
            if hours_since < self.rate_limit['min_hours_between_alerts']:
                return False
        
        return True
    
    def generate_alert_message(self, alert_type, severity, details):
        """
        Generate SMS-friendly alert message (160 chars for optimal delivery)
        
        Args:
            alert_type (str): 'DISEASE_OUTBREAK', 'WATER_CONTAMINATION', 'CRITICAL_RISK'
            severity (str): 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
            details (dict): Alert details
            
        Returns:
            str: SMS message (≤160 chars)
        """
        messages = {
            'DISEASE_OUTBREAK': {
                'CRITICAL': f"🚨 CRITICAL OUTBREAK ALERT in {details.get('region', 'your area')}. Seek medical care immediately. Cases: {details.get('cases', 'N/A')}",
                'HIGH': f"⚠️ HIGH outbreak risk in {details.get('region', 'your area')}. Limit water contact. Report symptoms.",
                'MEDIUM': f"📢 Elevated outbreak risk in {details.get('region', 'your area')}. Stay informed.",
            },
            'WATER_CONTAMINATION': {
                'CRITICAL': f"🚨 CRITICAL: Water contaminated in {details.get('region', 'your area')}. Do NOT drink. Use bottled water.",
                'HIGH': f"⚠️ High contamination risk. Boil water before use in {details.get('region', 'your area')}.",
                'MEDIUM': f"📢 Water quality issue in {details.get('region', 'your area')}. Monitor situation.",
            },
            'CRITICAL_RISK': {
                'CRITICAL': f"🚨 CRITICAL HEALTH RISK in {details.get('region', 'your area')}. Contact health authorities.",
                'HIGH': f"⚠️ HIGH health risk. Take precautions in {details.get('region', 'your area')}.",
            }
        }
        
        message = messages.get(alert_type, {}).get(severity, "Health Alert: Check your dashboard for details.")
        
        # Ensure SMS-friendly length
        return message[:160]
    
    def send_alert(self, user_id, alert_type, severity, details):
        """
        Send SMS alert to user (simulated for free tier)
        
        Args:
            user_id (str): User identifier
            alert_type (str): Type of alert
            severity (str): Alert severity
            details (dict): Alert details
            
        Returns:
            dict: Send result
        """
        # Check if user exists and opted in
        if user_id not in self.user_preferences:
            return {'status': 'failed', 'reason': 'User not registered'}
        
        user = self.user_preferences[user_id]
        if not user['opt_in']:
            return {'status': 'skipped', 'reason': 'User opted out'}
        
        # Check rate limits
        if not self.check_rate_limit(user_id):
            return {'status': 'rate_limited', 'reason': 'Alert frequency limit exceeded'}
        
        # Check severity threshold
        severity_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        user_threshold = severity_levels.get(user['alert_level'], 3)
        alert_severity = severity_levels.get(severity, 2)
        
        if alert_severity < user_threshold:
            return {'status': 'filtered', 'reason': f'Severity below user threshold ({user["alert_level"]})'}
        
        # Generate message
        message = self.generate_alert_message(alert_type, severity, details)
        
        # Log alert
        alert_record = {
            'user_id': user_id,
            'phone': user['phone'],
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status': 'sent (simulated)'
        }
        self.alert_log.append(alert_record)
        
        # Update last alert time
        self.user_preferences[user_id]['last_alert_time'] = datetime.now().isoformat()
        
        print(f"📱 SMS Alert Sent to {user_id}:")
        print(f"   To: {user['phone']}")
        print(f"   Message: {message}")
        print(f"   Status: FREE TIER (Simulated)")
        
        return {
            'status': 'sent',
            'message': message,
            'user_id': user_id,
            'phone': user['phone'][-4:] + '****',  # Mask phone number
            'timestamp': alert_record['timestamp']
        }
    
    def send_batch_alerts(self, alerts_list):
        """
        Send multiple alerts
        
        Args:
            alerts_list (list): List of {user_id, alert_type, severity, details}
            
        Returns:
            dict: Batch send results
        """
        results = []
        for alert in alerts_list:
            result = self.send_alert(
                alert['user_id'],
                alert['alert_type'],
                alert['severity'],
                alert['details']
            )
            results.append(result)
        
        return {
            'total_alerts': len(alerts_list),
            'sent': sum(1 for r in results if r['status'] == 'sent'),
            'failed': sum(1 for r in results if r['status'] == 'failed'),
            'rate_limited': sum(1 for r in results if r['status'] == 'rate_limited'),
            'results': results
        }
    
    def get_alert_history(self, user_id=None):
        """
        Get alert history
        
        Args:
            user_id (str): Optional user filter
            
        Returns:
            list: Alert history
        """
        if user_id:
            return [a for a in self.alert_log if a['user_id'] == user_id]
        return self.alert_log
    
    def get_setup_instructions(self):
        """Get setup instructions for free SMS services"""
        return {
            'free_options': [
                {
                    'service': 'Twilio Free Tier',
                    'cost': 'Free (Limited)',
                    'max_numbers': 'Only verified numbers',
                    'setup': 'Sign up at twilio.com, verify receiver number',
                    'code_example': 'pip install twilio\nfrom twilio.rest import Client'
                },
                {
                    'service': 'AWS SNS Free Tier',
                    'cost': 'Free (Limited)',
                    'max_messages': '100 SMS/month free',
                    'setup': 'AWS account + SNS setup',
                    'code_example': 'pip install boto3\nimport boto3'
                },
                {
                    'service': 'Open-source Kannel',
                    'cost': 'Free/Self-hosted',
                    'requirement': 'SMPP gateway account',
                    'setup': 'Self-hosted gateway',
                    'note': 'Requires additional infrastructure'
                }
            ],
            'recommendation': 'For MVP: Use Twilio free tier (verified numbers only). For production: AWS SNS or self-hosted Kannel'
        }


# Example usage
if __name__ == "__main__":
    sms_system = SMSAlertSystem(use_free_tier=True)
    
    # Register users
    print("\n📝 Registering users:")
    print(sms_system.register_user('user_001', '+1234567890', {'alert_level': 'HIGH'}))
    print(sms_system.register_user('user_002', '+0987654321', {'alert_level': 'CRITICAL'}))
    
    # Send alerts
    print("\n📱 Sending alerts:")
    result1 = sms_system.send_alert('user_001', 'DISEASE_OUTBREAK', 'HIGH', {'region': 'Region_A', 'cases': 85})
    print(json.dumps(result1, indent=2))
    
    result2 = sms_system.send_alert('user_002', 'WATER_CONTAMINATION', 'CRITICAL', {'region': 'Region_C'})
    print(json.dumps(result2, indent=2))
    
    # Show setup instructions
    print("\n💡 Free SMS Setup Options:")
    setup = sms_system.get_setup_instructions()
    print(json.dumps(setup, indent=2))