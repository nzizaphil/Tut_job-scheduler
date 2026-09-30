"""
models.py
Defines the Job hierarchy (parent + child classes).
Polymorphism: each subclass implements its own execute().
Encapsulation (Activity 3): status and logs are private, accessed via methods.
"""


from datetime import datetime

from typing import List


class Job:

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

    # -------------------------------------------------------------------


    def execute(self) -> None:

        """Must be overridden by subclasses."""

        raise NotImplementedError("Each job must implement its own execution logic.")


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