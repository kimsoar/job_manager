job_registry = []

def job(name):
    def decorator(func):
        job_registry.append((name, func))
        return func
    return decorator

def get_all_jobs():
    return job_registry

def get_job_by_name(names):
    return [(name, func) for name, func in job_registry if name in names]
