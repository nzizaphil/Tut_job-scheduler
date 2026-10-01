"""
app.py
Build a few jobs, register them, run them, print a summary.
"""


import json

import os

import time

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


if __name__ == "__main__":

    # ACTIVITY 2: sort so higher-priority jobs come first.
    # sorted() is stable, so jobs with equal priority keep their original order.
    jobs = sorted(build_jobs(), key=by_priority)


    manager = TaskManager()

    for job in jobs:

        manager.add_job(job)  # all start as 'pending'


    # FIX (app.py): pass 'manager' to Executor so it can update statuses.
    # Previously Executor(jobs).run() had no manager reference — statuses never changed.
    # ACTIVITY 2: run jobs in priority "waves". Jobs in the same priority level
    # run concurrently, but a lower-priority wave only starts once the
    # higher-priority wave has finished.
    wall_start = time.perf_counter()  # ACTIVITY 5: total real time for the whole run

    for priority, group in groupby(jobs, key=by_priority):

        print(f"\n--- Priority {priority} jobs ---")

        Executor(list(group), manager).run()

    wall_time = time.perf_counter() - wall_start


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