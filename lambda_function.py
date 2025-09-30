import json
import os
import logging
from datetime import datetime, date, timezone
from typing import List, Dict, Any, Optional, Union

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task
from dateutil import parser
import pytz

# AWS Lambda context type
class LambdaContext:
    """AWS Lambda context object type hint"""
    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    remaining_time_in_millis: int
    log_group_name: str
    log_stream_name: str
    aws_request_id: str

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Optional[LambdaContext]) -> Dict[str, Any]:
    """
    AWS Lambda handler function to complete recurring Todoist tasks due today.
    
    Args:
        event: AWS Lambda event object
        context: AWS Lambda context object
        
    Returns:
        Dict containing status and processed tasks information
    """
    try:
        # Get Todoist API token from environment variable
        todoist_token = os.environ.get('TODOIST_API_TOKEN')
        if not todoist_token:
            raise ValueError("TODOIST_API_TOKEN environment variable is required")

        # Get timezone from environment variable, default to UTC
        timezone_str = os.environ.get('TIMEZONE', 'UTC')
        user_timezone = pytz.timezone(timezone_str)
        
        # Initialize Todoist API
        api = TodoistAPI(todoist_token)
        
        # Get today's date in user's timezone
        today = datetime.now(user_timezone).date()
        logger.info(f"Processing tasks for date: {today} (timezone: {timezone_str})")

        # Get all active tasks
        try:
            tasks = api.get_tasks()
            # Ensure we have a list of tasks
            if not isinstance(tasks, list):
                tasks = list(tasks)
        except Exception as e:
            logger.error(f"Failed to retrieve tasks: {str(e)}")
            raise
        
        logger.info(f"Retrieved {len(tasks)} total tasks")
        
        # Filter for recurring tasks due today
        tasks_to_complete = []
        for i, task in enumerate(tasks):
            # Debug: log task type for first few tasks
            if i < 3:
                logger.debug(f"Task {i} type: {type(task)}, has due: {hasattr(task, 'due')}")
            
            # Skip if this is somehow a list (shouldn't happen with correct API)
            if isinstance(task, list):
                logger.warning(f"Unexpected list found at index {i}, skipping")
                continue
                
            if is_recurring_task_due_today(task, today, user_timezone):
                tasks_to_complete.append(task)
       
        logger.info(f"Found {len(tasks_to_complete)} recurring tasks due today")
        
        # Complete the tasks
        completed_tasks = []
        for task in tasks_to_complete:
            try:
                # Use the correct method to complete a task
                success = api.complete_task(task_id=task.id)
                if success:
                    completed_tasks.append({
                        'id': task.id,
                        'content': task.content,
                        'due_date': task.due.date if task.due else None
                    })
                    logger.info(f"Completed task: {task.content} (ID: {task.id})")
                else:
                    logger.warning(f"Failed to complete task: {task.content} (ID: {task.id})")
            except Exception as e:
                logger.error(f"Failed to complete task {task.id}: {str(e)}")
        
        # Return success response
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {len(completed_tasks)} recurring tasks',
                'completed_tasks': completed_tasks,
                'total_tasks_checked': len(tasks),
                'date_processed': today.isoformat(),
                'timezone': timezone_str
            }, default=str)
        }
        
        logger.info(f"Lambda execution completed successfully. Processed {len(completed_tasks)} tasks.")
        return response
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process Todoist tasks'
            })
        }


def is_recurring_task_due_today(task: Union[Task, Any], today: date, user_timezone: pytz.BaseTzInfo) -> bool:
    """
    Check if a task is recurring and due today.
    
    Args:
        task: Todoist task object
        today: Today's date in user's timezone
        user_timezone: User's timezone object
        
    Returns:
        bool: True if task is recurring and due today
    """
    # Check if task has a due date
    if not task.due:
        return False
    
    # Check if task is recurring (has recurring due date string)
    if not task.due.is_recurring:
        return False
    
    # Parse the due date
    try:
        if task.due.date:
            # Date-only due date
            due_date = parser.parse(str(task.due.date)).date()
        else:
            # Try to get datetime from the due object
            due_datetime_str = getattr(task.due, 'datetime', None)
            if due_datetime_str:
                # DateTime due date - convert to user's timezone
                due_datetime = parser.parse(str(due_datetime_str))
                if due_datetime.tzinfo is None:
                    # Assume it's in user's timezone if no timezone info
                    due_datetime = user_timezone.localize(due_datetime)
                else:
                    # Convert to user's timezone
                    due_datetime = due_datetime.astimezone(user_timezone)
                due_date = due_datetime.date()
            else:
                return False
        
        # Check if due date is today
        return due_date == today
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse due date for task {task.id}: {str(e)}")
        return False


def get_task_summary(task: Union[Task, Any]) -> Dict[str, Any]:
    """
    Get a summary of task information for logging.
    
    Args:
        task: Todoist task object
        
    Returns:
        Dict containing task summary
    """
    return {
        'id': task.id,
        'content': task.content,
        'due_date': task.due.date if task.due and task.due.date else None,
        'due_datetime': getattr(task.due, 'datetime', None) if task.due else None,
        'is_recurring': task.due.is_recurring if task.due else False,
        'project_id': task.project_id,
        'labels': task.labels
    }


if __name__ == "__main__":
    # For local testing
    test_event = {}
    test_context = None
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2, default=str))