import numpy as np
from typing import List, Dict, Tuple, Optional


class CoordinateConverter:
    def __init__(
        self,
        intrinsics: Optional[Dict] = None,
        depth_scale: float = 1.0,
        camera_height: float = 0.5,
        focal_length: float = 600.0
    ):
        self.intrinsics = intrinsics or {}
        self.depth_scale = depth_scale
        self.camera_height = camera_height
        self.focal_length = focal_length

    def set_intrinsics(self, fx: float, fy: float, cx: float, cy: float):
        self.intrinsics = {'fx': fx, 'fy': fy, 'cx': cx, 'cy': cy}

    def pixel_to_3d(
        self,
        u: float,
        v: float,
        depth: float,
        scale_factor: float = 1.0
    ) -> Tuple[float, float, float]:
        if not self.intrinsics:
            fx = fy = self.focal_length
            cx = cy = 320
        else:
            fx = self.intrinsics.get('fx', self.focal_length)
            fy = self.intrinsics.get('fy', self.focal_length)
            cx = self.intrinsics.get('cx', 320)
            cy = self.intrinsics.get('cy', 240)

        z = depth * scale_factor
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy

        return x, y, z

    def convert_2d_to_3d(
        self,
        points_2d: List[Dict],
        depth_map: Optional[np.ndarray] = None,
        depth_frame: Optional[np.ndarray] = None,
        image_width: int = 640,
        image_height: int = 480
    ) -> List[Dict]:
        points_3d = []

        for point in points_2d:
            if 'x' in point and 'y' in point:
                u = point['x'] * image_width
                v = point['y'] * image_height
            elif 'bbox' in point:
                u = point['center'][0]
                v = point['center'][1]
            else:
                continue

            if depth_frame is not None:
                depth = self._get_depth_from_realsense(depth_frame, int(u), int(v))
            elif depth_map is not None:
                depth = self._get_depth_from_midas(depth_map, int(u), int(v))
            else:
                depth = 1.0

            x, y, z = self.pixel_to_3d(u, v, depth)

            points_3d.append({
                'x': x,
                'y': y,
                'z': z,
                'original_2d': point
            })

        return points_3d

    def _get_depth_from_realsense(
        self,
        depth_frame: np.ndarray,
        x: int,
        y: int
    ) -> float:
        h, w = depth_frame.shape
        if 0 <= x < w and 0 <= y < h:
            return float(depth_frame[y, x]) * self.depth_scale / 1000.0
        return 1.0

    def _get_depth_from_midas(
        self,
        depth_map: np.ndarray,
        x: int,
        y: int
    ) -> float:
        h, w = depth_map.shape
        if 0 <= x < w and 0 <= y < h:
            return float(depth_map[y, x]) / 255.0 * 5.0
        return 1.0

    def create_point_cloud(
        self,
        points_3d: List[Dict],
        colors: Optional[List[Tuple[int, int, int]]] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        num_points = len(points_3d)
        points = np.zeros((num_points, 3))
        point_colors = np.zeros((num_points, 3))

        for i, point in enumerate(points_3d):
            points[i] = [point['x'], point['y'], point['z']]
            if colors and i < len(colors):
                point_colors[i] = [c / 255.0 for c in colors[i]]

        return points, point_colors
