import pandas as pd
import numpy as np


def seasonaly_baseline_1():
    # THEORY: Seasonal Baseline
    # A global average can be misleading when a metric follows a recurring
    # daily pattern. For example, CPU usage may naturally be higher during
    # business hours and lower at night.
    #
    # We build a separate baseline for each hour of the day, using historical
    # observations collected over multiple days.
    #
    # This allows us to compare the current value against the expected
    # behavior for that specific time window, reducing false positives
    # caused by normal daily fluctuations.

    # Same random data for each execution
    np.random.seed(42)

    # Generate 14 days of observation 
    timestamps = pd.date_range(
        start="2026-11-01",
        periods=14 * 24,
        freq="h"
    )

    data = []

    for timestamp in timestamps:
        hour = timestamp.hour

        if 8 <= hour <= 18:
            # Daily: mean 45%, mild deviation
            cpu = np.random.normal(loc=45, scale=5)
        else:
            # Nightly: mean 12%, small deviation
            cpu = np.random.normal(loc=12, scale=2)

        data.append({
            "timestamp": timestamp,
            "cpu_percent": max(0, cpu)
        })

    df = pd.DataFrame(data)

    # Stats for each hour of the day
    hourly_stats = (
        df.groupby(df["timestamp"].dt.hour)["cpu_percent"]
        .agg(["mean", "std"])
    )

    print(hourly_stats.round(2))

    # Indtrouce an anomaly at 3 AM

    baseline_03 = hourly_stats.loc[3]

    current_value = 20

    mean = baseline_03["mean"]
    std = baseline_03["std"]

    z_score = (current_value - mean) / std

    print(f"Historical mean: {mean:.2f}%")
    print(f"Historical std: {std:.2f}%")
    print(f"Current CPU: {current_value:.2f}%")
    print(f"Z-score: {z_score:.2f}")




def moving_average():
    # THEORY: Simple Moving Average (SMA)
    # A moving average smooths short-term fluctuations by calculating
    # the average of a fixed number of recent observations.
    #
    # A smaller window reacts faster to changes but is more sensitive
    # to noise. A larger window produces a smoother trend but reacts
    # more slowly to sudden changes.
    #
    # Moving averages are useful for identifying trends, but they do
    # not detect anomalies by themselves.
    cpu_values = [20, 22, 25, 28, 35, 42, 50]

    df = pd.DataFrame({
        "cpu_percent": cpu_values
    })

    df["moving_average"] = df["cpu_percent"].rolling(window=3).mean()

    print(df)


def moving_average_resilience_vs_stability():
    # THEORY: SMA vs EMA
    # SMA gives equal weight to all observations inside its window.
    # Older observations disappear completely when they leave the window.
    #
    # EMA (Exponential Moving Average) assigns more weight to recent
    # observations and progressively less weight to older ones.
    #
    # EMA reacts faster to recent changes, while SMA provides a more
    # uniform representation of the values inside its window.
    #
    # This comparison helps understand the trade-off between responsiveness
    # and stability when tracking operational metrics.
    cpu_values = [
        20, 22, 25, 28, 35,
        90, 90, 90, 35, 30
    ]

    df = pd.DataFrame({
        "cpu_percent": cpu_values
    })

    df["ma_3"] = df["cpu_percent"].rolling(window=3).mean()
    df["ma_5"] = df["cpu_percent"].rolling(window=5).mean()

    df["sma_3"] = df["cpu_percent"].rolling(window=3).mean()

    df["ema_3"] = df["cpu_percent"].ewm(span=3, adjust=False).mean()

    print(df)

def calculate_mad(historical_data):
     # THEORY: Median Absolute Deviation (MAD)
    # MAD measures the dispersion of observations around their median.
    #
    # Unlike standard deviation, MAD is resistant to extreme outliers,
    # because it uses the median instead of squared deviations.
    #
    # It is useful when historical data may already contain anomalies
    # that could distort traditional statistical measurements.
    series = pd.Series(historical_data)

    median = series.median()
    absolute_deviations = (series - median).abs()

    mad = absolute_deviations.median()

    return mad


def calculate_robust_z_score(current_value, historical_data):
     # THEORY: Robust Z-score
    # The Robust Z-score measures how far an observation is from the
    # historical median, using MAD as a robust measure of dispersion.
    #
    # The 0.6745 factor makes the score comparable to a standard Z-score
    # when the underlying distribution is approximately normal.
    #
    # It is particularly useful when the historical baseline contains
    # extreme values that could distort the mean and standard deviation.
    series = pd.Series(historical_data)

    median = series.median()
    mad = calculate_mad(historical_data=historical_data)

    if mad == 0:
        return None

    # This factor needs to make the measure comparable with standard deviation
    # 0.6745 is the number we use when data follow a normal distribution
    robust_z_score_factor = 0.6745

    return robust_z_score_factor * (current_value - median) / mad

