"""
app.py
Build a few jobs, register them, run them, print a summary.
"""


import io

import json

import os

import sys

import time

from contextlib import redirect_stdout

from itertools import groupby

# ACTIVITY 4: app.py no longer imports EmailJob, DataProcessingJob, etc.
# It only talks to the factory, so it's decoupled from the concrete classes.
from factory import JobFactory

# ACTIVITY 6: importing this module registers the "retryable" job type
# with the factory (plugin style) — factory.py itself didn't change.
import retryable_job  # noqa: F401

from task_manager import TaskManager

from executor import Executor


CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs.json")


def build_jobs():

    # ACTIVITY 4: job definitions now come from a config file, not hardcoded classes.
    with open(CONFIG_PATH) as f:

        configs = json.load(f)

    return JobFactory.from_config(configs)


# ACTIVITY 2: jobs without a priority attribute are treated as normal (3).
DEFAULT_PRIORITY = 3


def by_priority(job) -> int:

    return getattr(job, "priority", DEFAULT_PRIORITY)


def run_scheduler():

    """Create, register and run all jobs. Returns everything the reports need."""

    # ACTIVITY 2: sort so higher-priority jobs come first.
    # sorted() is stable, so jobs with equal priority keep their original order.
    jobs = sorted(build_jobs(), key=by_priority)


    manager = TaskManager()

    for job in jobs:

        manager.add_job(job)  # all start as 'pending'


    # FIX (app.py): pass 'manager' to Executor so it can update statuses.
    # ACTIVITY 2: run jobs in priority "waves". Jobs in the same priority level
    # run concurrently, but a lower-priority wave only starts once the
    # higher-priority wave has finished.
    wall_start = time.perf_counter()  # ACTIVITY 5: total real time for the whole run

    wave_offsets = {}  # ACTIVITY 8: when each wave started, for the dashboard timeline

    for priority, group in groupby(jobs, key=by_priority):

        wave_offsets[priority] = time.perf_counter() - wall_start

        print(f"\n--- Priority {priority} jobs ---")

        Executor(list(group), manager).run()

    wall_time = time.perf_counter() - wall_start

    return jobs, manager, wall_time, wave_offsets


def print_report(jobs, manager, wall_time) -> None:

    """Human-readable output (used by `python3 app.py`, GET / and CI)."""

    print("\n=== SUMMARY ===")

    print(f"Pending:   {len(manager.get_jobs_by_status('pending'))}")

    print(f"Completed: {len(manager.get_jobs_by_status('completed'))}")

    # FIX (app.py): added 'failed' count to summary so failures are visible.
    print(f"Failed:    {len(manager.get_jobs_by_status('failed'))}")


    # ACTIVITY 5: timing report.
    print("\n=== TIMING ===")

    for job in sorted(jobs, key=lambda j: j.job_id):

        print(f"Job {job.job_id}: {job.duration:.2f}s ({job.status})")

    total_job_time = sum(job.duration for job in jobs)

    slowest = max(jobs, key=lambda j: j.duration)

    print(f"Average job time:   {total_job_time / len(jobs):.2f}s")

    print(f"Slowest job:        {slowest.job_id} ({slowest.duration:.2f}s)")

    print(f"Sum of job times:   {total_job_time:.2f}s")

    print(f"Actual wall time:   {wall_time:.2f}s  <- less than the sum thanks to threads")


    # ACTIVITY 3: read each job's private log through its public method.
    print("\n=== JOB LOGS ===")

    for job in sorted(jobs, key=lambda j: j.job_id):

        print(f"Job {job.job_id} ({job.status}):")

        for entry in job.get_logs():

            print(f"  {entry}")


def json_report(jobs, manager, wall_time, wave_offsets, console: str) -> dict:

    """ACTIVITY 8: machine-readable output that Express saves to MongoDB."""

    return {

        "summary": {

            status: len(manager.get_jobs_by_status(status))

            for status in ("pending", "completed", "failed")

        },

        "wallTime": round(wall_time, 3),

        "totalJobTime": round(sum(job.duration for job in jobs), 3),

        "jobs": [

            {

                "jobId": job.job_id,

                "type": type(job).__name__,

                "description": job.description,

                "status": job.status,

                "priority": by_priority(job),

                "maxRetries": getattr(job, "max_retries", 0),

                "startOffset": round(wave_offsets[by_priority(job)], 3),

                "duration": round(job.duration, 3),

                "logs": job.get_logs(),

            }

            for job in sorted(jobs, key=lambda j: j.job_id)

        ],

        "console": console.strip().splitlines(),

    }


if __name__ == "__main__":

    if "--json" in sys.argv:

        # ACTIVITY 8: capture the threads' print() output so stdout contains
        # ONLY valid JSON — the console text is kept inside the JSON instead.
        buffer = io.StringIO()

        with redirect_stdout(buffer):

            jobs, manager, wall_time, wave_offsets = run_scheduler()

        print(json.dumps(json_report(jobs, manager, wall_time, wave_offsets, buffer.getvalue())))

    else:

        jobs, manager, wall_time, _ = run_scheduler()

        print_report(jobs, manager, wall_time)