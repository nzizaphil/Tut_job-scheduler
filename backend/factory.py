"""
factory.py
ACTIVITY 4: Factory pattern.
Creates jobs from a type name + parameters, so callers never need to know
(or import) the concrete job classes.
"""


from typing import Any, Dict, List, Type

from models import Job, EmailJob, DataProcessingJob, PriorityJob


class JobFactory:

    # Maps a simple type name (as used in config files / API requests) to a class.
    _registry: Dict[str, Type[Job]] = {

        "email": EmailJob,

        "data": DataProcessingJob,

        "priority": PriorityJob,

    }


    @classmethod
    def register(cls, name: str, job_class: Type[Job]) -> None:

        """Plug in a new job type without editing this file."""

        cls._registry[name] = job_class


    @classmethod
    def create(cls, job_type: str, **params: Any) -> Job:

        job_class = cls._registry.get(job_type)

        if job_class is None:

            known = ", ".join(cls._registry)

            raise ValueError(f"Unknown job type '{job_type}'. Known types: {known}")

        try:

            return job_class(**params)

        except TypeError as e:

            raise ValueError(f"Bad parameters for '{job_type}' job: {e}") from e


    @classmethod
    def from_config(cls, configs: List[Dict[str, Any]]) -> List[Job]:

        """Build jobs from a list of dicts, e.g. loaded from JSON."""

        jobs: List[Job] = []

        for cfg in configs:

            params = dict(cfg)               # copy, so the original isn't changed

            job_type = params.pop("type")    # everything else goes to the constructor

            jobs.append(cls.create(job_type, **params))

        return jobs
