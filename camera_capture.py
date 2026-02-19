import cv2
import numpy as np
from typing import Optional, Tuple
import pyrealsense2 as rs


class CameraCapture:
    def __init__(self, use_realsense: bool = False, camera_index: int = 0):
        self.use_realsense = use_realsense
        self.camera_index = camera_index
        self.pipeline = None
        self.pipeline_profile = None
        self._initialize_camera()

    def _initialize_camera(self):
        if self.use_realsense:
            self._init_realsense()
        else:
            self._init_webcam()

    def _init_realsense(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline_profile = self.pipeline.start(config)

    def _init_webcam(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 840)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 680)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera at index {self.camera_index}")

    def get_frame(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        if self.use_realsense:
            return self._get_realsense_frame()
        else:
            return self._get_webcam_frame(), None

    def _get_realsense_frame(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            return None, None

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return color_image, depth_image

    def _get_webcam_frame(self) -> Optional[np.ndarray]:
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def get_intrinsics(self) -> Optional[dict]:
        if self.use_realsense and self.pipeline_profile:
            depth_stream = self.pipeline_profile.get_stream(rs.stream.depth)
            intrinsics = depth_stream.as_video_stream_profile().get_intrinsics()
            return {
                'fx': intrinsics.fx,
                'fy': intrinsics.fy,
                'cx': intrinsics.ppx,
                'cy': intrinsics.ppy,
                'width': intrinsics.width,
                'height': intrinsics.height
            }
        return None

    def release(self):
        if self.use_realsense and self.pipeline:
            self.pipeline.stop()
        elif hasattr(self, 'cap'):
            self.cap.release()
