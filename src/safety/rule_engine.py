from typing import List, Dict, Any

class SafetyRuleEngine:
    def __init__(self, thresholds: Dict[str, Any] = None):
        self.thresholds = thresholds or {}

    def _calculate_iou(self, box1, box2):
        # [x1, y1, x2, y2]
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        iou = intersection_area / float(box1_area + box2_area - intersection_area)
        return iou

    def evaluate(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate detections against safety rules and return violations.
        Rules:
        - FIRE -> CRITICAL
        - SMOKE -> HIGH
        - MOBILE PHONE -> LOW
        - Person without helmet -> NO HELMET (MEDIUM)
        - Person without vest -> NO VEST (MEDIUM)
        """
        violations = []
        
        persons = [d for d in detections if d['label'] == 'person']
        helmets = [d for d in detections if d['label'] == 'helmet']
        vests = [d for d in detections if d['label'] == 'vest']
        
        # Immediate environmental rules
        for d in detections:
            lbl = d['label']
            if lbl == 'fire':
                violations.append({'type': 'FIRE', 'severity': 'CRITICAL', 'message': 'Fire detected!', 'bbox': d['bbox']})
            elif lbl == 'smoke':
                violations.append({'type': 'SMOKE', 'severity': 'HIGH', 'message': 'Smoke detected!', 'bbox': d['bbox']})
            elif lbl == 'mobile-phone':
                violations.append({'type': 'MOBILE_PHONE', 'severity': 'LOW', 'message': 'Mobile phone usage detected', 'bbox': d['bbox']})
            elif lbl == 'no-helmet':
                violations.append({'type': 'NO_HELMET', 'severity': 'MEDIUM', 'message': 'No helmet detected', 'bbox': d['bbox']})
            elif lbl == 'no-vest':
                violations.append({'type': 'NO_VEST', 'severity': 'MEDIUM', 'message': 'No vest detected', 'bbox': d['bbox']})

        # Association rules (Person + Helmet/Vest)
        # If no-helmet and no-vest are already directly detected by YOLO, this logic is a fallback.
        for p in persons:
            p_box = p['bbox']
            
            # Check helmet association
            has_helmet = any(self._calculate_iou(p_box, h['bbox']) > 0.1 for h in helmets)
            # We assume no-helmet isn't directly output by YOLO for this person.
            # If the model ONLY outputs "person" and "helmet", we do this:
            if not has_helmet:
                # To prevent double alerting if model also outputs 'no-helmet' directly
                direct_no_helmet = any(self._calculate_iou(p_box, nh['bbox']) > 0.5 for nh in detections if nh['label'] == 'no-helmet')
                if not direct_no_helmet:
                    violations.append({'type': 'NO_HELMET', 'severity': 'MEDIUM', 'message': 'Person detected without helmet', 'bbox': p_box})

            has_vest = any(self._calculate_iou(p_box, v['bbox']) > 0.1 for v in vests)
            if not has_vest:
                direct_no_vest = any(self._calculate_iou(p_box, nv['bbox']) > 0.5 for nv in detections if nv['label'] == 'no-vest')
                if not direct_no_vest:
                    violations.append({'type': 'NO_VEST', 'severity': 'MEDIUM', 'message': 'Person detected without vest', 'bbox': p_box})

        return violations
