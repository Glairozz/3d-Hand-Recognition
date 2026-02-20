import cv2
import numpy as np
from typing import Tuple, List
import math
import random


class AnimationRenderer:
    def __init__(self):
        self.particles = []
        self.glitch_offset = 0
        self.scan_lines = []

    def create_i_love_you_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)

        frame = self._draw_holographic_circle(frame, cx, cy, intensity)
        frame = self._draw_neon_hearts(frame, cx, cy, intensity)
        frame = self._draw_futuristic_particles(frame, cx, cy, intensity)
        frame = self._draw_cyber_rainbow(frame, cx, cy, intensity)
        frame = self._draw_futuristic_text(frame, "I LOVE YOU", w, h, 
                                          [(0, 255, 255), (255, 0, 255), (0, 255, 200)], 
                                          intensity)
        frame = self._draw_holo_outline(frame, cx, cy, int(100 * intensity))

        return frame

    def _draw_holographic_circle(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 800000

        for i in range(6):
            radius = 60 + i * 20 + 15 * math.sin(time * 2 + i)
            alpha = (1 - i / 6) * intensity * 0.7
            color = self._get_neon_color(i, alpha)
            cv2.circle(frame, (cx, cy), int(radius), color, 2)

            for angle in np.linspace(0, 2 * math.pi, 36):
                x = int(cx + radius * math.cos(angle + time * 2))
                y = int(cy + radius * math.sin(angle + time * 2))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 2, color, -1)

        return frame

    def _get_neon_color(self, index, alpha=1.0):
        colors = [
            (0, 255, 255),   # Cyan
            (255, 0, 255),   # Magenta
            (0, 255, 200),   # Electric Blue
            (255, 0, 150),  # Pink
            (150, 255, 0),  # Lime
            (255, 100, 0),  # Orange
        ]
        color = colors[index % len(colors)]
        return tuple(int(c * alpha) for c in color)

    def _draw_neon_hearts(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 800000

        heart_colors = [
            (255, 0, 150), (255, 50, 200), (0, 255, 255),
            (255, 100, 255), (150, 0, 255)
        ]

        for i in range(15):
            angle = time * 1.5 + i * 0.7
            radius = 50 + i * 10 + 20 * math.sin(time * 3 + i)
            
            x = int(cx + radius * math.cos(angle))
            y = int(cy - 30 + radius * math.sin(angle) * 0.3 - (time * 50 + i * 20) % 150)

            if 0 <= x < w and 0 <= y < h:
                size = int((15 + 8 * math.sin(time * 5 + i * 0.5)) * intensity)
                color = heart_colors[i % len(heart_colors)]
                frame = self._draw_neon_heart(frame, x, y, size, color)

        return frame

    def _draw_neon_heart(self, frame, x, y, size, color):
        if size < 4:
            return frame

        points = []
        for t in np.linspace(0, 2 * math.pi, 30):
            hx = size * 14 * math.pow(math.sin(t), 3)
            hy = -size * (11 * math.cos(t) - 4 * math.cos(2*t) - 2 * math.cos(3*t))
            points.append((int(x + hx), int(y + hy)))

        pts = np.array(points, np.int32)
        
        glow_color = tuple(max(0, min(255, c + 100)) for c in color)
        for glow in range(8, 0, -2):
            alpha = 0.1 / (glow / 2)
            g_color = tuple(int(c * alpha) for c in glow_color)
            cv2.polylines(frame, [pts], True, g_color, glow + 2)

        cv2.fillPoly(frame, [pts], color)
        cv2.polylines(frame, [pts], True, (255, 255, 255), 1)

        return frame

    def _draw_futuristic_particles(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 800000

        if len(self.particles) < 100:
            for _ in range(4):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(3, 8)
                self.particles.append({
                    'x': cx,
                    'y': cy,
                    'vx': speed * math.cos(angle),
                    'vy': speed * math.sin(angle) - 2,
                    'life': 1.0,
                    'color': self._get_neon_color(random.randint(0, 5)),
                    'size': random.randint(3, 7),
                    'decay': random.uniform(0.01, 0.025),
                    'trail': []
                })

        for p in self.particles[:]:
            p['trail'].append((int(p['x']), int(p['y'])))
            if len(p['trail']) > 8:
                p['trail'].pop(0)

            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['life'] -= p['decay']

            if p['life'] <= 0 or p['y'] > h:
                self.particles.remove(p)
                continue

            if 0 <= int(p['x']) < w and 0 <= int(p['y']) < h:
                for j, (tx, ty) in enumerate(p['trail']):
                    if 0 <= tx < w and 0 <= ty < h:
                        alpha = (j / len(p['trail'])) * p['life'] * intensity
                        t_color = tuple(int(c * alpha * 0.5) for c in p['color'])
                        cv2.circle(frame, (tx, ty), max(1, int(p['size'] * 0.5 * alpha)), t_color, -1)

                alpha = p['life'] * intensity
                color = tuple(int(c * alpha) for c in p['color'])
                cv2.circle(frame, (int(p['x']), int(p['y'])), 
                          int(p['size'] * p['life']), color, -1)
                cv2.circle(frame, (int(p['x']), int(p['y'])), 
                          int(p['size'] * p['life'] + 2), (255, 255, 255), 1)

        return frame

    def _draw_cyber_rainbow(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 800000

        colors = [
            (255, 0, 100), (255, 100, 0), (255, 255, 0),
            (0, 255, 100), (0, 100, 255), (255, 0, 255)
        ]

        for i, color in enumerate(colors):
            angle_offset = time * 1.5 + i * 0.8
            radius = 80 + 20 * math.sin(time * 2.5 + i)

            for a in np.linspace(0, 2 * math.pi, 25):
                x = int(cx + radius * math.cos(a + angle_offset))
                y = int(cy + radius * math.sin(a + angle_offset) * 0.8)
                if 0 <= x < w and 0 <= y < h:
                    alpha = 0.8 * intensity
                    c = tuple(int(c * alpha) for c in color)
                    cv2.circle(frame, (x, y), 3, c, -1)

        return frame

    def _draw_futuristic_text(self, frame, text, w, h, colors, intensity):
        time = cv2.getTickCount() / 800000

        scale = 2.0 + 0.5 * math.sin(time * 3)
        thickness = 5

        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX

        for layer in range(12, 0, -1):
            alpha = (0.08 / (layer / 3)) * intensity
            for c in colors:
                glow_r = min(255, int(c[0] * 1.5 * alpha))
                glow_g = min(255, int(c[1] * 1.5 * alpha))
                glow_b = min(255, int(c[2] * 1.5 * alpha))
                glow = (glow_r, glow_g, glow_b)
                x = (w - 450) // 2 + layer
                y = h - 120 + layer
                cv2.putText(frame, text, (x, y), font, scale, glow, thickness + layer)

        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        x = (w - text_size[0]) // 2
        y = h - 120

        gradient = np.linspace(0, 1, len(text))
        for i, color in enumerate(colors):
            color = tuple(int(c * intensity) for c in color)
            cv2.putText(frame, text, (x + i, y + i), font, scale, color, thickness)

        glow_layer = np.zeros_like(frame)
        cv2.putText(glow_layer, text, (x, y), font, scale, (255, 255, 255), thickness + 4)
        glow_layer = cv2.GaussianBlur(glow_layer, (21, 21), 0)
        frame = cv2.addWeighted(frame, 0.85, glow_layer, 0.15 * intensity, 0)

        subtext = "PEACE SIGN"
        sub_scale = 1.0
        sub_size = cv2.getTextSize(subtext, font, sub_scale, 2)[0]
        glow = (int(200 * intensity), int(200 * intensity), int(200 * intensity))
        cv2.putText(frame, subtext, ((w - sub_size[0]) // 2, y + 70), 
                   font, sub_scale, glow, 3)

        return frame

    def _draw_holo_outline(self, frame, cx, cy, radius):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 800000

        for ring in range(3):
            r = radius + ring * 30
            alpha = (1 - ring / 3) * 0.5
            color = self._get_neon_color(ring, alpha)
            
            for angle in np.linspace(0, 2 * math.pi, 60):
                offset = 5 * math.sin(time * 5 + angle * 8)
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
        time = cv2.getTickCount() / 800000

        frame = self._draw_holographic_circle(frame, cx, cy, intensity)
        frame = self._draw_cyber_wave(frame, cx, cy, intensity)
        frame = self._draw_futuristic_particles(frame, cx, cy, intensity)
        
        for i in range(6):
            offset_x = int(120 * math.cos(time * 3 + i * 1.0))
            offset_y = int(90 * math.sin(time * 3 + i * 1.0))
            x = cx + offset_x
            y = cy + offset_y - 70
            if 0 <= x < w and 0 <= y < h:
                size = int((25 + 10 * math.sin(time * 6 + i)) * intensity)
                frame = self._draw_emoji(frame, "👋", x, y, size)

        frame = self._draw_futuristic_text(frame, "HI GUYS!", w, h,
                                           [(100, 255, 255), (255, 255, 100), (255, 200, 100)],
                                           intensity)

        return frame

    def _draw_cyber_wave(self, frame, cx, cy, intensity):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 800000

        for i in range(8):
            phase = time * 4 + i * 1.5
            radius = 50 + i * 20 + 15 * math.sin(phase)
            alpha = (1 - i / 8) * intensity * 0.6
            color = self._get_neon_color(i, alpha)
            cv2.circle(frame, (cx, cy), int(radius), color, 2)

            for a in np.linspace(0, 2 * math.pi, 12):
                x = int(cx + radius * math.cos(a + time * 3))
                y = int(cy + radius * math.sin(a + time * 3))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 5, color, -1)

        return frame

    def _draw_emoji(self, frame, emoji, x, y, size):
        if size < 10:
            return frame
        cv2.putText(frame, emoji, (x - size//2, y + size//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, size/30, (255, 255, 255), 2)
        return frame

    def create_fist_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = cv2.getTickCount() / 800000

        for i in range(16):
            angle = i * math.pi / 8 + time * 4
            radius = 60 + 30 * math.sin(time * 5 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            if 0 <= x < w and 0 <= y < h:
                color = self._get_neon_color(i % 6, intensity)
                cv2.circle(frame, (x, y), int(10 * intensity), color, -1)

        for r in [40, 65, 90, 115]:
            radius = r + int(20 * math.sin(time * 6))
            alpha = (1 - r / 120) * intensity
            color = self._get_neon_color(0, alpha)
            cv2.circle(frame, (cx, cy), radius, color, 3)

            for angle in np.linspace(0, 2 * math.pi, 8):
                x = int(cx + radius * math.cos(angle + time * 2))
                y = int(cy + radius * math.sin(angle + time * 2))
                if 0 <= x < w and 0 <= y < h:
                    cv2.circle(frame, (x, y), 4, color, -1)

        frame = self._draw_futuristic_text(frame, "Inday Sara On Top!", w, h,
                                           [(255, 200, 50), (255, 150, 0), (255, 100, 50)],
                                           intensity)

        return frame

    def create_thumbs_up_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = cv2.getTickCount() / 800000

        for i in range(12):
            angle = time * 2.5 + i * 0.5
            radius = 55 + i * 7 + 15 * math.sin(time * 4 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy - 25 + radius * math.sin(angle) * 0.4)
            if 0 <= x < w and 0 <= y < h:
                alpha = (1 - i / 12) * intensity
                color = (int(50 * alpha), int(255 * alpha), int(150 * alpha))
                cv2.circle(frame, (x, y), int(7 * intensity), color, -1)

        for i in range(8):
            offset = int(60 * math.sin(time * 5 + i))
            x = cx - 50 + i * 14
            y = cy - 70 + offset
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(frame, (x, y), int(6 * intensity), (50, 255, 150), -1)

        frame = self._draw_futuristic_text(frame, "OK!", w, h,
                                           [(50, 255, 150), (100, 255, 200), (150, 255, 100)],
                                           intensity)

        return frame

    def create_one_finger_effect(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[float, float],
        intensity: float = 1.0
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        cx, cy = int(hand_pos[0] * w), int(hand_pos[1] * h)
        time = cv2.getTickCount() / 800000

        for i in range(20):
            angle = time * 2 + i * 0.3
            radius = 45 + i * 5 + 18 * math.sin(time * 4 + i)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle) * 0.3)
            if 0 <= x < w and 0 <= y < h:
                alpha = (1 - i / 20) * intensity
                color = self._get_neon_color((i + 2) % 6, alpha)
                cv2.circle(frame, (x, y), int(5 * intensity), color, -1)

        frame = self._draw_holographic_circle(frame, cx, cy, intensity * 0.7)
        frame = self._draw_futuristic_text(frame, "SYEMPRE IKAW LANG!", w, h,
                                           [(200, 100, 255), (255, 150, 200), (255, 100, 200)],
                                           intensity)

        return frame

    def create_glow_effect(self, frame, x, y, radius=70):
        h, w = frame.shape[:2]
        time = cv2.getTickCount() / 800000

        for r in range(radius, 0, -2):
            alpha = 1 - (r / radius)
            color = (int(0 * alpha), int(255 * alpha * 0.7), int(255 * alpha * 0.7))
            cv2.circle(frame, (x, y), r, color, 2)

        return frame

    def clear_particles(self):
        self.particles = []
        self.scan_lines = []
