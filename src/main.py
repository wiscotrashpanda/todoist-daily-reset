import os
import json
import datetime
import requests
import pytz

# Configuration
API_TOKEN = os.environ.get("TODOIST_API_TOKEN")
# Todoist REST API v2
BASE_URL = "https://api.todoist.com/rest/v2"


def get_cst_yesterday():
    """Returns yesterday's date string (YYYY-MM-DD) relative to CST/CDT."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    # Convert to CST (America/Chicago handles DST automatically)
    cst_tz = pytz.timezone("America/Chicago")
    cst_now = utc_now.astimezone(cst_tz)
    yesterday = cst_now - datetime.timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def is_daily_recurrence(task):
    """
    Checks if a task is a DAILY recurring task.
    Looks for 'daily', 'every day', 'ev day' in the due string.
    """
    if not task.get("due") or not task["due"].get("is_recurring"):
        return False

    due_string = task["due"].get("string", "").lower()
    daily_keywords = ["daily", "every day", "ev day"]

    # Basic string matching for daily patterns
    # This avoids matching "every week" or "every 3 days"
    return any(keyword in due_string for keyword in daily_keywords)


def lambda_handler(event, context):
    if not API_TOKEN:
        # Log warning but don't crash if running in a context where token isn't strictly needed for import
        # but runtime needs it.
        print("WARNING: TODOIST_API_TOKEN environment variable is not set")

    if not API_TOKEN:
        raise ValueError("TODOIST_API_TOKEN environment variable is not set")

    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    # 1. Fetch recurring and overdue tasks
    # We filter for 'overdue' to minimize the payload, though we still need to check the specific date logic manually
    print("Fetching overdue tasks...")
    params = {"filter": "overdue & recurring"}
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=headers, params=params)
        response.raise_for_status()
        tasks = response.json()
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        raise

    target_date = get_cst_yesterday()
    print(f"Target date for rollover (Yesterday CST): {target_date}")

    processed_count = 0

    for task in tasks:
        if not task.get("due") or not task["due"].get("date"):
            continue

        due_date = task["due"]["date"]

        # Logic:
        # 1. Must be due EXACTLY yesterday (relative to CST).
        #    If it's due 2 days ago, it's truly neglected, not just a "forgot to check off last night".
        # 2. Must be a "Daily" recurring task.
        if due_date == target_date and is_daily_recurrence(task):
            print(f"Rolling over task: {task['content']} (Due: {due_date})")

            # Close the task -> moves to next recurrence
            close_url = f"{BASE_URL}/tasks/{task['id']}/close"
            try:
                res = requests.post(close_url, headers=headers)
                res.raise_for_status()
                processed_count += 1
            except Exception as e:
                print(f"Failed to close task {task['id']}: {e}")
        else:
            print(
                f"Skipping task: {task['content']} (Due: {due_date}, Recurrence: {task['due'].get('string')})"
            )

    return {
        "statusCode": 200,
        "body": json.dumps(f"Processed {processed_count} daily recurring tasks."),
    }


if __name__ == "__main__":
    # Local testing entrypoint
    # Set env var before running locally
    # os.environ["TODOIST_API_TOKEN"] = "your_token_here"
    try:
        lambda_handler(None, None)
    except Exception as e:
        print(f"Local execution failed: {e}")
