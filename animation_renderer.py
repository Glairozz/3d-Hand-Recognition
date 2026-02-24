import cv2
import numpy as np
from typing import Tuple, List
import math
import random


class AnimationRenderer:
    def __init__(self):
        self.particles = []
        self.trail_particles = []

    def create_i_love_you_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)

        frame = self._draw_premium_ring(frame, cx, cy, intensity)
        frame = self._draw_neon_orbit(frame, cx, cy, intensity)
        frame = self._draw_premium_particles(frame, cx, cy, intensity)
        frame = self._draw_heart_burst(frame, cx, cy, intensity)
        frame = self._draw_premium_text(frame, "I LOVE YOU", w, h, intensity)
        frame = self._draw_aura(frame, cx, cy, intensity)

        return frame

    def _get_time(self):
        return cv2.getTickCount() / 600000

    def _draw_premium_ring(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = self._get_time()

        colors = [
            (255, 0, 150), (255, 50, 200), (255, 100, 255),
            (255, 150, 220), (255, 50, 150)
        ]

        for i in range(8):
            radius = 70 + i * 18 + 20 * math.sin(time * 2.5 + i)
            alpha = (1 - i / 10) * intensity
            color = colors[i % len(colors)]
            color = tuple(int(c * alpha) for c in color)
            cv2.circle(frame, (cx, cy), int(radius), color, 3)

            for angle in np.linspace(0, 2 * math.pi, 48):
                x = int(cx + radius * math.cos(angle + time * 1.5))
                y = int(cy + radius * math.sin(angle + time * 1.5))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 3, color, -1)

        return frame

    def _draw_neon_orbit(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = self._get_time()

        orbit_colors = [(0, 255, 255), (255, 0, 255), (0, 255, 200)]

        for i, orbit_color in enumerate(orbit_colors):
            for j in range(3):
                angle = time * (2 + i * 0.5) + j * (2 * math.pi / 3)
                radius = 90 + i * 25
                x = int(cx + radius * math.cos(angle))
                y = int(cy + radius * math.sin(angle) * 0.7)
                if 0 <= x < w and 0 <= y < h:
                    size = 6 + 3 * math.sin(time * 5 + i + j)
                    color = tuple(int(c * intensity) for c in orbit_color)
                    cv2.circle(frame, (x, y), int(size), color, -1)
                    cv2.circle(frame, (x, y), int(size + 4), color, 1)

        return frame

    def _draw_premium_particles(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = self._get_time()

        if len(self.particles) < 120:
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(4, 10)
                self.particles.append({
                    'x': cx,
                    'y': cy,
                    'vx': speed * math.cos(angle),
                    'vy': speed * math.sin(angle) - 3,
                    'life': 1.0,
                    'color': (
                        random.randint(200, 255),
                        random.randint(50, 150),
                        random.randint(100, 255)
                    ),
                    'size': random.randint(4, 10),
                    'decay': random.uniform(0.008, 0.02),
                    'trail': []
                })

        for p in self.particles[:]:
            p['trail'].append((int(p['x']), int(p['y'])))
            if len(p['trail']) > 12:
                p['trail'].pop(0)

            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.08
            p['life'] -= p['decay']

            if p['life'] <= 0 or p['y'] > h:
                self.particles.remove(p)
                continue

            if 0 <= int(p['x']) < w and 0 <= int(p['y']) < h:
                for j, (tx, ty) in enumerate(p['trail']):
                    if 0 <= tx < w and 0 <= ty < h:
                        alpha = (j / len(p['trail'])) * p['life'] * intensity
                        t_color = tuple(int(c * alpha * 0.6) for c in p['color'])
                        cv2.circle(frame, (tx, ty), max(1, int(p['size'] * 0.4)), t_color, -1)

                alpha = p['life'] * intensity
                color = tuple(int(c * alpha) for c in p['color'])
                cv2.circle(frame, (int(p['x']), int(p['y'])), 
                          int(p['size'] * p['life']), color, -1)
                cv2.circle(frame, (int(p['x']), int(p['y'])), 
                          int(p['size'] * p['life'] + 3), (255, 255, 255), 2)

        return frame

    def _draw_heart_burst(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = self._get_time()

        heart_colors = [
            (255, 0, 120), (255, 50, 180), (255, 100, 200),
            (255, 80, 150), (255, 120, 180)
        ]

        for i in range(18):
            angle = time * 1.2 + i * 0.5
            radius = 55 + i * 8 + 25 * math.sin(time * 2.5 + i)

            x = int(cx + radius * math.cos(angle))
            y = int(cy - 35 + radius * math.sin(angle) * 0.35 - (time * 45 + i * 18) % 140)

            if 0 <= x < w and 0 <= y < h:
                size = int((18 + 10 * math.sin(time * 5 + i * 0.4)) * intensity)
                color = heart_colors[i % len(heart_colors)]
                frame = self._draw_premium_heart(frame, x, y, size, color)

        return frame

    def _draw_premium_heart(self, frame, x, y, size, color):
        if size < 5:
            return frame

        points = []
        for t in np.linspace(0, 2 * math.pi, 35):
            hx = size * 13 * math.pow(math.sin(t), 3)
            hy = -size * (10 * math.cos(t) - 3 * math.cos(2*t) - 2 * math.cos(3*t))
            points.append((int(x + hx), int(y + hy)))

        pts = np.array(points, np.int32)

        for glow in range(10, 0, -2):
            alpha = 0.08 / (glow / 3)
            glow_color = tuple(min(255, int(c * (1 + alpha))) for c in color)
            cv2.polylines(frame, [pts], True, glow_color, glow + 2)

        cv2.fillPoly(frame, [pts], color)
        cv2.polylines(frame, [pts], True, (255, 255, 255), 2)

        center_x = x
        center_y = y
        cv2.circle(frame, (center_x, center_y), 3, (255, 255, 255), -1)

        return frame

    def _draw_premium_text(self, frame, text, w, h, intensity):
        time = self._get_time()

        scale = 2.2 + 0.6 * math.sin(time * 3)
        thickness = 6

        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX

        for layer in range(15, 0, -1):
            alpha = (0.06 / (layer / 4)) * intensity
            glow_r = min(255, int(255 * alpha * 1.2))
            glow_g = min(255, int(50 * alpha * 1.2))
            glow_b = min(255, int(200 * alpha * 1.2))
            glow = (glow_r, glow_g, glow_b)
            x = (w - 480) // 2 + layer
            y = h - 140 + layer
            cv2.putText(frame, text, (x, y), font, scale, glow, thickness + layer)

        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        x = (w - text_size[0]) // 2
        y = h - 140

        colors = [(255, 50, 150), (255, 100, 200), (255, 150, 220)]
        for i, color in enumerate(colors):
            color = tuple(int(c * intensity) for c in color)
            cv2.putText(frame, text, (x + i*2, y + i*2), font, scale, color, thickness)

        glow_layer = np.zeros_like(frame)
        cv2.putText(glow_layer, text, (x, y), font, scale, (255, 255, 255), thickness + 6)
        glow_layer = cv2.GaussianBlur(glow_layer, (25, 25), 0)
        frame = cv2.addWeighted(frame, 0.8, glow_layer, 0.2 * intensity, 0)

        subtext = "PEACE SIGN"
        sub_scale = 1.2
        sub_size = cv2.getTextSize(subtext, font, sub_scale, 3)[0]
        sub_glow = (int(220 * intensity), int(220 * intensity), int(220 * intensity))
        cv2.putText(frame, subtext, ((w - sub_size[0]) // 2, y + 90), 
                   font, sub_scale, sub_glow, 4)

        return frame

    def _draw_aura(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = self._get_time()

        for ring in range(4):
            r = 80 + ring * 35
            alpha = (1 - ring / 5) * 0.3 * intensity
            color = (int(255 * alpha), int(100 * alpha), int(180 * alpha))

            for angle in np.linspace(0, 2 * math.pi, 80):
                offset = 8 * math.sin(time * 6 + angle * 10 + ring)
                x = int(cx + (r + offset) * math.cos(angle + time))
                y = int(cy + (r + offset) * math.sin(angle + time))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 2, color, -1)

        return frame

    def create_open_hand_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)

        frame = self._draw_premium_ring(frame, cx, cy, intensity)
        frame = self._draw_wave_burst(frame, cx, cy, intensity)
        frame = self._draw_premium_particles(frame, cx, cy, intensity)
        frame = self._draw_premium_text(frame, "HI GUYS!", w, h, intensity)

        return frame

    def _draw_wave_burst(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = self._get_time()

        for i in range(10):
            phase = time * 4.5 + i * 1.2
            radius = 55 + i * 22 + 20 * math.sin(phase)
            alpha = (1 - i / 12) * intensity * 0.7
            color = (int(200 * alpha), int(255 * alpha), int(150 * alpha))
            cv2.circle(frame, (cx, cy), int(radius), color, 3)

            for a in np.linspace(0, 2 * math.pi, 16):
                x = int(cx + radius * math.cos(a + time * 3))
                y = int(cy + radius * math.sin(a + time * 3))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 6, color, -1)

        return frame

    def create_fist_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = self._get_time()

        for i in range(20):
            angle = i * math.pi / 10 + time * 5
            radius = 70 + 35 * math.sin(time * 6 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            if 0 <= x < w and 0 <= y < h:
                color = (255, int(200 - i * 8), int(50 + i * 5))
                color = tuple(int(c * intensity) for c in color)
                cv2.circle(frame, (x, y), int(12 * intensity), color, -1)

        for r in [45, 75, 105, 135]:
            radius = r + int(25 * math.sin(time * 7))
            alpha = (1 - r / 140) * intensity
            color = (int(255 * alpha), int(200 * alpha), int(50 * alpha))
            cv2.circle(frame, (cx, cy), radius, color, 4)

            for angle in np.linspace(0, 2 * math.pi, 12):
                x = int(cx + radius * math.cos(angle + time * 2.5))
                y = int(cy + radius * math.sin(angle + time * 2.5))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 5, color, -1)

        frame = self._draw_premium_text(frame, "Inday Sara On Top!", w, h, intensity)

        return frame

    def create_thumbs_up_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = self._get_time()

        for i in range(15):
            angle = time * 3 + i * 0.4
            radius = 60 + i * 6 + 20 * math.sin(time * 5 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy - 30 + radius * math.sin(angle) * 0.5)
            if 0 <= x < w and 0 <= y < h:
                alpha = (1 - i / 15) * intensity
                color = (int(80 * alpha), int(255 * alpha), int(180 * alpha))
                cv2.circle(frame, (x, y), int(8 * intensity), color, -1)

        for i in range(10):
            offset = int(70 * math.sin(time * 6 + i))
            x = cx - 60 + i * 13
            y = cy - 80 + offset
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(7 * intensity), (80, 255, 180), -1)

        frame = self._draw_premium_text(frame, "OK!", w, h, intensity)

        return frame

    def create_one_finger_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = self._get_time()

        for i in range(24):
            angle = time * 2.5 + i * 0.25
            radius = 50 + i * 4 + 22 * math.sin(time * 5 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle) * 0.35)
            if 0 <= x < w and 0 <= y < h:
                alpha = (1 - i / 24) * intensity
                color = (int(220 * alpha), int(120 * alpha), int(255 * alpha))
                cv2.circle(frame, (x, y), int(6 * intensity), color, -1)

        frame = self._draw_premium_ring(frame, cx, cy, intensity * 0.8)
        frame = self._draw_premium_text(frame, "SYEMPRE IKAW LANG!", w, h, intensity)

        return frame

    def create_glow_effect(self, frame, x, y, radius=80):
        h, w = frame.shape[:2]
        time = self._get_time()

        for r in range(radius, 0, -2):
            alpha = 1 - (r / radius)
            color = (int(255 * alpha * 0.6), int(150 * alpha * 0.6), int(200 * alpha * 0.6))
            cv2.circle(frame, (x, y), r, color, 2)

        return frame

    def clear_particles(self):
        self.particles = []
        self.trail_particles = []
