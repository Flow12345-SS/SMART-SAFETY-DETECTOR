import time
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, cooldown_seconds: int = 10):
        self.cooldown_seconds = cooldown_seconds
        # Stores the last time an alert was triggered for a specific type
        self.last_alerts = {}

    def process_violations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process incoming violations, apply cooldown, and return valid new alerts.
        """
        current_time = time.time()
        new_alerts = []

        for v in violations:
            alert_type = v['type']
            severity = v['severity']
            
            last_time = self.last_alerts.get(alert_type, 0)
            
            if (current_time - last_time) >= self.cooldown_seconds:
                alert = {
                    "type": alert_type,
                    "severity": severity,
                    "message": v['message'],
                    "timestamp": current_time,
                    "status": "NEW"
                }
                new_alerts.append(alert)
                self.last_alerts[alert_type] = current_time
                logger.info(f"ALERT TRIGGERED: {alert_type} ({severity}) - {v['message']}")

        return new_alerts
