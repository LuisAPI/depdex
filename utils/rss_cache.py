import time
from utils.rss import get_latest_rss_summaries as original_get_latest_rss_summaries

CACHE_DURATION = 300  # seconds (5 minutes)
_cache = {
    "timestamp": 0,
    "data": ""
}

def get_latest_rss_summaries_cached():
    now = time.time()
    if now - _cache["timestamp"] > CACHE_DURATION or not _cache["data"]:
        # Cache expired or empty — fetch fresh data
        _cache["data"] = original_get_latest_rss_summaries()
        _cache["timestamp"] = now
    return _cache["data"]

    rss_used = is_rss_used(req.message)
    if rss_used:
        print("📡 RSS content likely relevant to this request.")
    else:
        print("📭 RSS not relevant for this request.")

