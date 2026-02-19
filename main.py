import cv2
import numpy as np
from typing import Optional
import argparse
import sys

from camera_capture import CameraCapture
from depth_estimation import DepthEstimator
from feature_detection import HandDetector, FaceDetector, ObjectDetector
from coordinate_conversion import CoordinateConverter
from visualization_3d import Visualizer3D, PointCloudProcessor, LandmarkVisualizer


class Recognition3DApp:
    def __init__(
        self,
        use_realsense: bool = False,
        detection_mode: str = "hand",
        use_midas: bool = True,
        show_2d: bool = True,
        show_3d: bool = True
    ):
        self.use_realsense = use_realsense
        self.detection_mode = detection_mode
        self.use_midas = use_midas
        self.show_2d = show_2d
        self.show_3d = show_3d

        self.camera = CameraCapture(use_realsense=use_realsense)
        self.depth_estimator = DepthEstimator() if use_midas and not use_realsense else None
        self.coord_converter = CoordinateConverter()

        intrinsics = self.camera.get_intrinsics()
        if intrinsics:
            self.coord_converter.set_intrinsics(
                intrinsics['fx'], intrinsics['fy'],
                intrinsics['cx'], intrinsics['cy']
            )

        if detection_mode == "hand":
            self.detector = HandDetector()
        elif detection_mode == "face":
            self.detector = FaceDetector()
        elif detection_mode == "object":
            self.detector = ObjectDetector()
        else:
            raise ValueError(f"Unknown detection mode: {detection_mode}")

        self.visualizer_3d = Visualizer3D() if show_3d else None
        self.pcd_processor = PointCloudProcessor()
        self.landmark_viz = LandmarkVisualizer()

    def run(self):
        print(f"Starting 3D Recognition System")
        print(f"Mode: {self.detection_mode}")
        print(f"Depth: {'RealSense' if self.use_realsense else 'MiDaS' if self.use_midas else 'None'}")
        print("Press 'q' to quit")

        try:
            while True:
                color_frame, depth_frame = self.camera.get_frame()

                if color_frame is None:
                    break

                detected_frame, detections = self._process_detection(color_frame)

                if self.use_realsense:
                    depth_map = depth_frame
                elif self.use_midas and self.depth_estimator:
                    depth_map = self.depth_estimator.estimate_depth(color_frame)
                else:
                    depth_map = None

                points_3d = self._convert_to_3d(detections, depth_map, depth_frame, color_frame.shape)

                if self.show_3d and points_3d and self.visualizer_3d:
                    self._update_3d_visualization(points_3d)

                if self.show_2d:
                    cv2.imshow("2D Detection", detected_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

        finally:
            self.cleanup()

    def _process_detection(self, frame):
        if self.detection_mode == "object":
            return self.detector.detect(frame)
        else:
            return self.detector.detect(frame)

    def _convert_to_3d(self, detections, depth_map, depth_frame, image_shape):
        if not detections:
            return []

        h, w = image_shape[:2]
        points_3d = self.coord_converter.convert_2d_to_3d(
            detections,
            depth_map=depth_map,
            depth_frame=depth_frame,
            image_width=w,
            image_height=h
        )

        return points_3d

    def _update_3d_visualization(self, points_3d):
        if not points_3d:
            return

        points_array = np.array([[p['x'], p['y'], p['z']] for p in points_3d])
        colors = np.random.rand(len(points_array), 3)

        self.visualizer_3d.update_point_cloud(points_array, colors)
        self.visualizer_3d.render_frame()

    def cleanup(self):
        self.camera.release()
        if self.visualizer_3d:
            self.visualizer_3d.close()
        cv2.destroyAllWindows()
        print("Cleanup complete")


def main():
    parser = argparse.ArgumentParser(description="3D Recognition System")
    parser.add_argument("--realsense", action="store_true", help="Use Intel RealSense camera")
    parser.add_argument("--mode", type=str, default="hand",
                        choices=["hand", "face", "object"],
                        help="Detection mode")
    parser.add_argument("--no-midas", action="store_true", help="Disable MiDaS depth estimation")
    parser.add_argument("--no-2d", action="store_true", help="Disable 2D visualization")
    parser.add_argument("--no-3d", action="store_true", help="Disable 3D visualization")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index")

    args = parser.parse_args()

    use_realsense = args.realsense
    use_midas = not args.no_midas and not use_realsense

    app = Recognition3DApp(
        use_realsense=use_realsense,
        detection_mode=args.mode,
        use_midas=use_midas,
        show_2d=not args.no_2d,
        show_3d=not args.no_3d
    )

    app.run()


if __name__ == "__main__":
    main()
