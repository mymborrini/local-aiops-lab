from shared.config.logging import AiOpsLog
import pandas as pd


class AnomalyDetector:
    def __init__(self):
        self.log = AiOpsLog("anomaly_lab.analysis.anomaly_detector")

    def detect_anomalies_against_baseline(
        self,
        baseline: pd.Series,
        current_values: pd.Series,
        threshold: float = 3.0,
    ) -> pd.DataFrame:

        mean = baseline.mean()
        std = baseline.std()

        if std == 0:
            raise ValueError("Baseline standard deviation cannot be zero")

        z_scores = (current_values - mean) / std

        return pd.DataFrame(
            {
                "value": current_values,
                "z_score": z_scores,
                "is_anomaly": z_scores.abs() > threshold,
            }
        )

    def detect_anomalies(
        self,
        values: pd.Series,
        threshold: float = 3.0,
    ) -> pd.DataFrame:

        mean = values.mean()
        std = values.std()

        z_scores = self._calculate_z_scores(
            values=values,
            mean=mean,
            std=std,
        )

        return pd.DataFrame(
            {
                "value": values,
                "z_score": z_scores,
                "is_anomaly": z_scores.abs() > threshold,
            }
        )

    def _calculate_z_scores(
        self,
        values: pd.Series,
        mean: float,
        std: float,
    ) -> pd.Series:

        if std == 0:
            raise ValueError("Standard deviation cannot be zero")

        return (values - mean) / std
