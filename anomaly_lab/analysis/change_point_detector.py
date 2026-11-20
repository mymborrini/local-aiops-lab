import pandas as pd
from shared.config.logging import AiOpsLog

class ChangePointDetector:

    def __init__(self):
        self.log = AiOpsLog("anomaly_lab.analysis.change_point_detector")

    def detect_mean_shift(self, previous_window: pd.Series, current_window: pd.Series, threshold: float = 3.0) -> dict:

        previous_mean = previous_window.mean()
        current_mean = current_window.mean()

        previous_std = previous_window.std()

        if previous_std == 0 :
            raise ValueError("Previous window standard deviation cannot be zero")

        z_score = (current_mean - previous_mean) / previous_std

        return {
            "previous_mean": float(previous_mean),
            "current_mean": float(current_mean),
            "z_score": float(z_score),
            "change_detected": bool(abs(z_score) > threshold)
        }