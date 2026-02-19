import numpy as np
from typing import List, Dict, Tuple, Optional


class GestureRecognizer:
    def __init__(self, confidence_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold
        self.gesture_history = []
        self.history_size = 8
        self.current_gesture = None

    def recognize(self, landmarks: List[Dict]) -> Optional[str]:
        if not landmarks or len(landmarks) < 21:
            return None

        if not all(lm is not None and 'x' in lm and 'y' in lm for lm in landmarks):
            return None

        fingers_extended = self._get_finger_states(landmarks)
        gesture = self._classify_gesture(fingers_extended, landmarks)

        self.gesture_history.append(gesture)
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)

        if self._is_stable_gesture(gesture):
            self.current_gesture = gesture
            return gesture

        return self.current_gesture

    def _get_finger_states(self, landmarks: List[Dict]) -> Dict[str, bool]:
        wrist = landmarks[0]
        index_mcp = landmarks[5]
        pinky_mcp = landmarks[17]
        hand_center_x = (index_mcp['x'] + pinky_mcp['x']) / 2

        fingers = {}

        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[1]
        thumb_extended = self._check_thumb(thumb_tip, thumb_ip, thumb_mcp, wrist, hand_center_x)
        fingers['thumb'] = thumb_extended

        for finger_name, tip_idx, pip_idx in [
            ('index', 8, 6), ('middle', 12, 10), ('ring', 16, 14), ('pinky', 20, 18)
        ]:
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            if tip is None or pip is None:
                fingers[finger_name] = False
            else:
                fingers[finger_name] = tip['y'] < pip['y'] - 0.01

        return fingers

    def _check_thumb(self, tip, ip, mcp, wrist, hand_center) -> bool:
        if tip is None or mcp is None or wrist is None:
            return False
        thumb_tip_x = tip['x']
        thumb_mcp_x = mcp['x']
        wrist_x = wrist['x']
        is_left_hand = wrist_x < hand_center
        if is_left_hand:
            return thumb_tip_x > thumb_mcp_x + 0.05
        else:
            return thumb_tip_x < thumb_mcp_x - 0.05

    def _classify_gesture(self, fingers: Dict[str, bool], landmarks: List[Dict]) -> Optional[str]:
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        index_pip = landmarks[6]
        middle_pip = landmarks[10]
        ring_pip = landmarks[14]
        pinky_pip = landmarks[18]

        fingers_vertical = {
            'index': index_tip['y'] < index_pip['y'] - 0.005,
            'middle': middle_tip['y'] < middle_pip['y'] - 0.005,
            'ring': ring_tip['y'] < ring_pip['y'] - 0.005,
            'pinky': pinky_tip['y'] < pinky_pip['y'] - 0.005
        }
        
        index_mcp = landmarks[5]
        middle_mcp = landmarks[9]
        ring_mcp = landmarks[13]
        pinky_mcp = landmarks[17]
        
        fingers_curled = {
            'index': index_tip['y'] > index_mcp['y'],
            'middle': middle_tip['y'] > middle_mcp['y'],
            'ring': ring_tip['y'] > ring_mcp['y'],
            'pinky': pinky_tip['y'] > pinky_mcp['y']
        }

        if (fingers_vertical['index'] and fingers_vertical['middle'] and 
            not fingers_vertical['ring'] and not fingers_vertical['pinky'] and fingers['thumb']):
            return "i_love_you"

        if (fingers_vertical['index'] and fingers_vertical['middle'] and 
            not fingers_vertical['ring'] and not fingers_vertical['pinky'] and not fingers['thumb']):
            return "peace"

        if (fingers_vertical['index'] and fingers_vertical['middle'] and 
            fingers_vertical['ring'] and fingers_vertical['pinky'] and fingers['thumb']):
            return "open_hand"

        if (fingers_vertical['index'] and fingers_vertical['middle'] and 
            fingers_vertical['ring'] and fingers_vertical['pinky'] and not fingers['thumb']):
            return "four"

        if (all(fingers_curled[k] for k in ['index', 'middle', 'ring', 'pinky']) and not fingers['thumb']):
            return "fist"

        if (all(fingers_curled[k] for k in ['index', 'middle', 'ring', 'pinky']) and fingers['thumb']):
            return "thumbs_up"

        if (fingers_vertical['index'] and not fingers_vertical['middle'] and 
            not fingers_vertical['ring'] and not fingers_vertical['pinky'] and not fingers['thumb']):
            return "one"

        if (fingers_vertical['index'] and fingers_vertical['middle'] and 
            not fingers_vertical['ring'] and not fingers_vertical['pinky'] and fingers['thumb']):
            return "two"

        return "unknown"

    def _is_stable_gesture(self, gesture: Optional[str]) -> bool:
        if gesture is None or gesture == "unknown":
            return False
        if len(self.gesture_history) < self.history_size:
            return False
        recent = self.gesture_history[-self.history_size:]
        return all(g == gesture for g in recent)

    def get_hand_position(self, landmarks: List[Dict]) -> Tuple[float, float]:
        wrist = landmarks[0]
        return wrist['x'], wrist['y']

    def get_palm_center(self, landmarks: List[Dict]) -> Tuple[float, float]:
        palm_points = [0, 1, 5, 9, 13, 17]
        avg_x = sum(landmarks[i]['x'] for i in palm_points) / len(palm_points)
        avg_y = sum(landmarks[i]['y'] for i in palm_points) / len(palm_points)
        return avg_x, avg_y
