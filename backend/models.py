"""
models.py
Defines the Job hierarchy (parent + child classes).
Polymorphism: each subclass implements its own execute().
"""


class Job:

    """Parent/base class shared by all job types."""

    def __init__(self, job_id: int, description: str) -> None:

        self.job_id = job_id

        self.description = description

        self.status = "pending"


    def execute(self) -> None:

        """Must be overridden by subclasses."""

        raise NotImplementedError("Each job must implement its own execution logic.")


    def mark_done(self) -> None:

        self.status = "completed"


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


    def __repr__(self) -> str:

        return f"<PriorityJob id={self.job_id} priority={self.priority} status={self.status}>"