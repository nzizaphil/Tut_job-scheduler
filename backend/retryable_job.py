"""
retryable_job.py
ACTIVITY 6: RetryableJob — a flaky job (e.g. calling an unreliable external API)
that declares its own retry policy. The Executor reads that policy and retries.

This lives in its own module and registers itself with JobFactory, so neither
models.py nor factory.py had to be edited to add it (Open/Closed principle).
"""


import random

from errors import JobExecutionError

from factory import JobFactory

from models import Job


class RetryableJob(Job):

    """Child class: may fail, but is allowed to be retried with backoff."""

    def __init__(self, job_id: int, description: str, max_retries: int = 3,
                 failure_rate: float = 0.5, base_delay: float = 0.5) -> None:

        super().__init__(job_id, description)

        if max_retries < 0:

            raise ValueError("max_retries cannot be negative")

        if not 0 <= failure_rate <= 1:

            raise ValueError("failure_rate must be between 0 and 1")

        self.max_retries = max_retries      # extra attempts after the first one

        self.failure_rate = failure_rate    # chance each attempt fails (simulation)

        self.base_delay = base_delay        # seconds to wait before the first retry


    def retry_delay(self, attempt: int) -> float:

        """Exponential backoff: 0.5s, 1s, 2s, ... gives a struggling service time to recover."""

        return self.base_delay * (2 ** (attempt - 1))


    def execute(self) -> None:

        print(f"Calling flaky service for '{self.description}'...")

        if random.random() < self.failure_rate:

            raise JobExecutionError(self.job_id, "Flaky service timed out")

        self.log("Flaky service call succeeded")


    def __repr__(self) -> str:

        return f"<RetryableJob id={self.job_id} max_retries={self.max_retries} status={self.status}>"


# Plug the new type into the factory — this is what JobFactory.register() is for.
JobFactory.register("retryable", RetryableJob)
