import pandas as pd
from shared.config.logging import AiOpsLog
import matplotlib.pyplot as plt 

class Statistics:

    def __init__(self):
        self.log = AiOpsLog("anomaly_lab.analysis.statistics")

    def calculate_statistics(self, values: pd.Series) -> dict:

        values = pd.to_numeric(values, errors="coerce").dropna()

        if values.empty:
            raise ValueError("Cannot calculate statistics on an empty series")

        return {
            "count": int(values.count()),
            "mean": float(values.mean()),
            "median": float(values.median()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
            "p50": float(values.quantile(0.50)),
            "p95": float(values.quantile(0.95)),
            "p99": float(values.quantile(0.99))
        }

    def print_stats(self, stats: dict):
         for name, value in stats.items():
            print(f"{name}: {value:.4f}" if isinstance(value, float) else f"{name}: {value}")

    def print_graph(self, df: pd.DataFrame, stats: dict):
        plt.figure(figsize=(12, 5))

        plt.plot(
            df["timestamp"],
            df["value"],
            label="Average job duration",
        )

        plt.axhline(
            stats["mean"],
            linestyle="--",
            label="Mean",
        )

        plt.axhline(
            stats["p95"],
            linestyle=":",
            label="P95",
        )

        plt.title("Job Processing Duration")
        plt.xlabel("Time")
        plt.ylabel("Duration (seconds)")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()