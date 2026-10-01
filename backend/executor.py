"""
executor.py
Runs jobs concurrently using threads to simulate a scheduler.
- Random delay: simulates work
- Random failure: exercises exception handling
- Retry loop (Activity 6): jobs with max_retries are retried with backoff
"""


import threading

import time

import random

from datetime import datetime

from typing import List

from errors import JobExecutionError

from models import Job


class Executor:

    # FIX (executor.py): added 'manager' parameter so Executor can update
    # job statuses in TaskManager after each job succeeds or fails.
    # Previously Executor had no reference to manager, so statuses were never updated.
    def __init__(self, jobs: List[Job], manager) -> None:

        self.jobs = jobs

        self.manager = manager


    def _ts(self) -> str:

        return datetime.now().strftime("%H:%M:%S")


    def run_job(self, job: Job) -> None:

        print(f"[{self._ts()}] Executing job {job.job_id} ({job.description})...")

        job.log("Execution started")  # ACTIVITY 3

        # ACTIVITY 5: lifecycle begins — mark as running and start the timer.
        self.manager.update_status(job, "running")

        job.start()

        # ACTIVITY 6: jobs that don't declare max_retries get 0 retries (1 attempt),
        # so EmailJob, DataProcessingJob and PriorityJob behave exactly as before.
        max_retries = getattr(job, "max_retries", 0)

        try:

            for attempt in range(1, max_retries + 2):

                try:

                    self._attempt(job)

                    break  # success -> leave the retry loop

                except JobExecutionError as e:

                    if attempt > max_retries:

                        raise  # out of retries -> handled below as a real failure

                    delay = job.retry_delay(attempt)

                    job.log(f"Attempt {attempt} failed ({e}); retrying in {delay:.1f}s")

                    print(f"[{self._ts()}] Job {job.job_id} attempt {attempt} failed, "
                          f"retrying in {delay:.1f}s...")

                    time.sleep(delay)

            # FIX (executor.py): update manager AFTER execute() succeeds,
            # so the job moves from "running" -> "completed" in TaskManager.
            self.manager.update_status(job, "completed")

            print(f"[{self._ts()}] Completed job {job.job_id}.")

        except JobExecutionError as e:

            # FIX (executor.py): mark failed jobs in manager so they appear
            # in the summary under "failed".
            job.log(f"Error: {e}")  # ACTIVITY 3

            self.manager.update_status(job, "failed")

            print(f"[{self._ts()}] Error in job {e.job_id}: {e}")

        finally:

            # ACTIVITY 5: 'finally' runs on success AND failure,
            # so every job gets a duration (including time spent retrying).
            job.end()


    def _attempt(self, job: Job) -> None:

        """ACTIVITY 6: one try at running the job (simulated work + possible failure)."""

        time.sleep(random.uniform(1, 3))

        if random.random() < 0.2:  # ~20% simulated failure

            raise JobExecutionError(job.job_id)

        job.execute()


    def run(self) -> None:

        threads: List[threading.Thread] = []

        for job in self.jobs:

            t = threading.Thread(target=self.run_job, args=(job,))

            threads.append(t)

            t.start()


        for t in threads:

            t.join()