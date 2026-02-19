import cv2
import numpy as np
from typing import Tuple, List
import math


class AnimationRenderer:
    def __init__(self):
        self.particles = []
        self.heart_color = (0, 100, 255)
        self.text_color = (255, 100, 150)
        self.bg_color = (20, 20, 40)

    def create_i_love_you_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)

        frame = self._draw_heart_background(frame, cx, cy, intensity)
        frame = self._draw_floating_hearts(frame, cx, cy, intensity)
        frame = self._draw_particles(frame, cx, cy, intensity)
        frame = self._draw_text(frame, w, h, intensity)

        return frame

    def _draw_heart_background(
        self,
        frame: np.ndarray,
        cx: int,
        cy: int,
        intensity: float
    ) -> np.ndarray:
        h, w = frame.shape[:2]

        for angle in np.linspace(0, 2 * math.pi, 36):
            radius = 50 + 30 * math.sin(4 * angle + cv2.getTickCount() / 1000000)
            radius = int(radius * intensity)

            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))

            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), 2, self.heart_color, -1)

        return frame

    def _draw_floating_hearts(
        self,
        frame: np.ndarray,
        cx: int,
        cy: int,
        intensity: float
    ) -> np.ndarray:
        h, w = frame.shape[:2]

        time = cv2.getTickCount() / 1000000

        for i in range(8):
            angle = time + i * math.pi / 4
            radius = 80 + 20 * math.sin(time * 2 + i)

            x = int(cx + radius * math.cos(angle))
            y = int(cy - 50 + radius * math.sin(angle) * 0.3 - (time * 30 + i * 20) % 200)

            if 0 <= x < w and 0 <= y < h:
                size = int((8 + 4 * math.sin(time * 3 + i)) * intensity)
                frame = self._draw_heart(frame, x, y, size)

        return frame

    def _draw_heart(
        self,
        frame: np.ndarray,
        x: int,
        y: int,
        size: int
    ) -> np.ndarray:
        if size < 3:
            return frame

        h, w = frame.shape[:2]
        heart_points = []

        for t in np.linspace(0, 2 * math.pi, 30):
            hx = size * 16 * math.pow(math.sin(t), 3)
            hy = -size * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            heart_points.append((int(x + hx), int(y + hy)))

        pts = np.array(heart_points, np.int32)
        cv2.fillPoly(frame, [pts], self.heart_color)

        return frame

    def _draw_particles(
        self,
        frame: np.ndarray,
        cx: int,
        cy: int,
        intensity: float
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 1000000

        if len(self.particles) < 50:
            self.particles.append({
                'x': cx,
                'y': cy,
                'vx': np.random.uniform(-3, 3),
                'vy': np.random.uniform(-5, -1),
                'life': 1.0,
                'color': (
                    np.random.randint(200, 255),
                    np.random.randint(100, 200),
                    np.random.randint(150, 255)
                ),
                'size': np.random.randint(2, 6)
            })

        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['life'] -= 0.02

            if p['life'] <= 0 or p['y'] > h:
                self.particles.remove(p)
                continue

            if 0 <= int(p['x']) < w and 0 <= int(p['y']) < h:
                alpha = p['life'] * intensity
                color = tuple(int(c * alpha) for c in p['color'])
                cv2.circle(frame, (int(p['x']), int(p['y'])), int(p['size'] * p['life']), color, -1)

        return frame

    def _draw_text(
        self,
        frame: np.ndarray,
        w: int,
        h: int,
        intensity: float
    ) -> np.ndarray:
        time = cv2.getTickCount() / 1000000

        text = "I LOVE YOU"
        scale = 1.5 + 0.3 * math.sin(time * 2)
        thickness = 3

        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        x = (w - text_size[0]) // 2
        y = h - 80

        glow_size = thickness * 3
        for i in range(1, 4):
            alpha = 0.3 / i
            color = tuple(int(c * alpha) for c in self.text_color)
            cv2.putText(frame, text, (x + i, y + i), font, scale, color, glow_size)

        cv2.putText(frame, text, (x, y), font, scale, self.text_color, thickness)

        subtext = "Peace Sign Detected"
        sub_scale = 0.7
        sub_size = cv2.getTextSize(subtext, font, sub_scale, 2)[0]
        cv2.putText(frame, subtext, ((w - sub_size[0]) // 2, y + 50), font, sub_scale, (150, 150, 150), 2)

        return frame

    def create_peace_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)

        time = cv2.getTickCount() / 1000000

        for i in range(12):
            angle = time + i * math.pi / 6
            radius = 60 + 10 * math.sin(time * 3 + i)

            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))

            if 0 <= x < w and 0 <= y < h:
                size = int(3 * intensity)
                cv2.circle(frame, (x, y), size, (100, 200, 255), -1)

        return frame

    def create_glow_effect(
        self,
        frame: np.ndarray,
        x: int,
        y: int,
        radius: int = 50
    ) -> np.ndarray:
        h, w = frame.shape[:2]

        for r in range(radius, 0, -5):
            alpha = 1 - (r / radius)
            color = (int(255 * alpha), int(200 * alpha), int(100 * alpha))
            cv2.circle(frame, (x, y), r, color, 2)

        return frame

    def create_open_hand_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = cv2.getTickCount() / 1000000

        for i in range(5):
            offset_x = int(80 * math.cos(time * 2 + i * 1.2))
            offset_y = int(60 * math.sin(time * 2 + i * 1.2))
            x = cx + offset_x
            y = cy + offset_y - 50
            if 0 <= x < w and 0 <= y < h:
                size = int((15 + 5 * math.sin(time * 4 + i)) * intensity)
                cv2.putText(frame, "👋", (x - size//2, y + size//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, size/20, (255, 255, 255), 2)

        frame = self._draw_wave_effect(frame, cx, cy, intensity)
        frame = self._draw_hand_text(frame, "HI GUYS!", w, h, (100, 255, 255), intensity)

        return frame

    def _draw_wave_effect(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 1000000
        
        for i in range(8):
            angle = time * 2 + i * 0.8
            radius = 70 + i * 10
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle) * 0.5)
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(5 * intensity), (255, 200, 100), -1)
        return frame

    def create_fist_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = cv2.getTickCount() / 1000000

        for i in range(8):
            angle = i * math.pi / 4
            radius = 40 + 20 * math.sin(time * 5)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(6 * intensity), (255, 200, 0), -1)

        for r in [30, 50, 70]:
            radius = r + int(10 * math.sin(time * 4))
            cv2.circle(frame, (cx, cy), radius, (255, 150, 0), 2)

        frame = self._draw_hand_text(frame, "Inday Sara On Top!", w, h, (0, 200, 255), intensity)

        return frame

    def create_thumbs_up_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = cv2.getTickCount() / 1000000

        for i in range(6):
            offset = int(40 * math.sin(time * 3 + i))
            x = cx - 30 + i * 12
            y = cy - 50 + offset
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(4 * intensity), (0, 255, 100), -1)

        frame = self._draw_hand_text(frame, "OK!", w, h, (0, 255, 100), intensity)

        return frame

    def create_one_finger_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = cv2.getTickCount() / 1000000

        for i in range(12):
            angle = time * 2 + i * 0.5
            radius = 50 + i * 5
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle) * 0.3)
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(3 * intensity), (200, 100, 255), -1)

        frame = self._draw_hand_text(frame, "SYEMPRE IKAW LANG!", w, h, (200, 100, 255), intensity)

        return frame

    def _draw_hand_text(
        self,
        frame: np.ndarray,
        text: str,
        w: int,
        h: int,
        color: Tuple[int, int, int],
        intensity: float
    ) -> np.ndarray:
        time = cv2.getTickCount() / 1000000

        scale = 1.2 + 0.2 * math.sin(time * 2)
        thickness = 3

        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        x = (w - text_size[0]) // 2
        y = h - 80

        glow_size = thickness * 3
        for i in range(1, 4):
            alpha = 0.3 / i
            glow_color = tuple(int(c * alpha) for c in color)
            cv2.putText(frame, text, (x + i, y + i), font, scale, glow_color, glow_size)

        cv2.putText(frame, text, (x, y), font, scale, color, thickness)

        return frame

    def clear_particles(self):
        self.particles = []
