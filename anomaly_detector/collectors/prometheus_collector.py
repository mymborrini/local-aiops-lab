import requests
import pandas as pd


class PrometheusCollector:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def query_range(
        self, query: str, start: str, end: str, step: str = "15s"
    ) -> pd.DataFrame:
        url = f"{self.base_url}/api/v1/query_range"

        params = {"query": query, "start": start, "end": end, "step": step}

        response = self.session.get(url=url, params=params, timeout=10)

        response.raise_for_status()

        payload = response.json()

        if payload.get("status") != "success":
            raise RuntimeError(f"Prometheus query failed: {payload}")

        results = payload["data"]["result"]

        rows = []

        for result in results:
            labels = result["metric"]

            for timestamp, value in result["values"]:
                rows.append(
                    {
                        "timestamp": pd.to_datetime(
                            float(timestamp), unit="s", utc=True
                        ),
                        "value": float(value),
                        "labels": labels,
                    }
                )

        df = pd.DataFrame(rows)

        if not df.empty:
            # Avoid infinity values to change statistics
            df["value"] = pd.to_numeric(df["value"], errors="coerce")

            df["value"] = df["value"].replace(
                [float("inf"), float("-inf")], float("nan")
            )

            df = df.dropna(subset=["timestamp", "value"])

            df = df.sort_values("timestamp").reset_index(drop=True)

        return df
