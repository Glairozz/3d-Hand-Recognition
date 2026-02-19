import cv2
import numpy as np
from typing import Tuple, List
import math
import random


class AnimationRenderer:
    def __init__(self):
        self.particles = []
        self.sparkles = []
        self.rings = []
        self.trails = []

    def create_i_love_you_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)

        frame = self._draw_rainbow_ring(frame, cx, cy, intensity)
        frame = self._draw_floating_hearts_enhanced(frame, cx, cy, intensity)
        frame = self._draw_sparkles(frame, cx, cy, intensity, color=(255, 100, 150))
        frame = self._draw_particles_enhanced(frame, cx, cy, intensity)
        frame = self._draw_glowing_text(frame, "I LOVE YOU", w, h, 
                                        gradient_colors=[(255, 0, 100), (255, 100, 200), (255, 50, 150)], 
                                        intensity=intensity, glow_color=(255, 0, 150))
        frame = self._draw_heart_outline(frame, cx, cy, int(80 * intensity))

        return frame

    def _draw_rainbow_ring(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 1000000
        
        colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (148, 0, 211)
        ]
        
        for i, color in enumerate(colors):
            angle_offset = time * 2 + i * 0.5
            radius = 70 + 15 * math.sin(time * 3 + i)
            
            for a in np.linspace(0, 2 * math.pi, 20):
                x = int(cx + radius * math.cos(a + angle_offset))
                y = int(cy + radius * math.sin(a + angle_offset))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 3, color, -1)
        
        return frame

    def _draw_floating_hearts_enhanced(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 1000000

        heart_colors = [
            (255, 100, 150), (255, 50, 100), (255, 0, 100),
            (255, 150, 180), (255, 80, 130)
        ]

        for i in range(12):
            angle = time * 1.5 + i * 0.8
            base_radius = 60 + i * 12
            radius = base_radius + 20 * math.sin(time * 2 + i)
            
            x = int(cx + radius * math.cos(angle))
            y = int(cy - 40 + radius * math.sin(angle) * 0.4 - (time * 40 + i * 25) % 180)

            if 0 <= x < w and 0 <= y < h:
                size = int((12 + 6 * math.sin(time * 4 + i * 0.5)) * intensity)
                color = heart_colors[i % len(heart_colors)]
                frame = self._draw_heart(frame, x, y, size, color)

        return frame

    def _draw_heart(self, frame, x, y, size, color):
        if size < 3:
            return frame

        heart_points = []
        for t in np.linspace(0, 2 * math.pi, 25):
            hx = size * 15 * math.pow(math.sin(t), 3)
            hy = -size * (12 * math.cos(t) - 4 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            heart_points.append((int(x + hx), int(y + hy)))

        pts = np.array(heart_points, np.int32)
        cv2.fillPoly(frame, [pts], color)
        
        cv2.polylines(frame, [pts], True, (255, 255, 255), 1)

        return frame

    def _draw_sparkles(self, frame, cx, cy, intensity, color):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 1000000

        for i in range(20):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(40, 120)
            x = int(cx + radius * math.cos(angle + time))
            y = int(cy + radius * math.sin(angle + time) * 0.6)
            
            if 0 <= x < w and 0 <= y < h:
                size = random.randint(1, 3)
                alpha = random.uniform(0.5, 1.0) * intensity
                sparkle_color = tuple(int(c * alpha) for c in color)
                cv2.circle(frame, (x, y), size, sparkle_color, -1)

        return frame

    def _draw_particles_enhanced(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 1000000

        if len(self.particles) < 80:
            for _ in range(3):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 6)
                self.particles.append({
                    'x': cx,
                    'y': cy,
                    'vx': speed * math.cos(angle),
                    'vy': speed * math.sin(angle) - 3,
                    'life': 1.0,
                    'color': (
                        random.randint(200, 255),
                        random.randint(50, 150),
                        random.randint(100, 200)
                    ),
                    'size': random.randint(3, 8),
                    'decay': random.uniform(0.015, 0.03)
                })

        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.15
            p['life'] -= p['decay']

            if p['life'] <= 0 or p['y'] > h:
                self.particles.remove(p)
                continue

            if 0 <= int(p['x']) < w and 0 <= int(p['y']) < h:
                alpha = p['life'] * intensity
                color = tuple(int(c * alpha) for c in p['color'])
                cv2.circle(frame, (int(p['x']), int(p['y'])), 
                          int(p['size'] * p['life']), color, -1)

        return frame

    def _draw_glowing_text(self, frame, text, w, h, gradient_colors, intensity, glow_color):
        time = cv2.getTickCount() / 1000000

        scale = 1.8 + 0.4 * math.sin(time * 2.5)
        thickness = 4

        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        
        for layer in range(8, 0, -2):
            alpha = (0.15 / (layer / 2)) * intensity
            glow_col = tuple(int(c * alpha) for c in glow_color)
            x = (w - 400) // 2
            y = h - 100
            cv2.putText(frame, text, (x + layer, y + layer), font, scale, glow_col, thickness + layer)

        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        x = (w - text_size[0]) // 2
        y = h - 100

        colors = gradient_colors
        for i, color in enumerate(colors):
            color = tuple(int(c * intensity) for c in color)
            cv2.putText(frame, text, (x + i, y + i), font, scale, color, thickness)

        subtext = "Peace Sign"
        sub_scale = 0.9
        sub_size = cv2.getTextSize(subtext, font, sub_scale, 2)[0]
        cv2.putText(frame, subtext, ((w - sub_size[0]) // 2, y + 60), 
                   font, sub_scale, (200, 200, 200), 2)

        return frame

    def _draw_heart_outline(self, frame, cx, cy, radius):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 1000000

        heart_points = []
        for t in np.linspace(0, 2 * math.pi, 40):
            scale = radius / 20
            hx = scale * 16 * math.pow(math.sin(t), 3)
            hy = -scale * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            heart_points.append((int(cx + hx), int(cy + hy)))

        pts = np.array(heart_points, np.int32)
        
        for thickness in [3, 2, 1]:
            alpha = 0.3 + 0.2 * (3 - thickness)
            color = (int(255 * alpha), int(100 * alpha), int(200 * alpha))
            cv2.polylines(frame, [pts], True, color, thickness)

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

        frame = self._draw_wave_rings(frame, cx, cy, intensity)
        frame = self._draw_sparkles(frame, cx, cy, intensity, color=(100, 255, 255))
        
        for i in range(5):
            offset_x = int(100 * math.cos(time * 2.5 + i * 1.2))
            offset_y = int(80 * math.sin(time * 2.5 + i * 1.2))
            x = cx + offset_x
            y = cy + offset_y - 60
            if 0 <= x < w and 0 <= y < h:
                size = int((20 + 8 * math.sin(time * 5 + i)) * intensity)
                cv2.putText(frame, "👋", (x - size//2, y + size//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, size/25, (255, 255, 200), 3)

        frame = self._draw_glowing_text(frame, "HI GUYS!", w, h,
                                        gradient_colors=[(100, 255, 255), (255, 255, 100), (255, 200, 100)],
                                        intensity=intensity, glow_color=(255, 200, 100))

        return frame

    def _draw_wave_rings(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 1000000

        for i in range(5):
            phase = time * 3 + i * 1.2
            radius = 40 + i * 25 + 15 * math.sin(phase)
            alpha = (1 - i / 5) * intensity * 0.6
            color = (int(255 * alpha), int(220 * alpha), int(100 * alpha))
            cv2.circle(frame, (cx, cy), int(radius), color, 2)

            for a in np.linspace(0, 2 * math.pi, 8):
                x = int(cx + radius * math.cos(a + time * 2))
                y = int(cy + radius * math.sin(a + time * 2))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 4, color, -1)

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

        for i in range(12):
            angle = i * math.pi / 6 + time * 3
            radius = 50 + 25 * math.sin(time * 4 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(8 * intensity), (255, 180, 0), -1)

        for r in [35, 55, 75, 95]:
            radius = r + int(15 * math.sin(time * 5))
            alpha = (1 - r / 100) * intensity
            color = (int(255 * alpha), int(180 * alpha), int(0 * alpha))
            cv2.circle(frame, (cx, cy), radius, color, 3)

        frame = self._draw_glowing_text(frame, "Inday Sara On Top!", w, h,
                                        gradient_colors=[(255, 200, 0), (255, 150, 50), (255, 100, 0)],
                                        intensity=intensity, glow_color=(255, 150, 0))

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

        for i in range(10):
            angle = time * 2 + i * 0.6
            radius = 50 + i * 8
            x = int(cx + radius * math.cos(angle))
            y = int(cy - 30 + radius * math.sin(angle) * 0.5)
            if 0 <= x < w and 0 <= y < h:
                alpha = (1 - i / 10) * intensity
                color = (int(50 * alpha), int(255 * alpha), int(100 * alpha))
                cv2.circle(frame, (x, y), int(6 * intensity), color, -1)

        for i in range(6):
            offset = int(50 * math.sin(time * 4 + i))
            x = cx - 40 + i * 16
            y = cy - 60 + offset
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(5 * intensity), (0, 255, 150), -1)

        frame = self._draw_glowing_text(frame, "OK!", w, h,
                                        gradient_colors=[(50, 255, 150), (100, 255, 200), (150, 255, 100)],
                                        intensity=intensity, glow_color=(0, 255, 100))

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

        for i in range(16):
            angle = time * 2 + i * 0.4
            radius = 40 + i * 6 + 15 * math.sin(time * 3 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle) * 0.4)
            if 0 <= x < w and 0 <= y < h:
                alpha = (1 - i / 16) * intensity
                color = (int(200 * alpha), int(80 * alpha), int(255 * alpha))
                cv2.circle(frame, (x, y), int(4 * intensity), color, -1)

        frame = self._draw_sparkles(frame, cx, cy, intensity, color=(200, 100, 255))
        
        frame = self._draw_glowing_text(frame, "SYEMPRE IKAW LANG!", w, h,
                                        gradient_colors=[(200, 100, 255), (255, 150, 200), (255, 100, 200)],
                                        intensity=intensity, glow_color=(200, 50, 255))

        return frame

    def create_glow_effect(self, frame, x, y, radius=60):
        h, w = frame.shape[:2]
        
        for r in range(radius, 0, -3):
            alpha = 1 - (r / radius)
            color = (int(255 * alpha * 0.5), int(200 * alpha * 0.5), int(100 * alpha * 0.5))
            cv2.circle(frame, (x, y), r, color, 2)

        return frame

    def clear_particles(self):
        self.particles = []
        self.sparkles = []
        self.rings = []
        self.trails = []
