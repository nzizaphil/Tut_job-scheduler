"""
models.py
Defines the Job hierarchy (parent + child classes).
Polymorphism: each subclass implements its own execute().
Encapsulation (Activity 3): status and logs are private, accessed via methods.
Abstraction (Activity 4): Job is an abstract base class; it can't be created directly.
Lifecycle (Activity 5): start() / end() record how long each job takes.
"""


from abc import ABC, abstractmethod

import time

from datetime import datetime

from typing import List, Optional


# ACTIVITY 4: inheriting from ABC makes Job abstract.
class Job(ABC):

    """Parent/base class shared by all job types."""

    # ACTIVITY 3: the only statuses a job is allowed to have.
    VALID_STATUSES = ("pending", "running", "completed", "failed")


    def __init__(self, job_id: int, description: str) -> None:

        self.job_id = job_id

        self.description = description

        # ACTIVITY 3: double underscore = private (Python name-mangles these to
        # _Job__status / _Job__logs), so outside code can't touch them directly.
        self.__status = "pending"

        self.__logs: List[str] = []

        # ACTIVITY 5: private timing fields, filled in by start() / end().
        self.__started_at: Optional[float] = None

        self.__ended_at: Optional[float] = None

        self.log("Job created (status: pending)")


    # ---------- ACTIVITY 3: controlled access to private data ----------

    @property
    def status(self) -> str:

        """Read-only view of the private status."""

        return self.__status


    @status.setter
    def status(self, new_status: str) -> None:

        """Every status change is validated and logged automatically."""

        if new_status not in self.VALID_STATUSES:

            raise ValueError(f"Invalid status '{new_status}' for job {self.job_id}")

        self.log(f"Status: {self.__status} -> {new_status}")

        self.__status = new_status


    def log(self, message: str) -> None:

        """Add a timestamped entry to this job's private log."""

        ts = datetime.now().strftime("%H:%M:%S")

        self.__logs.append(f"[{ts}] {message}")


    def get_logs(self) -> List[str]:

        """Return a COPY, so callers can read logs but never modify the real list."""

        return list(self.__logs)


    # ---------- ACTIVITY 5: lifecycle timing ----------

    def start(self) -> None:

        """Call when the job begins running."""

        self.__started_at = time.perf_counter()  # monotonic clock, ideal for durations

        self.__ended_at = None

        self.log("Timer started")


    def end(self) -> None:

        """Call when the job finishes (success OR failure)."""

        if self.__started_at is None:

            raise RuntimeError(f"Job {self.job_id}: end() called before start()")

        self.__ended_at = time.perf_counter()

        self.log(f"Timer stopped after {self.duration:.2f}s")


    @property
    def duration(self) -> Optional[float]:

        """Seconds between start() and end(), or None if the job hasn't finished."""

        if self.__started_at is None or self.__ended_at is None:

            return None

        return self.__ended_at - self.__started_at

    # -------------------------------------------------------------------


    # ACTIVITY 4: @abstractmethod forces every subclass to implement execute().
    # Python now refuses to create Job(...) or any subclass that forgets it.
    @abstractmethod
    def execute(self) -> None:

        """Each job type defines its own execution logic."""


    def mark_done(self) -> None:

        self.status = "completed"  # goes through the validated setter


    def __repr__(self) -> str:

        return f"<Job id={self.job_id} status={self.status} desc='{self.description}'>"



class EmailJob(Job):

    """Child class: sends an email."""

    def __init__(self, job_id: int, recipient: str) -> None:

        # super() calls parent constructor (DRY)

        super().__init__(job_id, f"Send email to {recipient}")

        self.recipient = recipient


    def execute(self) -> None:

        print(f"Sending email to {self.recipient}...")

        self.log(f"Email sent to {self.recipient}")  # ACTIVITY 3

        # FIX (models.py): removed self.mark_done() here.
        # Previously mark_done() set job.status="completed" inside execute(),
        # so update_status() in executor.py searched the wrong bucket and
        # added a duplicate — causing Pending:4, Completed:4 in the summary.
        # Status is now managed exclusively by TaskManager.update_status().



class DataProcessingJob(Job):

    """Child class: processes a dataset."""

    def __init__(self, job_id: int, dataset: str) -> None:

        super().__init__(job_id, f"Process dataset {dataset}")

        self.dataset = dataset


    def execute(self) -> None:

        print(f"Processing dataset {self.dataset}...")

        self.log(f"Dataset {self.dataset} processed")  # ACTIVITY 3

        # FIX (models.py): removed self.mark_done() here — same reason as EmailJob above.



# ACTIVITY 2: PriorityJob — extends Job WITHOUT modifying the base class.
class PriorityJob(Job):

    """Child class: a job with a priority level (1 = highest, 5 = lowest)."""

    def __init__(self, job_id: int, description: str, priority: int = 3) -> None:

        super().__init__(job_id, description)

        if not 1 <= priority <= 5:

            raise ValueError("priority must be between 1 (highest) and 5 (lowest)")

        self.priority = priority


    def execute(self) -> None:

        print(f"[PRIORITY {self.priority}] Handling {self.description}...")

        self.log(f"Handled with priority {self.priority}")  # ACTIVITY 3


    def __repr__(self) -> str:

        return f"<PriorityJob id={self.job_id} priority={self.priority} status={self.status}>"