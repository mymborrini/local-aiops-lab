import pandas as pd
from shared.config.logging import AiOpsLog


class ChangePointDetector:
    def __init__(self):
        self.log = AiOpsLog("anomaly_lab.analysis.change_point_detector")

    def detect_mean_shift(
        self,
        previous_window: pd.Series,
        current_window: pd.Series,
        threshold: float = 3.0,
    ) -> dict:

        previous_window = pd.to_numeric(previous_window, errors="coerce").dropna()

        current_window = pd.to_numeric(current_window, errors="coerce").dropna()

        if previous_window.empty or current_window.empty:
            raise ValueError("Windows cannot be empty")

        previous_mean = previous_window.mean()
        current_mean = current_window.mean()

        previous_std = previous_window.std()

        if pd.isna(previous_std):
            raise ValueError("Insufficient samples in previous window")

        if previous_std == 0:
            z_score = (
                0.0
                if current_mean == previous_mean
                else float("inf")
                if current_mean > previous_mean
                else float("-inf")
            )
        else:
            z_score = (current_mean - previous_mean) / previous_std

        return {
            "previous_mean": float(previous_mean),
            "current_mean": float(current_mean),
            "z_score": float(z_score),
            "change_detected": bool(abs(z_score) > threshold),
        }

    def detect_change_points(
        self,
        values: pd.Series,
        window_size: int = 5,
        threshold: int = 3.0,
        min_distance: int = 5,
    ) -> pd.DataFrame:

        if window_size < 2:
            raise ValueError("window_size must be at least 2")

        if min_distance < 1:
            raise ValueError("min_distance must be at least 1")

        values = pd.to_numeric(values, errors="coerce").dropna().reset_index(drop=True)

        if len(values) < window_size * 2:
            raise ValueError("Not enough samples for the selected window size")

        results = []

        for i in range(window_size, len(values) - window_size + 1):
            previous_window = values.iloc[i - window_size : i]
            current_window = values.iloc[i : i + window_size]

            result = self.detect_mean_shift(
                previous_window=previous_window,
                current_window=current_window,
                threshold=threshold,
            )

            results.append({"index": i, **result})

        result_df = pd.DataFrame(results)

        print("\n ---- Result without grouping ----")
        print(result_df)

        return self._group_change_points(results=result_df, min_distance=min_distance)

    def _group_change_points(
        self, results: pd.DataFrame, min_distance: int
    ) -> pd.DataFrame:
        if results.empty:
            return results

        candidates = results[results["change_detected"]].copy()

        if candidates.empty:
            return candidates

        candidates = candidates.sort_values("index")
        groups = []
        current_group = [candidates.iloc[0]]

        for _, row in candidates.iloc[1:].iterrows():
            previous_index = current_group[-1]["index"]

            if row["index"] - previous_index < min_distance:
                current_group.append(row)
            else:
                groups.append(current_group)
                current_group = [row]

        groups.append(current_group)

        selected = []

        for group in groups:
            strongest = max(group, key=lambda row: abs(row["z_score"]))
            selected.append(strongest)

        return pd.DataFrame(selected).reset_index(drop=True)
