import inspect
from functools import wraps

def tool(func):
    """
    Decorator to register a function as a tool.
    In a real system, this might add metadata for the LLM.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    
    # Attach metadata to the wrapper function
    wrapper._is_tool = True
    wrapper._name = func.__name__
    wrapper._doc = inspect.getdoc(func)
    wrapper._sig = inspect.signature(func)
    
    return wrapper
