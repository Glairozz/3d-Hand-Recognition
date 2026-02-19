import cv2
import numpy as np
import torch
from typing import Optional
from torchvision.transforms import Compose, Resize, Normalize, ToTensor


class DepthEstimator:
    def __init__(self, model_type: str = "DPT_Large"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = None
        self._load_model(model_type)

    def _load_model(self, model_type: str):
        if model_type == "DPT_Large":
            self.model = torch.hub.load("intel-isl/MiDaS", "DPT_Large")
        elif model_type == "DPT_Hybrid":
            self.model = torch.hub.load("intel-isl/MiDaS", "DPT_Hybrid")
        else:
            self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS")

        self.model.to(self.device)
        self.model.eval()

        self.transform = Compose([
            Resize((384, 384)),
            ToTensor(),
            Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_batch = self.transform(img_rgb).unsqueeze(0).to(self.device)

        with torch.no_grad():
            prediction = self.model(input_batch)

        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode="bicubic",
            align_corners=False
        ).squeeze()

        depth_map = prediction.cpu().numpy()
        depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min() + 1e-8)
        depth_map = (depth_map * 255).astype(np.uint8)

        return depth_map

    def get_depth_at_point(self, depth_map: np.ndarray, x: int, y: int) -> float:
        h, w = depth_map.shape
        if 0 <= x < w and 0 <= y < h:
            return float(depth_map[y, x])
        return 0.0
