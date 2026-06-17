from datetime import datetime
from analytics.mongo import activity_logs


def log_activity(user, action, metadata=None):

    activity_logs.insert_one({
        "user_id": user.id,
        "username": user.username,
        "action": action,
        "metadata": metadata or {},
        "created_at": datetime.utcnow()
    })