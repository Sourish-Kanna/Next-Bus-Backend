import functools
import asyncio

def log_activity(func):
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # print("Decorator: sync Function is being called")
        x = func(*args, **kwargs)
        # print(f"Decorator: Function returned {x}")
        return x

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # print("Decorator: async Function is being called")
        x = await func(*args, **kwargs)
        # print(f"Decorator: Function returned {x}")
        return x

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
