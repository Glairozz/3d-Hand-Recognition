# 3D Hand Tracker with Gesture Recognition

A Python-based 3D recognition system that detects hand gestures using a webcam, recognizes the peace sign (✌️), and displays a cool "I Love You" animation with hearts, particles, and visual effects.

## Features

- **Real-time Hand Tracking** - Uses MediaPipe for accurate hand landmark detection
- **Gesture Recognition** - Detects multiple gestures with animations:
  - ✌️ **Peace Sign** → Triggers "I Love You" animation (after 0.5s)
  - 🤟 **I Love You (ILY)** → Instant "I LOVE YOU" animation with hearts & particles
  - ✋ **Open Hand** → Instant "HI GUYS!" wave animation
  - 👊 **Fist** → Instant "POWER!" punch animation with expanding circles
  - 👍 **Thumbs Up** → Instant "OK!" animation with green particles
  - ☝️ **One Finger** → Instant "SYEMPRE IKAW LANG!" animation (Filipino)
- **Cool Animations** - Heart particles, floating hearts, glow effects, pulsing text, wave effects
- **3D Visualization** - Optional Open3D point cloud visualization
- **Depth Support** - Optional MiDaS depth estimation or Intel RealSense camera

## Installation

### 1. Clone or Download the Project

```bash
cd "C:\Downloads\All python relation\3d recogniton"
```

### 2. Install Python Dependencies

**Option A - Full Installation (Recommended):**
```bash
pip install -r requirements.txt
```

**Option B - Minimal Installation (Hand Tracker Only):**
```bash
pip install opencv-python numpy mediapipe
```

**Option C - Manual Installation:**
```bash
pip install opencv-python>=4.8.0
pip install numpy>=1.24.0
pip install mediapipe>=0.10.0
pip install ultralytics>=8.0.0
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install open3d>=0.17.0
```

### 3. Special Dependencies

**For Intel RealSense Camera:**
- Install [Intel RealSense SDK 2.0](https://github.com/IntelRealSense/librealsense)
- Then: `pip install pyrealsense2`

**For Open3D (Better compatibility):**
- Download from: https://www.open3d.org/docs/release/getting_started.html

## Usage

### Basic Usage (Hand Tracker with Animations)
```bash
python hand_tracker.py
```

### With Custom Camera
```bash
python hand_tracker.py --camera 1
```

### Disable Animations
```bash
python hand_tracker.py --no-animations
```

### Adjust Animation Intensity
```bash
python hand_tracker.py --intensity 1.5
```

### Full 3D Recognition System
```bash
python main.py --mode hand
```

### Other Detection Modes
```bash
python main.py --mode face      # Face detection
python main.py --mode object    # Object detection (YOLOv8)
python main.py --realsense      # Use Intel RealSense camera
```

## Controls

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `c` | Clear animations |

## Project Structure

```
3d recogniton/
├── hand_tracker.py          # Main application (run this!)
├── main.py                 # Full 3D recognition system
├── camera_capture.py       # Camera handling (webcam/Realsense)
├── depth_estimation.py     # MiDaS depth estimation
├── feature_detection.py    # MediaPipe/YOLOv8 detection
├── gesture_recognition.py  # Gesture classification
├── animation_renderer.py   # Visual effects & animations
├── coordinate_conversion.py# 2D to 3D coordinate mapping
├── visualization_3d.py     # Open3D visualization
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Requirements

- Python 3.8+
- Webcam or Intel RealSense D435 camera
- 4GB RAM minimum (8GB recommended for full system)

## Troubleshooting

### Camera not opening
- Check if another application is using the camera
- Try different camera index: `--camera 1` or `--camera 2`

### Low FPS
- Close other applications
- Reduce camera resolution in `camera_capture.py`
- Use CPU-optimized PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

### MediaPipe errors
- Update Mediapipe: `pip install --upgrade mediapipe`
- Ensure OpenCV is installed: `pip install opencv-python`

### Animation lag
- Reduce intensity: `--intensity 0.5`
- Disable some visual effects in `animation_renderer.py`

## How It Works

1. **Camera Capture** - Captures video frames from webcam
2. **Hand Detection** - MediaPipe detects 21 hand landmarks
3. **Gesture Recognition** - Classifies hand pose based on finger positions
4. **2D to 3D** - Converts landmarks to 3D coordinates (with depth)
5. **Animation** - Renders visual effects at hand position

## License

MIT License - Free to use and modify
