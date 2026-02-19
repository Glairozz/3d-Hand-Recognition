import cv2
import numpy as np
import argparse
import sys

from camera_capture import CameraCapture
from feature_detection import HandDetector
from gesture_recognition import GestureRecognizer
from animation_renderer import AnimationRenderer


class HandTrackerApp:
    def __init__(
        self,
        camera_index: int = 0,
        show_animations: bool = True,
        animation_intensity: float = 1.0
    ):
        self.camera_index = camera_index
        self.show_animations = show_animations
        self.animation_intensity = animation_intensity

        self.camera = CameraCapture(use_realsense=False, camera_index=camera_index)
        self.hand_detector = HandDetector()
        self.gesture_recognizer = GestureRecognizer()
        self.animation_renderer = AnimationRenderer()

        self.current_gesture = None
        self.gesture_active_time = 0
        self.animation_active = False

    def run(self):
        print("Starting 3D Hand Tracker with Gesture Recognition")
        print("Gestures: Peace -> I Love You | Open Hand -> Hi Guys | Fist -> Power | Thumbs Up -> OK | One -> Syempre Ikaw Lang")
        print("Press 'q' to quit")
        print("Press 'c' to clear animations")

        while True:
            color_frame, _ = self.camera.get_frame()

            if color_frame is None:
                break

            detected_frame, hand_landmarks = self.hand_detector.detect(color_frame)

            gesture = None
            hand_pos = None

            if hand_landmarks:
                for landmarks in hand_landmarks:
                    gesture = self.gesture_recognizer.recognize(landmarks)
                    hand_pos = self.gesture_recognizer.get_palm_center(landmarks)

                    if gesture:
                        cv2.putText(
                            detected_frame,
                            f"Gesture: {gesture}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2
                        )

            gesture_animations = {
                "i_love_you": self.animation_renderer.create_i_love_you_effect,
                "peace": self.animation_renderer.create_i_love_you_effect,
                "open_hand": self.animation_renderer.create_open_hand_effect,
                "fist": self.animation_renderer.create_fist_effect,
                "thumbs_up": self.animation_renderer.create_thumbs_up_effect,
                "one": self.animation_renderer.create_one_finger_effect,
            }

            if gesture in gesture_animations and hand_pos and self.show_animations:
                self.animation_active = True
                self.gesture_active_time += 1

                if gesture in ["i_love_you", "peace", "open_hand", "fist", "thumbs_up", "one"]:
                    intensity = self.animation_intensity
                else:
                    intensity = min(self.animation_intensity, self.gesture_active_time / 30.0)

                detected_frame = gesture_animations[gesture](detected_frame, hand_pos, intensity)

                cx = int(hand_pos[0] * detected_frame.shape[1])
                cy = int(hand_pos[1] * detected_frame.shape[0])
                detected_frame = self.animation_renderer.create_glow_effect(
                    detected_frame, cx, cy, 60
                )
            else:
                if self.gesture_active_time > 0:
                    self.gesture_active_time -= 1
                if self.gesture_active_time == 0:
                    self.animation_active = False
                    self.animation_renderer.clear_particles()

            cv2.imshow("3D Hand Tracker - Gesture Recognition", detected_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                self.animation_renderer.clear_particles()
                self.gesture_active_time = 0
                self.animation_active = False

        self.cleanup()

    def cleanup(self):
        self.camera.release()
        cv2.destroyAllWindows()
        print("Application closed")


def main():
    parser = argparse.ArgumentParser(description="3D Hand Tracker with Gesture Recognition")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--no-animations", action="store_true", help="Disable animations")
    parser.add_argument("--intensity", type=float, default=1.0, help="Animation intensity (0.1-2.0)")

    args = parser.parse_args()

    app = HandTrackerApp(
        camera_index=args.camera,
        show_animations=not args.no_animations,
        animation_intensity=args.intensity
    )

    app.run()


if __name__ == "__main__":
    main()
