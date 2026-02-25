import cv2
import numpy as np
from typing import Tuple, List
import math
import random


class AnimationRenderer:
    def __init__(self):
        self.particles = []
        self.trail_particles = []
        self.smooth_time = 0.0
        self.prev_hand_pos = (0.5, 0.5)
        self.smooth_hand_pos = (0.5, 0.5)
        self.velocity_x = 0.0
        self.velocity_y = 0.0

    def _get_time(self):
        return cv2.getTickCount() / 2000000.0

    def _smooth_hand_position(self, hand_pos, smooth_factor=0.08):
        dx = hand_pos[0] - self.smooth_hand_pos[0]
        dy = hand_pos[1] - self.smooth_hand_pos[1]
        
        self.velocity_x = self.velocity_x * 0.7 + dx * 0.3
        self.velocity_y = self.velocity_y * 0.7 + dy * 0.3
        
        self.smooth_hand_pos = (
            self.smooth_hand_pos[0] + self.velocity_x * smooth_factor,
            self.smooth_hand_pos[1] + self.velocity_y * smooth_factor
        )
        return self.smooth_hand_pos

    def _lerp(self, a, b, t):
        return a + (b - a) * t

    def create_i_love_you_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        
        smooth_pos = self._smooth_hand_position(hand_pos)
        cx, cy = int(smooth_pos[0] * w), int(smooth_pos[1] * h)

        frame = self._draw_elegant_ring(frame, cx, cy, intensity)
        frame = self._draw_elegant_orbit(frame, cx, cy, intensity)
        frame = self._draw_elegant_particles(frame, cx, cy, intensity)
        frame = self._draw_elegant_hearts(frame, cx, cy, intensity)
        frame = self._draw_elegant_text(frame, "I LOVE YOU", w, h, intensity)
        frame = self._draw_elegant_aura(frame, cx, cy, intensity)

        return frame

    def _draw_elegant_ring(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        t = self._get_time()

        colors = [
            (255, 80, 190), (255, 120, 210), (255, 160, 230),
            (255, 100, 200), (255, 140, 220)
        ]

        for i in range(5):
            phase = t * 0.8 + i * 0.5
            radius = 80 + i * 18 + 12 * math.sin(phase)
            alpha = (0.7 - i * 0.12) * intensity
            color = tuple(int(c * alpha) for c in colors[i % len(colors)])
            cv2.circle(frame, (cx, cy), int(radius), color, 2)

            num_dots = 20 + i * 4
            for j in range(num_dots):
                angle = (j / num_dots) * 2 * math.pi + t * (0.5 + i * 0.08)
                x = int(cx + radius * math.cos(angle))
                y = int(cy + radius * math.sin(angle))
                if 0 <= x < w and 0 <= y < h:
                    size = 2 + int(1.5 * math.sin(phase + j * 0.25))
                    cv2.circle(frame, (x, y), size, color, -1)

        return frame

    def _draw_elegant_orbit(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        t = self._get_time()

        orbit_colors = [(0, 255, 255), (255, 0, 255), (150, 255, 100)]

        for i, orbit_color in enumerate(orbit_colors):
            for j in range(3):
                angle = t * (1.0 + i * 0.2) + j * (2 * math.pi / 3)
                radius = 90 + i * 22
                x = int(cx + radius * math.cos(angle))
                y = int(cy + radius * math.sin(angle) * 0.5)
                if 0 <= x < w and 0 <= y < h:
                    size = 4 + 1.5 * math.sin(t * 3 + i + j)
                    color = tuple(int(c * intensity) for c in orbit_color)
                    cv2.circle(frame, (x, y), int(size), color, -1)

        return frame

    def _draw_elegant_particles(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        t = self._get_time()

        if len(self.particles) < 60:
            for _ in range(2):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1.5, 4)
                self.particles.append({
                    'x': cx,
                    'y': cy,
                    'vx': speed * math.cos(angle),
                    'vy': speed * math.sin(angle) - 1.0,
                    'life': 1.0,
                    'color': (
                        random.randint(230, 255),
                        random.randint(100, 160),
                        random.randint(140, 200)
                    ),
                    'size': random.randint(3, 6),
                    'decay': random.uniform(0.012, 0.02),
                    'trail': []
                })

        for p in self.particles[:]:
            p['trail'].append((int(p['x']), int(p['y'])))
            if len(p['trail']) > 20:
                p['trail'].pop(0)

            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.03
            p['life'] -= p['decay']

            if p['life'] <= 0 or p['y'] > h:
                self.particles.remove(p)
                continue

            if 0 <= int(p['x']) < w and 0 <= int(p['y']) < h:
                for idx, (tx, ty) in enumerate(p['trail']):
                    if 0 <= tx < w and 0 <= ty < h:
                        alpha = (idx / len(p['trail'])) * p['life'] * intensity * 0.6
                        t_color = tuple(int(c * alpha) for c in p['color'])
                        cv2.circle(frame, (tx, ty), max(1, int(p['size'] * 0.4)), t_color, -1)

                alpha = p['life'] * intensity
                color = tuple(int(c * alpha) for c in p['color'])
                cv2.circle(frame, (int(p['x']), int(p['y'])), 
                          int(p['size'] * p['life']), color, -1)

        return frame

    def _draw_elegant_hearts(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        t = self._get_time()

        heart_colors = [(255, 60, 160), (255, 100, 190), (255, 80, 175)]

        for i in range(12):
            phase = t * 0.7 + i * 0.4
            radius = 55 + i * 6 + 15 * math.sin(phase)
            angle = phase * 0.4

            x = int(cx + radius * math.cos(angle))
            y_pos = int(cy - 25 + radius * math.sin(angle) * 0.2 - (t * 28 + i * 12) % 100)

            if 0 <= x < w and 0 <= y_pos < h:
                size = int((12 + 6 * math.sin(phase + i * 0.15)) * intensity)
                color = heart_colors[i % len(heart_colors)]
                frame = self._draw_elegant_heart(frame, x, y_pos, size, color)

        return frame

    def _draw_elegant_heart(self, frame, x, y, size, color):
        if size < 3:
            return frame

        points = []
        for angle in np.linspace(0, 2 * math.pi, 25):
            hx = size * 10 * math.pow(math.sin(angle), 3)
            hy = -size * (8 * math.cos(angle) - 2 * math.cos(2*angle) - 1.2 * math.cos(3*angle))
            points.append((int(x + hx), int(y + hy)))

        pts = np.array(points, np.int32)

        for glow in [5, 3, 1]:
            alpha = 0.2 / (glow + 0.5)
            glow_color = tuple(min(255, int(c * (1 + alpha))) for c in color)
            cv2.polylines(frame, [pts], True, glow_color, glow)

        cv2.fillPoly(frame, [pts], color)

        return frame

    def _draw_elegant_text(self, frame, text, w, h, intensity):
        t = self._get_time()

        scale = 1.8 + 0.2 * math.sin(t * 2)
        thickness = 4

        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX

        for layer in range(8, 0, -1):
            alpha = (0.1 / (layer / 2)) * intensity
            glow = (
                min(255, int(255 * alpha * 1.5)),
                min(255, int(100 * alpha * 1.5)),
                min(255, int(190 * alpha * 1.5))
            )
            x = (w - 400) // 2 + layer
            y = h - 160 + layer
            cv2.putText(frame, text, (x, y), font, scale, glow, thickness + layer)

        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        x = (w - text_size[0]) // 2
        y = h - 160

        colors = [(255, 70, 170), (255, 120, 200), (255, 150, 210)]
        for i, color in enumerate(colors):
            color = tuple(int(c * intensity) for c in color)
            cv2.putText(frame, text, (x + i, y + i), font, scale, color, thickness)

        glow_layer = np.zeros_like(frame)
        cv2.putText(glow_layer, text, (x, y), font, scale, (255, 255, 255), thickness + 3)
        glow_layer = cv2.GaussianBlur(glow_layer, (11, 11), 0)
        frame = cv2.addWeighted(frame, 0.88, glow_layer, 0.12 * intensity, 0)

        subtext = "PEACE SIGN"
        sub_scale = 0.9
        sub_size = cv2.getTextSize(subtext, font, sub_scale, 2)[0]
        sub_glow = (int(180 * intensity), int(180 * intensity), int(180 * intensity))
        cv2.putText(frame, subtext, ((w - sub_size[0]) // 2, y + 70), 
                   font, sub_scale, sub_glow, 2)

        return frame

    def _draw_elegant_aura(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        t = self._get_time()

        for ring in range(3):
            r = 95 + ring * 28
            alpha = (0.6 - ring * 0.18) * 0.2 * intensity
            color = (int(255 * alpha), int(130 * alpha), int(180 * alpha))

            for angle in np.linspace(0, 2 * math.pi, 50, endpoint=False):
                offset = 5 * math.sin(t * 3 + angle * 6 + ring)
                x = int(cx + (r + offset) * math.cos(angle + t * 0.4))
                y = int(cy + (r + offset) * math.sin(angle + t * 0.4))
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
        
        smooth_pos = self._smooth_hand_position(hand_pos)
        cx, cy = int(smooth_pos[0] * w), int(smooth_pos[1] * h)

        frame = self._draw_elegant_ring(frame, cx, cy, intensity)
        frame = self._draw_elegant_wave(frame, cx, cy, intensity)
        frame = self._draw_elegant_particles(frame, cx, cy, intensity)
        frame = self._draw_elegant_text(frame, "HI GUYS!", w, h, intensity)

        return frame

    def _draw_elegant_wave(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        t = self._get_time()

        for i in range(6):
            phase = t * 2 + i * 0.9
            radius = 65 + i * 16 + 10 * math.sin(phase)
            alpha = (0.65 - i * 0.1) * intensity * 0.5
            color = (int(200 * alpha), int(255 * alpha), int(160 * alpha))
            cv2.circle(frame, (cx, cy), int(radius), color, 2)

            num_dots = 10 + i * 2
            for j in range(num_dots):
                angle = (j / num_dots) * 2 * math.pi + t * 1.5
                x = int(cx + radius * math.cos(angle))
                y = int(cy + radius * math.sin(angle))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 3, color, -1)

        return frame

    def create_fist_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        
        smooth_pos = self._smooth_hand_position(hand_pos)
        cx, cy = int(smooth_pos[0] * w), int(smooth_pos[1] * h)
        t = self._get_time()

        for i in range(12):
            angle = i * math.pi / 6 + t * 2
            radius = 60 + 20 * math.sin(t * 3 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            if 0 <= x < w and 0 <= y < h:
                color = (255, int(230 - i * 12), int(90 + i * 10))
                color = tuple(int(c * intensity) for c in color)
                cv2.circle(frame, (x, y), int(8 * intensity), color, -1)

        for r in [35, 55, 75, 95]:
            radius = r + int(15 * math.sin(t * 4))
            alpha = (1 - r / 100) * intensity * 0.7
            color = (int(255 * alpha), int(210 * alpha), int(70 * alpha))
            cv2.circle(frame, (cx, cy), radius, color, 2)

            for angle in np.linspace(0, 2 * math.pi, 8, endpoint=False):
                x = int(cx + radius * math.cos(angle + t * 1.5))
                y = int(cy + radius * math.sin(angle + t * 1.5))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 3, color, -1)

        frame = self._draw_elegant_text(frame, "Inday Sara On Top!", w, h, intensity)

        return frame

    def create_thumbs_up_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        
        smooth_pos = self._smooth_hand_position(hand_pos)
        cx, cy = int(smooth_pos[0] * w), int(smooth_pos[1] * h)
        t = self._get_time()

        for i in range(10):
            angle = t * 1.5 + i * 0.4
            radius = 50 + i * 5 + 12 * math.sin(t * 3 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy - 20 + radius * math.sin(angle) * 0.35)
            if 0 <= x < w and 0 <= y < h:
                alpha = (0.85 - i * 0.07) * intensity
                color = (int(110 * alpha), int(255 * alpha), int(180 * alpha))
                cv2.circle(frame, (x, y), int(6 * intensity), color, -1)

        for i in range(6):
            offset = int(45 * math.sin(t * 4 + i))
            x = cx - 35 + i * 10
            y = cy - 55 + offset
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(5 * intensity), (110, 255, 180), -1)

        frame = self._draw_elegant_text(frame, "OK!", w, h, intensity)

        return frame

    def create_one_finger_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        
        smooth_pos = self._smooth_hand_position(hand_pos)
        cx, cy = int(smooth_pos[0] * w), int(smooth_pos[1] * h)
        t = self._get_time()

        for i in range(16):
            angle = t * 1.4 + i * 0.25
            radius = 42 + i * 3 + 14 * math.sin(t * 3.5 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle) * 0.25)
            if 0 <= x < w and 0 <= y < h:
                alpha = (0.9 - i * 0.05) * intensity
                color = (int(220 * alpha), int(140 * alpha), int(255 * alpha))
                cv2.circle(frame, (x, y), int(4 * intensity), color, -1)

        frame = self._draw_elegant_ring(frame, cx, cy, intensity * 0.6)
        frame = self._draw_elegant_text(frame, "SYEMPRE IKAW LANG!", w, h, intensity)

        return frame

    def create_glow_effect(self, frame, x, y, radius=60):
        h, w = frame.shape[:2]

        for r in range(radius, 0, -4):
            alpha = 1 - (r / radius)
            color = (int(255 * alpha * 0.4), int(200 * alpha * 0.4), int(230 * alpha * 0.4))
            cv2.circle(frame, (x, y), r, color, 2)

        return frame

    def clear_particles(self):
        self.particles = []
        self.trail_particles = []
        self.smooth_hand_pos = (0.5, 0.5)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