def calculate_z_score(current_value, historical_data):
     # THEORY: Standard Z-score
    # The Z-score measures how many standard deviations an observation
    # is above or below the historical mean.
    #
    # A positive score indicates a value above the mean, while a negative
    # score indicates a value below it.
    #
    # It allows us to evaluate deviations relative to the normal
    # variability of a metric, rather than using fixed thresholds.
    #
    # It works best when the distribution is reasonably well-behaved
    # and the historical baseline is not heavily contaminated by outliers.
    df = pd.DataFrame({"value": historical_data})

    mean = df["value"].mean()
    std = df["value"].std()

    print(f"Mean: {mean}")
    print(f"Std: {std}")

    if std == 0:
        return None

    return (current_value - mean) / std


def z_score_2():
    # THEORY: Outlier Contamination
    # An extreme value inside the historical dataset can inflate both
    # the mean and standard deviation.
    #
    # This can make subsequent anomalies appear statistically normal
    # when using a standard Z-score.
    #
    # Comparing Standard Z-score and Robust Z-score demonstrates why
    # median-based statistics can be more reliable when historical
    # observations contain outliers.

    # Baseline without anomalies
    historical_clean = [
        98, 99, 100, 101, 102,
        99, 100, 101, 98, 102
    ]

    # Same baseline but with an anomaly
    historical_contaminated = historical_clean + [2000]

    current_value = 300

    print("Clean:")
    print("Standard Z-score:", calculate_z_score(current_value, historical_clean))
    print("Robust Z-score:", calculate_robust_z_score(current_value, historical_clean))

    print("\nContaminated:")
    print("Standard Z-score:", calculate_z_score(current_value, historical_contaminated))
    print("Robust Z-score:", calculate_robust_z_score(current_value, historical_contaminated))

def z_score():

    # THEORY: Historical Baseline Comparison
    # We calculate the mean and standard deviation using historical data
    # and compare a new observation against that baseline.
    #
    # The current observation must not be included in the historical
    # baseline, otherwise it could influence the statistics used to
    # evaluate itself.

    historical_data = [98, 102, 99, 101, 100, 97, 103, 100, 101, 99]

    current_value = 130

    df = pd.DataFrame({
        "latency_ms": historical_data
    })

    mean = df["latency_ms"].mean()
    std = df["latency_ms"].std()

    z_score = (current_value - mean) / std

    print("Mean:", mean)
    print("Std Dev:", std)
    print("Current:", current_value)
    print("Z-score:", z_score)

def std_var():

    # THEORY: Variance and Standard Deviation
    # Variance measures how dispersed observations are around their mean,
    # using squared deviations.
    #
    # Standard deviation is the square root of variance and expresses
    # dispersion in the same unit as the original metric.
    #
    # These measurements help distinguish between services with similar
    # average performance but different levels of predictability.

    service_a = [98, 99, 100, 101, 102]
    service_b = [50, 75, 100, 125, 150]

    df = pd.DataFrame({
        "service_a": service_a,
        "service_b": service_b
    })

    print("--- Statistics ---")

    print("Mean A:", df["service_a"].mean())
    print("Mean B:", df["service_b"].mean())

    print("Variance A:", df["service_a"].var())
    print("Variance B:", df["service_b"].var())

    print("Std Dev A:", df["service_a"].std())
    print("Std Dev B:", df["service_b"].std())


def mean_and_median():
    # THEORY: Mean, Median and Percentiles
    # Mean represents the arithmetic average and is sensitive to extreme
    # observations.
    #
    # Median (P50) represents the central observation and is more resistant
    # to extreme values.
    #
    # P95 and P99 describe tail latency: they help identify performance
    # degradation affecting a smaller percentage of requests.
    #
    # Comparing these statistics helps reveal situations where average
    # performance looks healthy while a subset of users experiences
    # significantly slower responses.

    durations = (
        [100] * 90 +
        [500] * 8 +
        [2000] * 2
    )

    
    df = pd.DataFrame({
        "duration_ms": durations
    })

    show_statistics(df, "First Dataset")

    durations_2 = [200] * 90 + [600] * 8 + [3000] * 2

    df_2 = pd.DataFrame({
        "duration_ms": durations_2
    })

    show_statistics(df_2, "Second Dataset")
    

def show_statistics(df, dataset_name: str):
    print("\n")
    print("+"*50)
    print("\n--- HTTP Latency Statistics ---")
    print(f"\n--- {dataset_name} ---")
    
    print("Mean:", df["duration_ms"].mean())
    print("Median:", df["duration_ms"].median())
    print("P50:", df["duration_ms"].quantile(0.50))
    print("P95:", df["duration_ms"].quantile(0.95))
    print("P99:", df["duration_ms"].quantile(0.99))
    print("Std Dev:", df["duration_ms"].std())

if __name__ == "__main__":
    print("Seasonaly baseline 1")
    seasonaly_baseline_1()