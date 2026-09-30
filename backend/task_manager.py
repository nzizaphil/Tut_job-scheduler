"""
task_manager.py
Tracks jobs by status using defaultdict(list) to avoid KeyErrors and boilerplate.
"""


from collections import defaultdict

from typing import Dict, List

from models import Job


class TaskManager:

    def __init__(self) -> None:

        self.jobs_by_status: Dict[str, List[Job]] = defaultdict(list)


    def add_job(self, job: Job) -> None:

        self.jobs_by_status[job.status].append(job)


    def get_all(self) -> Dict[str, List[Job]]:

        return self.jobs_by_status


    def get_jobs_by_status(self, status: str) -> List[Job]:

        return list(self.jobs_by_status.get(status, []))


    # FIX (task_manager.py): new method to move a job between status buckets.
    # Removes job from its current bucket, updates job.status, adds to new bucket.
    # Called by Executor after each job finishes (success or failure).
    def update_status(self, job: Job, new_status: str) -> None:

        old_bucket = self.jobs_by_status.get(job.status, [])

        if job in old_bucket:

            old_bucket.remove(job)

        job.status = new_status

        self.jobs_by_status[new_status].append(job)