
import argparse
import json
import random
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def percentile(values, p):
    if not values:
        return 0.0

    ordered = sorted(values)
    index = min(int((len(ordered) - 1) * p), len(ordered) - 1)
    return ordered[index]


def send_request(base_url, timeout):
    numbers = [
        random.randint(1, 100)
        for _ in range(random.randint(2, 8))
    ]

    payload = json.dumps({"numbers": numbers}).encode("utf-8")

    request = Request(
        f"{base_url}/jobs",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            status = response.status

    except HTTPError as error:
        status = error.code
        body = error.read().decode("utf-8")

    except (URLError, TimeoutError, OSError) as error:
        return {
            "status": "CONNECTION_ERROR",
            "duration": time.perf_counter() - start,
            "error": str(error),
        }

    duration = time.perf_counter() - start

    job_id = None

    if 200 <= status < 300:
        try:
            parsed = json.loads(body)
            if isinstance(parsed, str):
                job_id = parsed
        except json.JSONDecodeError:
            pass

    return {
        "status": status,
        "duration": duration,
        "job_id": job_id,
    }


def check_job_status(base_url, job_id, timeout=5):
    request = Request(
        f"{base_url}/jobs/{job_id}",
        method="GET",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    except (HTTPError, URLError, TimeoutError, OSError):
        return None


def monitor_jobs(base_url, job_ids, max_wait=60, interval=2):
    print("\n" + "=" * 45)
    print("ASYNC JOB PROCESSING")
    print("=" * 45)

    statuses = {
        job_id: None
        for job_id in job_ids
    }

    start = time.perf_counter()

    while time.perf_counter() - start < max_wait:

        for job_id in job_ids:
            if statuses[job_id] in ("COMPLETED", "FAILED"):
                continue

            result = check_job_status(base_url, job_id)

            if result:
                statuses[job_id] = result.get("status")

        completed = sum(
            status == "COMPLETED"
            for status in statuses.values()
        )

        failed = sum(
            status == "FAILED"
            for status in statuses.values()
        )

        pending = sum(
            status in (None, "PENDING", "RUNNING")
            for status in statuses.values()
        )

        print(
            f"Completed: {completed}/{len(job_ids)} | "
            f"Failed: {failed} | "
            f"Pending/Running/Unknown: {pending}",
            flush=True,
        )

        if completed + failed == len(job_ids):
            break

        time.sleep(interval)

    duration = time.perf_counter() - start

    print("\nFinal job status:")
    print(f"  COMPLETED: {completed}")
    print(f"  FAILED:    {failed}")
    print(f"  Remaining: {pending}")
    print(f"  Duration:  {duration:.2f}s")

    return statuses



def main():
    parser = argparse.ArgumentParser(
        description="Controlled load test for AIOps Lab"
    )

    parser.add_argument("port", type=int)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=10)

    args = parser.parse_args()

    if args.requests < 1 or args.concurrency < 1:
        parser.error("Requests and concurrency must be positive")

    base_url = f"http://{args.host}:{args.port}"

    print("AIOps Lab - Load Test")
    print(f"Target:       {base_url}/jobs")
    print(f"Requests:     {args.requests}")
    print(f"Concurrency:  {args.concurrency}")
    print(f"Timeout:      {args.timeout}s")
    print("-" * 45)

    start = time.perf_counter()

    results = []

    with ThreadPoolExecutor(
        max_workers=args.concurrency
    ) as executor:

        futures = [
            executor.submit(send_request, base_url, args.timeout)
            for _ in range(args.requests)
        ]

        for completed, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)

            print(
                f"[{completed:03}/{args.requests}] "
                f"{result['status']} "
                f"({result['duration']:.3f}s)",
                flush=True,
            )

    total_duration = time.perf_counter() - start

    durations = [r["duration"] for r in results]
    successful = [r for r in results if isinstance(r["status"], int)
                  and 200 <= r["status"] < 300]

    status_counts = Counter(str(r["status"]) for r in results)

    job_ids = [
        r["job_id"]
        for r in successful
        if r["job_id"] is not None
    ]

    print("\n" + "=" * 45)
    print("LOAD TEST RESULTS")
    print("=" * 45)

    print(f"Total requests:       {len(results)}")
    print(f"Successful requests:  {len(successful)}")
    print(f"Failed requests:      {len(results) - len(successful)}")
    print(f"Success rate:         {len(successful) / len(results) * 100:.2f}%")
    print(f"Total duration:       {total_duration:.2f}s")
    print(f"Throughput:           {len(results) / total_duration:.2f} req/s")

    print("\nHTTP status distribution:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print("\nLatency:")
    print(f"  Average: {sum(durations) / len(durations):.3f}s")
    print(f"  p95:     {percentile(durations, 0.95):.3f}s")
    print(f"  p99:     {percentile(durations, 0.99):.3f}s")
    print(f"  Max:     {max(durations):.3f}s")

    print(f"\nJob IDs received: {len(job_ids)}")

    output = {
        "timestamp": datetime.now().isoformat(),
        "requests": len(results),
        "successful": len(successful),
        "job_ids": job_ids,
    }

    with open("load_test_results.json", "w") as file:
        json.dump(output, file, indent=2)

    print("Results saved to load_test_results.json")

    if job_ids:
        monitor_jobs(base_url, job_ids)


if __name__ == "__main__":
    print("Start heavy load")
    main()
