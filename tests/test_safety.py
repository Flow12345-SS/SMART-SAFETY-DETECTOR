import pytest
from src.safety.rule_engine import SafetyRuleEngine
from src.alerts.alert_manager import AlertManager
from src.database.db import get_db

def test_rule_engine_fire():
    engine = SafetyRuleEngine()
    detections = [{"label": "fire", "confidence": 0.9, "bbox": [0,0,10,10], "tracking_id": 1}]
    violations = engine.evaluate(detections)
    
    assert len(violations) == 1
    assert violations[0]['type'] == 'FIRE'
    assert violations[0]['severity'] == 'CRITICAL'

def test_rule_engine_person_no_helmet():
    engine = SafetyRuleEngine()
    # A person but no helmet
    detections = [{"label": "person", "confidence": 0.9, "bbox": [0,0,100,100], "tracking_id": 1}]
    violations = engine.evaluate(detections)
    
    # It should flag no helmet and no vest
    types = [v['type'] for v in violations]
    assert 'NO_HELMET' in types
    assert 'NO_VEST' in types

def test_alert_manager_cooldown():
    am = AlertManager(cooldown_seconds=10)
    violations = [{"type": "FIRE", "severity": "CRITICAL", "message": "Fire!"}]
    
    alerts1 = am.process_violations(violations)
    assert len(alerts1) == 1
    
    # Second immediate call should be suppressed by cooldown
    alerts2 = am.process_violations(violations)
    assert len(alerts2) == 0
