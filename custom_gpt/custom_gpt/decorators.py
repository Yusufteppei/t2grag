import time
from functools import wraps
import logging
from accounts.models import Usage

def measure_latency_and_tokens(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Start measuring time
        start_time = time.time()
        
        # Call the function
        result = func(*args, **kwargs)
        
        # End measuring time
        end_time = time.time()
        latency = end_time - start_time
        
        # Assuming the function returns a dictionary with token usage info
        completion_tokens = result.usage.completion_tokens
        prompt_tokens = result.usage.prompt_tokens
        
        # Log the latency and token usage
        logging.info(f"Function '{func.__name__}' executed in {latency:.2f} seconds.")
        logging.info(f"Token usage: {completion_tokens}, {prompt_tokens}")
        
        # Create object
        Usage.objects.create(user=args[0].user, latency=latency, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)

        return result
    return wrapper