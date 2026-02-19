import numpy as np
import open3d as o3d
from typing import List, Dict, Optional, Tuple
import threading


class Visualizer3D:
    def __init__(self, window_name: str = "3D Recognition"):
        self.window_name = window_name
        self.vis = None
        self.point_cloud = None
        self.geometries = []
        self.running = False
        self.lock = threading.Lock()

    def initialize(self):
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window(
            window_name=self.window_name,
            width=1280,
            height=720
        )
        self.running = True

    def update_point_cloud(
        self,
        points: np.ndarray,
        colors: Optional[np.ndarray] = None
    ):
        with self.lock:
            if self.point_cloud is not None:
                self.vis.remove_geometry(self.point_cloud)

            self.point_cloud = o3d.geometry.PointCloud()
            self.point_cloud.points = o3d.utility.Vector3dVector(points)

            if colors is not None:
                self.point_cloud.colors = o3d.utility.Vector3dVector(colors)

            self.vis.add_geometry(self.point_cloud)

    def add_geometries(self, geometry):
        with self.lock:
            self.vis.add_geometry(geometry)

    def remove_geometries(self, geometry):
        with self.lock:
            self.vis.remove_geometry(geometry)

    def render_frame(self):
        if self.vis:
            self.vis.poll_events()
            self.vis.update_renderer()

    def run(self):
        self.initialize()
        self.vis.run()

    def close(self):
        if self.vis:
            self.vis.destroy_window()
            self.running = False


class PointCloudProcessor:
    def __init__(self):
        pass

    def create_from_arrays(
        self,
        points: np.ndarray,
        colors: Optional[np.ndarray] = None
    ) -> o3d.geometry.PointCloud:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)

        if colors is not None:
            pcd.colors = o3d.utility.Vector3dVector(colors)

        return pcd

    def downsample(
        self,
        pcd: o3d.geometry.PointCloud,
        voxel_size: float = 0.01
    ) -> o3d.geometry.PointCloud:
        return pcd.voxel_down_sample(voxel_size)

    def estimate_normals(self, pcd: o3d.geometry.PointCloud):
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
        )
        pcd.orient_normals_consistent_tangent_plane(k=15)

    def cluster_dbscan(
        self,
        pcd: o3d.geometry.PointCloud,
        eps: float = 0.02,
        min_points: int = 10
    ) -> List[int]:
        labels = np.array(pcd.cluster_dbscan(eps=eps, min_points=min_points))
        return labels

    def remove_outliers(
        self,
        pcd: o3d.geometry.PointCloud,
        nb_points: int = 20,
        radius: float = 0.02
    ) -> o3d.geometry.PointCloud:
        cl, ind = pcd.remove_radius_outlier(nb_points, radius)
        return pcd.select_by_index(ind)

    def bounding_box(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.OrientedBoundingBox:
        return pcd.get_oriented_bounding_box()

    def axis_align(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        pcd.translate(-pcd.get_center())
        return pcd


class LandmarkVisualizer:
    def __init__(self):
        self.joint_radius = 0.01
        self.line_radius = 0.003
        self.colors = {
            'hand': [1.0, 0.0, 0.0],
            'face': [0.0, 1.0, 0.0],
            'object': [0.0, 0.0, 1.0]
        }

    def create_sphere(self, center: np.ndarray, radius: float, color: List[float]) -> o3d.geometry.TriangleMesh:
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
        sphere.translate(center)
        sphere.paint_uniform_color(color)
        return sphere

    def create_line(
        self,
        start: np.ndarray,
        end: np.ndarray,
        color: List[float]
    ) -> o3d.geometry.LineSet:
        points = [start, end]
        lines = [[0, 1]]
        colors = [color, color]

        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)

        return line_set

    def visualize_hand_landmarks(self, landmarks_3d: List[Dict]) -> List:
        geometries = []

        for landmark in landmarks_3d:
            center = np.array([landmark['x'], landmark['y'], landmark['z']])
            sphere = self.create_sphere(center, self.joint_radius, self.colors['hand'])
            geometries.append(sphere)

        hand_connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17)
        ]

        for idx1, idx2 in hand_connections:
            if idx1 < len(landmarks_3d) and idx2 < len(landmarks_3d):
                start = np.array([landmarks_3d[idx1]['x'], landmarks_3d[idx1]['y'], landmarks_3d[idx1]['z']])
                end = np.array([landmarks_3d[idx2]['x'], landmarks_3d[idx2]['y'], landmarks_3d[idx2]['z']])
                line = self.create_line(start, end, self.colors['hand'])
                geometries.append(line)

        return geometries
