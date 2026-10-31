"""Shared-cache lock preventing overlapping manual and scheduled generations."""

from django.core.cache import cache

GENERATION_LOCK_KEY = 'analysis:daily_bets:generation_lock'
GENERATION_LOCK_TIMEOUT_SECONDS = 30 * 60


def acquire_generation_lock(owner_id):
    current_owner = cache.get(GENERATION_LOCK_KEY)
    if current_owner == owner_id:
        return True
    return cache.add(
        GENERATION_LOCK_KEY,
        owner_id,
        timeout=GENERATION_LOCK_TIMEOUT_SECONDS,
    )


def get_generation_lock_owner():
    return cache.get(GENERATION_LOCK_KEY)


def renew_generation_lock(owner_id):
    try:
        if cache.get(GENERATION_LOCK_KEY) != owner_id:
            return False
        cache.set(
            GENERATION_LOCK_KEY,
            owner_id,
            timeout=GENERATION_LOCK_TIMEOUT_SECONDS,
        )
        return True
    except Exception:
        return False


def release_generation_lock(owner_id):
    try:
        if cache.get(GENERATION_LOCK_KEY) == owner_id:
            cache.delete(GENERATION_LOCK_KEY)
    except Exception:
        return False
    return True