from analysis.change_point_detector import ChangePointDetector

import pandas as pd


class MockedAnomalyLab:
    def __init__(self):
        self.change_point_detector = ChangePointDetector()

    def detect_change_points(self):
        previous = pd.Series([4.5, 5.2, 4.8, 5.5, 4.9])

        current = pd.Series([30, 32, 29, 34, 31])

        result = self.change_point_detector.detect_mean_shift(
            previous_window=previous, current_window=current
        )

        print("\nDetected change points:")
        print(result)

    def detect_moving_change_points(self):

        values = pd.Series(
            [
                # Normal behavior
                5,
                4,
                6,
                5,
                4,
                5,
                # First degradation
                30,
                32,
                29,
                34,
                31,
                30,
                # Recovery
                5,
                4,
                6,
                5,
                4,
                5,
                # Second degradation
                20,
                22,
                19,
                24,
                21,
                23,
            ]
        )

        results = self.change_point_detector.detect_change_points(
            values=values, window_size=5, threshold=3.0, min_distance=5
        )

        print("-" * 60)
        print("\n --- Detected change points: ---")
        print(results[results["change_detected"]])
