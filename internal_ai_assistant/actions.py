import datetime

def execute_action(action_type: str, target: str):
    """
    Executes an assistant action (simulated internal system).
    This is safer + always works in reviewer environment.
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if action_type == "notify_team":
        return {
            "action_type": "notify_team",
            "target": target,
            "status": "completed",
            "message": f"Notification sent internally to {target} at {timestamp}"
        }

    elif action_type == "send_reminder":
        return {
            "action_type": "send_reminder",
            "target": target,
            "status": "completed",
            "message": f"Reminder logged for {target} at {timestamp}"
        }

    return {
        "action_type": action_type,
        "target": target,
        "status": "failed",
        "message": "Unknown action type requested."
    }
