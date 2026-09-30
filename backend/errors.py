""" 
errors.py 
Custom exception — clearer than using generic Exception everywhere. 
""" 

 
class JobExecutionError(Exception): 

    """Raised when a job fails during execution.""" 


    def __init__(self, job_id: int, message: str = "Job execution failed") -> None: 

        self.job_id = job_id 

        super().__init__(message) 