"""
app.py
Build a few jobs, register them, run them, print a summary.
"""


from models import EmailJob, DataProcessingJob, PriorityJob

from task_manager import TaskManager

from executor import Executor

from itertools import groupby


def build_jobs():

    return [

        EmailJob(1, "user@example.com"),

        DataProcessingJob(2, "dataset_A"),

        EmailJob(3, "admin@example.com"),

        DataProcessingJob(4, "dataset_B"),

        # ACTIVITY 2: priority jobs (1 = highest, 5 = lowest)
        PriorityJob(5, "Critical security alert", priority=1),

        PriorityJob(6, "Nightly log cleanup", priority=5),

    ]


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
    for priority, group in groupby(jobs, key=by_priority):

        print(f"\n--- Priority {priority} jobs ---")

        Executor(list(group), manager).run()


    print("\n=== SUMMARY ===")

    print(f"Pending:   {len(manager.get_jobs_by_status('pending'))}")

    print(f"Completed: {len(manager.get_jobs_by_status('completed'))}")

    # FIX (app.py): added 'failed' count to summary so failures are visible.
    print(f"Failed:    {len(manager.get_jobs_by_status('failed'))}")