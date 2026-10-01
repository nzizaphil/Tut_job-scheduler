"""
ACTIVITY 7: unit tests that GitHub Actions runs on every push and pull request.

The Executor uses random delays and random failures, so the tests replace
time.sleep and random.random with fakes. That makes every run predictable:
a test should pass or fail because of the code, never because of luck.
"""


import random
import time

import pytest

from errors import JobExecutionError
from executor import Executor
from factory import JobFactory
from models import Job, EmailJob, DataProcessingJob, PriorityJob
from retryable_job import RetryableJob
from task_manager import TaskManager


# ---------- helpers ----------

@pytest.fixture
def no_sleep(monkeypatch):
    """Skip all waiting, so the tests run in milliseconds."""
    monkeypatch.setattr(time, "sleep", lambda seconds: None)


def fake_random(monkeypatch, values):
    """Make random.random() return these values in order."""
    it = iter(values)
    monkeypatch.setattr(random, "random", lambda: next(it))


def run_one(job):
    manager = TaskManager()
    manager.add_job(job)
    Executor([job], manager).run()
    return manager


# ---------- Activity 4: abstraction + factory ----------

def test_job_is_abstract():
    with pytest.raises(TypeError):
        Job(1, "can't create the base class")


def test_factory_builds_correct_types():
    jobs = JobFactory.from_config([
        {"type": "email", "job_id": 1, "recipient": "a@b.com"},
        {"type": "data", "job_id": 2, "dataset": "ds"},
        {"type": "priority", "job_id": 3, "description": "p", "priority": 1},
        {"type": "retryable", "job_id": 4, "description": "r"},
    ])
    assert [type(j) for j in jobs] == [EmailJob, DataProcessingJob, PriorityJob, RetryableJob]


def test_factory_rejects_unknown_type():
    with pytest.raises(ValueError, match="Unknown job type"):
        JobFactory.create("sms", job_id=9)


def test_factory_rejects_bad_parameters():
    with pytest.raises(ValueError, match="Bad parameters"):
        JobFactory.create("email", job_id=9)  # missing recipient


# ---------- Activity 2: priority ----------

@pytest.mark.parametrize("bad", [0, 6])
def test_priority_must_be_1_to_5(bad):
    with pytest.raises(ValueError):
        PriorityJob(1, "x", priority=bad)


# ---------- Activity 3: encapsulation ----------

def test_logs_are_private_and_read_only():
    job = EmailJob(1, "a@b.com")
    with pytest.raises(AttributeError):
        job.__logs  # name-mangled, not reachable from outside
    job.get_logs().append("tampered")
    assert "tampered" not in job.get_logs()


def test_invalid_status_is_rejected():
    job = EmailJob(1, "a@b.com")
    with pytest.raises(ValueError):
        job.status = "banana"


# ---------- Activity 5: timing ----------

def test_duration_lifecycle():
    job = EmailJob(1, "a@b.com")
    assert job.duration is None
    with pytest.raises(RuntimeError):
        job.end()  # end() before start()
    job.start()
    job.end()
    assert job.duration >= 0


# ---------- TaskManager ----------

def test_update_status_moves_job_between_buckets():
    manager = TaskManager()
    job = EmailJob(1, "a@b.com")
    manager.add_job(job)
    manager.update_status(job, "completed")
    assert manager.get_jobs_by_status("pending") == []
    assert manager.get_jobs_by_status("completed") == [job]


# ---------- Executor + Activity 6: retries ----------

def test_successful_job_is_completed_and_timed(no_sleep, monkeypatch):
    fake_random(monkeypatch, [0.99])  # executor's 20% failure check passes
    job = EmailJob(1, "a@b.com")
    manager = run_one(job)
    assert job.status == "completed"
    assert manager.get_jobs_by_status("completed") == [job]
    assert job.duration is not None


def test_normal_job_is_not_retried(no_sleep, monkeypatch):
    fake_random(monkeypatch, [0.0])  # executor's failure check fails
    job = EmailJob(1, "a@b.com")
    run_one(job)
    assert job.status == "failed"
    assert not any("Attempt" in line for line in job.get_logs())


def test_retryable_job_recovers(no_sleep, monkeypatch):
    # attempt 1: executor ok (0.99), service fails (0.0)
    # attempt 2: executor ok (0.99), service ok (0.99)
    fake_random(monkeypatch, [0.99, 0.0, 0.99, 0.99])
    job = RetryableJob(7, "flaky", max_retries=3, failure_rate=0.5)
    run_one(job)
    assert job.status == "completed"
    assert sum("Attempt" in line for line in job.get_logs()) == 1


def test_retryable_job_gives_up_after_max_retries(no_sleep):
    job = RetryableJob(7, "always fails", max_retries=2, failure_rate=1.0)
    run_one(job)
    assert job.status == "failed"
    assert sum("Attempt" in line for line in job.get_logs()) == 2  # 3 tries = 2 retries


def test_exponential_backoff():
    job = RetryableJob(7, "r", base_delay=0.5)
    assert [job.retry_delay(n) for n in (1, 2, 3)] == [0.5, 1.0, 2.0]
