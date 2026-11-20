from shared.config.app_properties import PROMETHEUS_URL
from collectors.prometheus_collector import PrometheusCollector
from shared.config.logging import configure_logging, AiOpsLog
from analysis.statistics import Statistics
from analysis.anomaly_detector import AnomalyDetector
from analysis.change_point_detector import ChangePointDetector

from datetime import datetime, timedelta, timezone
import pandas as pd


class AnomalyLab:
    
    def __init__(self):
        configure_logging()
        self.log = AiOpsLog("anomaly_lab.main")
        self.statistics = Statistics()
        self.anomaly_detector = AnomalyDetector()
        self.log.info(f"Trying collecting metrics from {PROMETHEUS_URL}")
        self.prometheus_collector = PrometheusCollector(PROMETHEUS_URL)
        self.change_point_detector = ChangePointDetector()

    def detect_anomalies(self):
       
        now = datetime.now(timezone.utc)

        # Baseline: 17 november, 10:58 - 11:05 UTC
        baseline_start = datetime(2026, 11, 17, 10, 58, tzinfo=timezone.utc)
        baseline_end = datetime(2026, 11, 17, 11, 5, tzinfo=timezone.utc)

        # Current values: last 15 minutes
        current_start = now - timedelta(minutes=5)
        current_end = now

        baseline_df = self.__get_job_processing_duration_mean(baseline_start, baseline_end)
        current_df =  self.__get_job_processing_duration_mean(current_start, current_end)

        self.log.info(f"Baseline: {baseline_start.isoformat()} - {baseline_end.isoformat()}")
        self.log.info(f"Current values: {current_start.isoformat()} - {current_end.isoformat()}")

        self.log.info(f"Number of baseline samples: {len(baseline_df)}")
        self.log.info(f"Number of current samples: {len(current_df)}")

        baseline_stats = self.statistics.calculate_statistics(baseline_df["value"])
        current_stats = self.statistics.calculate_statistics(current_df["value"])

        print("\n--- BASELINE ---")
        self.statistics.print_stats(baseline_stats)
        print("\n--- CURRENT ---")
        self.statistics.print_stats(current_stats)

        results = self.anomaly_detector.detect_anomalies_against_baseline(
            baseline=baseline_df["value"],
            current_values=current_df["value"],
        )

        print(results)
        print("\nDetected anomalies:")
        print(results[results["is_anomaly"]])

    def detect_change_points(self):
        previous = pd.Series([
            4.5, 5.2, 4.8, 5.5, 4.9
        ])
        
        current = pd.Series([
            30, 32, 29, 34, 31
        ])

        result = self.change_point_detector.detect_mean_shift(
            previous_window=previous,
            current_window=current
        )

        print("\nDetected change points:")
        print(result)

    
    def __get_job_processing_duration_mean(self, start: datetime.timestamp, end: datetime.timestamp) -> pd.DataFrame:
        range = "5m"
        query = f"""
            rate(job_processing_duration_seconds_sum[{range}])
            /
            rate(job_processing_duration_seconds_count[{range}])
        """

        return self.prometheus_collector.query_range(
            query=query,
            start=start.isoformat(),
            end=end.isoformat(),
            step="15s"
        )



if __name__ == "__main__":
    AnomalyLab().detect_change_points()