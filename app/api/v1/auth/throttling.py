# Rate limiting system to protect the API from too many requests

import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import HTTPException, status

# --- Rate Limit Configuration ---
# These can be easily modified to adjust rate limiting behavior

# For authenticated users
AUTH_RATE_LIMIT = 5  # requests per time window
AUTH_TIME_WINDOW_SECONDS = 60  # time window in seconds

# For unauthenticated "global" users
GLOBAL_RATE_LIMIT = 3  # requests per time window
GLOBAL_TIME_WINDOW_SECONDS = 60  # time window in seconds

# --- In-memory storage for user requests ---
user_requests = defaultdict(list)

# --- Rate limiting functions ---
def apply_rate_limit(user_id: str) -> bool:
    """
    Apply rate limiting to a user request.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        bool: True if request is allowed
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    current_time = time.time()

    # Determine rate limit settings based on user type
    if user_id == "global_unauthenticated_user":
        rate_limit = GLOBAL_RATE_LIMIT
        time_window = GLOBAL_TIME_WINDOW_SECONDS
    else:
        rate_limit = AUTH_RATE_LIMIT
        time_window = AUTH_TIME_WINDOW_SECONDS

    # Clean up old requests outside the time window
    user_requests[user_id] = [
        t for t in user_requests[user_id] if t > current_time - time_window
    ]

    # Check if rate limit is exceeded
    if len(user_requests[user_id]) >= rate_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Too many requests. Please try again later.",
                "rate_limit": rate_limit,
                "time_window_seconds": time_window,
                "retry_after": int(time_window - (current_time - user_requests[user_id][0]))
            }
        )
    
    # Add current request timestamp
    user_requests[user_id].append(current_time)
    
    return True

def get_user_rate_limit_status(user_id: str) -> Dict:
    """
    Get the current rate limit status for a specific user.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Dict: Rate limit status information
    """
    current_time = time.time()
    
    # Determine rate limit settings
    if user_id == "global_unauthenticated_user":
        rate_limit = GLOBAL_RATE_LIMIT
        time_window = GLOBAL_TIME_WINDOW_SECONDS
    else:
        rate_limit = AUTH_RATE_LIMIT
        time_window = AUTH_TIME_WINDOW_SECONDS
    
    # Clean up old requests
    user_requests[user_id] = [
        t for t in user_requests[user_id] if t > current_time - time_window
    ]
    
    current_usage = len(user_requests[user_id])
    remaining_requests = max(0, rate_limit - current_usage)
    
    # Calculate time until reset
    time_until_reset = 0
    if user_requests[user_id]:
        oldest_request = user_requests[user_id][0]
        time_until_reset = max(0, time_window - (current_time - oldest_request))
    
    return {
        "user_id": user_id,
        "rate_limit": rate_limit,
        "time_window_seconds": time_window,
        "current_usage": current_usage,
        "remaining_requests": remaining_requests,
        "time_until_reset_seconds": int(time_until_reset),
        "is_limited": current_usage >= rate_limit
    }

def get_all_rate_limit_status() -> Dict:
    """
    Get rate limit status for all users.
    
    Returns:
        Dict: Rate limit status for all users
    """
    current_time = time.time()
    all_status = {}
    
    for user_id in user_requests.keys():
        # Clean up old requests for this user
        user_requests[user_id] = [
            t for t in user_requests[user_id] if t > current_time - AUTH_TIME_WINDOW_SECONDS
        ]
        
        if user_requests[user_id]:  # Only include users with recent activity
            all_status[user_id] = get_user_rate_limit_status(user_id)
    
    return {
        "total_active_users": len(all_status),
        "rate_limit_config": {
            "authenticated_users": {
                "limit": AUTH_RATE_LIMIT,
                "time_window_seconds": AUTH_TIME_WINDOW_SECONDS
            },
            "unauthenticated_users": {
                "limit": GLOBAL_RATE_LIMIT,
                "time_window_seconds": GLOBAL_TIME_WINDOW_SECONDS
            }
        },
        "users": all_status
    }

def reset_user_rate_limit(user_id: str) -> Dict:
    """
    Reset rate limit for a specific user.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Dict: Confirmation message
    """
    if user_id in user_requests:
        del user_requests[user_id]
        return {
            "message": f"Rate limit reset for user {user_id}",
            "user_id": user_id,
            "status": "reset"
        }
    else:
        return {
            "message": f"No rate limit data found for user {user_id}",
            "user_id": user_id,
            "status": "not_found"
        }

def reset_all_rate_limits() -> Dict:
    """
    Reset rate limits for all users.
    
    Returns:
        Dict: Confirmation message
    """
    user_count = len(user_requests)
    user_requests.clear()
    
    return {
        "message": f"Rate limits reset for all users",
        "users_reset": user_count,
        "status": "reset"
    }

def update_rate_limit_config(
    auth_limit: int = None,
    auth_window: int = None,
    global_limit: int = None,
    global_window: int = None
) -> Dict:
    """
    Update rate limit configuration.
    
    Args:
        auth_limit: New limit for authenticated users
        auth_window: New time window for authenticated users
        global_limit: New limit for unauthenticated users
        global_window: New time window for unauthenticated users
        
    Returns:
        Dict: Updated configuration
    """
    global AUTH_RATE_LIMIT, AUTH_TIME_WINDOW_SECONDS, GLOBAL_RATE_LIMIT, GLOBAL_TIME_WINDOW_SECONDS
    
    if auth_limit is not None:
        AUTH_RATE_LIMIT = auth_limit
    if auth_window is not None:
        AUTH_TIME_WINDOW_SECONDS = auth_window
    if global_limit is not None:
        GLOBAL_RATE_LIMIT = global_limit
    if global_window is not None:
        GLOBAL_TIME_WINDOW_SECONDS = global_window
    
    return {
        "message": "Rate limit configuration updated",
        "new_config": {
            "authenticated_users": {
                "limit": AUTH_RATE_LIMIT,
                "time_window_seconds": AUTH_TIME_WINDOW_SECONDS
            },
            "unauthenticated_users": {
                "limit": GLOBAL_RATE_LIMIT,
                "time_window_seconds": GLOBAL_TIME_WINDOW_SECONDS
            }
        }
    }