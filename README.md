# 3D Hand Tracker with Gesture Recognition

Real-time hand gesture detection with animated visual effects using webcam.

## Gestures

| Gesture | Output |
|---------|--------|
| ✌️ Peace Sign | "I LOVE YOU" + hearts & particles |
| 🤟 I Love You | Same as above (instant) |
| ✋ Open Hand | "HI GUYS!" + wave animation |
| 👊 Fist | "Inday Sara On Top!" + power burst |
| 👍 Thumbs Up | "OK!" + green particles |
| ☝️ One Finger | "SYEMPRE IKAW LANG!" |

## Quick Start

```bash
pip install opencv-python numpy mediapipe
python hand_tracker.py
```

## Options

```bash
python hand_tracker.py --camera 1        # Different camera
python hand_tracker.py --no-animations   # Disable effects
python hand_tracker.py --intensity 0.5   # Lower intensity
```

## Controls

- `q` - Quit
- `c` - Clear animations

## Files

| File | Purpose |
|------|---------|
| `hand_tracker.py` | Main app (run this) |
| `main.py` | Full 3D system with depth |
| `gesture_recognition.py` | Gesture classifier |
| `animation_renderer.py` | Visual effects |
| `feature_detection.py` | MediaPipe detection |
| `depth_estimation.py` | MiDaS depth (optional) |

## Requirements

- Python 3.8+
- Webcam
- 4GB RAM

## Troubleshooting

- **Camera error**: Try `--camera 1` or `--camera 2`
- **Low FPS**: Close other apps, use `--intensity 0.5`
- **No gestures detected**: Ensure good lighting, hand visible to camera
