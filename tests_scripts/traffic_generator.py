import argparse
import json
import random
import time
import uuid
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(
        description="Random HTTP traffic generator for AIOps Lab"
    )
    parser.add_argument(
        "port",
        type=int,
        help="Port on which the FastAPI application is running",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Application host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=10,
        help="Seconds between cycles (default: 10)",
    )
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    known_job_ids = []

    print(f"Traffic generator started: {base_url}")
    print(f"Interval: {args.interval}s")
    print("Press Ctrl+C to stop.\n")

    def call_endpoint(method, path, payload=None):
        url = f"{base_url}{path}"
        headers = {}

        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        start = time.perf_counter()

        try:
            with urlopen(request, timeout=5) as response:
                body = response.read().decode("utf-8")
                status = response.status

        except HTTPError as error:
            status = error.code
            body = error.read().decode("utf-8")

        except (URLError, TimeoutError, OSError) as error:
            duration = time.perf_counter() - start
            print(
                f"[{datetime.now():%H:%M:%S}] "
                f"{method} {path} -> CONNECTION ERROR "
                f"({duration:.3f}s): {error}",
                flush=True,
            )
            return None

        duration = time.perf_counter() - start

        print(
            f"[{datetime.now():%H:%M:%S}] "
            f"{method} {path} -> {status} "
            f"({duration:.3f}s)",
            flush=True,
        )

        return status, body

    def create_job():
        numbers = [random.randint(1, 100) for _ in range(random.randint(2, 8))]

        result = call_endpoint(
            "POST",
            "/jobs",
            {"numbers": numbers},
        )

        if result and 200 <= result[0] < 300:
            try:
                job_id = json.loads(result[1])
                if isinstance(job_id, str):
                    known_job_ids.append(job_id)
                    print(f"    Created job: {job_id}", flush=True)
            except json.JSONDecodeError:
                pass

    def get_jobs():
        call_endpoint("GET", "/jobs")

    def get_job():
        # Mostly query existing jobs, but occasionally simulate a 404.
        if known_job_ids and random.random() < 0.8:
            job_id = random.choice(known_job_ids)
        else:
            job_id = str(uuid.uuid4())

        call_endpoint("GET", f"/jobs/{job_id}")

    actions = [create_job, get_jobs, get_job]

    try:
        while True:
            print(
                f"\n--- New cycle: {datetime.now():%H:%M:%S} ---",
                flush=True,
            )

            # Each cycle executes one to three randomly selected actions.
            number_of_requests = random.randint(1, 3)

            for _ in range(number_of_requests):
                random.choice(actions)()

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nTraffic generator stopped.")


if __name__ == "__main__":
    main()
