from shared.config.app_properties import PROMETHEUS_URL
from anomaly_detector.collectors.prometheus_collector import PrometheusCollector
from shared.config.logging import configure_logging, AiOpsLog
from anomaly_detector.analysis.statistics import Statistics
from anomaly_detector.analysis.anomaly_detector import AnomalyDetector
from anomaly_detector.analysis.change_point_detector import ChangePointDetector

from datetime import datetime, timedelta, timezone
import pandas as pd
import time


class AnomalyLab:
    POLLING_INTERVAL = 60

    REFERENCE_WINDOW_MINUTES = 30
    DETECTION_WINDOW_MINUTES = 5

    SAMPLING_STEP = "15s"

    ANOMALY_THRESHOLD = 3.0
    CHANGE_POINT_THRESHOLD = 3.0

    CHANGE_POINT_WINDOW_MINUTES = 5

    def __init__(self):
        configure_logging()
        self.log = AiOpsLog("anomaly_lab.main")
        self.statistics = Statistics()
        self.anomaly_detector = AnomalyDetector()
        self.prometheus_collector = PrometheusCollector(PROMETHEUS_URL)
        self.change_point_detector = ChangePointDetector()

    def run(self):
        self.log.info("Starting continuous anomaly detection")

        while True:
            cycle_start = time.monotonic()

            try:
                self.__detect_anomalies()

            except Exception:
                self.log.error("Error during anomaly detection cycle")

            elapsed = time.monotonic() - cycle_start

            sleep_time = max(0, self.POLLING_INTERVAL - elapsed)

            time.sleep(sleep_time)

    def __detect_anomalies(self):

        now = datetime.now(timezone.utc)

        detection_start = now - timedelta(minutes=self.DETECTION_WINDOW_MINUTES)

        reference_start = detection_start - timedelta(
            minutes=self.REFERENCE_WINDOW_MINUTES
        )

        reference_end = detection_start

        df = self.__get_job_processing_duration_mean(reference_start, now)

        if df.empty:
            self.log.warning("No metric samples returned by Prometheus")
            return

        reference_window = df[
            (df["timestamp"] >= reference_start) & (df["timestamp"] < reference_end)
        ]

        detection_window = df[
            (df["timestamp"] >= detection_start) & (df["timestamp"] <= now)
        ]

        if reference_window.empty or detection_window.empty:
            self.log.warning("Insufficient data for anomaly detection")
            return

        self.log.info(
            f"Polling data from {PROMETHEUS_URL}, "
            f"Reference samples: {len(reference_window)}, "
            f"Detection samples: {len(detection_window)}"
        )

        self.__detect_baseline_anomalies(reference_window, detection_window)

        self.__detect_change_points(reference_window, detection_window)

    def __detect_baseline_anomalies(
        self, reference_window: pd.DataFrame, detection_window: pd.DataFrame
    ):

        results = self.anomaly_detector.detect_anomalies_against_baseline(
            baseline=reference_window["value"],
            current_values=detection_window["value"],
            threshold=self.ANOMALY_THRESHOLD,
        )

        anomalies = results[results["is_anomaly"]]

        if anomalies.empty:
            return

        self.log.warning(f"Baseline detection: {len(anomalies)} anomalies detected")

        for timestamp, row in zip(
            detection_window.loc[anomalies.index, "timestamp"], anomalies.itertuples()
        ):
            self.log.warning(
                f"Anomaly detected | "
                f"timestamp={timestamp.isoformat()} | "
                f"value={row.value:.4f} | "
                f"z_score={row.z_score:.2f}"
            )

    def __detect_change_points(
        self, reference_window: pd.DataFrame, detection_window: pd.DataFrame
    ):

        previous_window = reference_window[
            reference_window["timestamp"]
            >= (
                reference_window["timestamp"].max()
                - timedelta(minutes=self.CHANGE_POINT_WINDOW_MINUTES)
            )
        ]

        current_window = detection_window[
            detection_window["timestamp"]
            >= (
                detection_window["timestamp"].max()
                - timedelta(minutes=self.CHANGE_POINT_WINDOW_MINUTES)
            )
        ]

        if previous_window.empty or current_window.empty:
            return

        result = self.change_point_detector.detect_mean_shift(
            previous_window=previous_window["value"],
            current_window=current_window["value"],
            threshold=self.CHANGE_POINT_THRESHOLD,
        )

        if not result["change_detected"]:
            return

        self.log.warning(
            f"Change point detected | "
            f"previous_mean={result['previous_mean']:.4f} | "
            f"current_mean={result['current_mean']:.4f} | "
            f"z_score={result['z_score']:.2f}"
        )

    def detect_moving_change_points(self):

        now = datetime.now(timezone.utc)
        start = now - timedelta(minutes=30)
        end = now

        df = self.__get_job_processing_duration_mean(start, end)

        self.log.info(f"Collected {len(df)} samples")

        if df.empty:
            self.log.warning("No data returned by Prometheus")
            return

        results = self.change_point_detector.detect_change_points(
            values=df["value"], window_size=5, threshold=3.0, min_distance=5
        )

        print("-" * 60)
        print("\n--- Detected change points ---")
        print(results)

    def __get_job_processing_duration_mean(
        self, start: datetime.timestamp, end: datetime.timestamp
    ) -> pd.DataFrame:
        range = "5m"
        query = f"""
            rate(job_processing_duration_seconds_sum[{range}])
            /
            rate(job_processing_duration_seconds_count[{range}])
        """

        return self.prometheus_collector.query_range(
            query=query, start=start.isoformat(), end=end.isoformat(), step="15s"
        )


if __name__ == "__main__":
    try:
        AnomalyLab().run()

    except KeyboardInterrupt:
        print("\nAnomalyLab service stopped.")
