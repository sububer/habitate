from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Tuple
import time
import asyncio
import redis

app = FastAPI()
cache = redis.Redis(host='redis', port=6379)

class FibonacciResponse(BaseModel):
    x: int
    fib_x: int
    time_elapsed: str

async def fibonacci_iterative(n: int) -> int:
    if n <= 1:
        return n
    if cache.get(n):
        return int(cache.get(n))
    
    #not in cache, compute and store in cache
    a, b = 0, 1
    for _ in range(2, n+1):
        await asyncio.sleep(.1)
        a, b = b, a + b
    cache.set(n, b)
    return b

def format_time_elapsed(seconds: float) -> str:
    return f"{seconds:.2f} seconds"

@app.get("/fibonacci/{x}", response_model=FibonacciResponse)
async def compute_fibonacci(x: int) -> FibonacciResponse:
    if x < 0:
        raise HTTPException(status_code=400, detail="x must be greater than or equal to 0")

    start_time = time.perf_counter()
    fib_x = await fibonacci_iterative(x)
    time_elapsed = format_time_elapsed(time.perf_counter() - start_time)

    return FibonacciResponse(x=x, fib_x=fib_x, time_elapsed=time_elapsed)
