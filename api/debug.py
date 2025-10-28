# File: api/debug.py

from fastapi import APIRouter
import redis

# NOTE: This connects to Redis directly, just like main.py
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
router = APIRouter()

@router.delete("/memory/reset/{user_id}")
async def reset_user_memory(user_id: str):
    """Deletes the entire short-term conversation history for a single user."""
    redis_key = f"history:{user_id}"
    deleted_count = redis_client.delete(redis_key)
    
    # We DON'T delete ChromaDB history here, as long-term memory is supposed to persist
    
    if deleted_count > 0:
        return {"status": "success", "message": f"Short-term memory reset for user: {user_id}"}
    return {"status": "not_found", "message": f"No memory found for user: {user_id}"}