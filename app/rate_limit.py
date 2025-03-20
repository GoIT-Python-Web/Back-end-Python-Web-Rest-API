from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import time


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    def is_rate_limited(self, user_id: str) -> Tuple[bool, float]:
        current_time = time.time()
        user_requests = self.requests[user_id]

        user_requests = [
            req_time for req_time in user_requests if current_time - req_time < 60
        ]

        if len(user_requests) >= self.requests_per_minute:
            time_until_next = 60 - (current_time - user_requests[0])
            return True, time_until_next

        user_requests.append(current_time)
        self.requests[user_id] = user_requests
        return False, 0


contact_creation_limiter = RateLimiter(requests_per_minute=5)
contact_search_limiter = RateLimiter(requests_per_minute=30)
contact_general_limiter = RateLimiter(requests_per_minute=60)


async def check_rate_limit(limiter: RateLimiter, user_id: str):
    is_limited, time_until_next = limiter.is_rate_limited(user_id)
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Please try again in {time_until_next:.1f} seconds.",
        )
