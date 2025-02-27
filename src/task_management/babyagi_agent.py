import time
import threading
import logging
import datetime
import sched
from src.utils.config import Config

class TaskScheduler:
    """
    Task scheduler for executing recurring and scheduled tasks.
    """
    
    def __init__(self):
        """
        Initialize the task scheduler.
        """
        self.tasks = []
        self.running = False
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.lock = threading.Lock()
        logging.info("TaskScheduler initialized")

    def add_task(self, task_function, interval=None, schedule=None, task_name=None):
        """
        Add a task to the scheduler.
        
        Args:
            task_function (callable): Function to execute
            interval (float, optional): Time interval in seconds between executions
            schedule (str, optional): Cron-like schedule string (e.g., "09:30")
            task_name (str, optional): Name for the task
            
        Returns:
            str: Task ID
        """
        if not task_function:
            logging.error("Cannot add task: No function provided")
            return None
            
        if interval is None and schedule is None:
            logging.error("Cannot add task: No interval or schedule provided")
            return None
        
        # Generate task name if not provided
        if task_name is None:
            task_name = f"Task_{len(self.tasks) + 1}"
        
        # Create task object
        task = {
            "id": f"task_{int(time.time())}_{len(self.tasks)}",
            "name": task_name,
            "function": task_function,
            "interval": interval,
            "schedule": schedule,
            "last_run": None,
            "next_run": None,
            "runs": 0,
            "enabled": True
        }
        
        # Calculate next run time
        if interval:
            task["next_run"] = time.time() + interval
        elif schedule:
            task["next_run"] = self._calculate_next_run(schedule)
        
        # Add task to list
        with self.lock:
            self.tasks.append(task)
            # Schedule task
            if self.running:
                self._schedule_task(task)
        
        logging.info(f"Added task: {task_name}, ID: {task['id']}")
        return task["id"]

    def _calculate_next_run(self, schedule):
        """
        Calculate the next run time based on a schedule string.
        
        Args:
            schedule (str): Schedule string (HH:MM)
            
        Returns:
            float: Unix timestamp for next run
        """
        try:
            # Parse schedule
            hour, minute = map(int, schedule.split(":"))
            
            # Get current time
            now = datetime.datetime.now()
            scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If scheduled time is in the past, use tomorrow
            if scheduled_time <= now:
                scheduled_time += datetime.timedelta(days=1)
            
            # Convert to timestamp
            return scheduled_time.timestamp()
        except Exception as e:
            logging.error(f"Error parsing schedule '{schedule}': {e}")
            # Default to running in 1 hour
            return time.time() + 3600

    def start(self):
        """
        Start the task scheduler.
        
        Returns:
            bool: Success status
        """
        if self.running:
            logging.warning("TaskScheduler is already running")
            return False
        
        self.running = True
        
        # Schedule all tasks
        with self.lock:
            for task in self.tasks:
                if task["enabled"]:
                    self._schedule_task(task)
        
        # Start scheduler in a separate thread
        threading.Thread(target=self._run_scheduler, daemon=True).start()
        
        logging.info("TaskScheduler started")
        return True

    def stop(self):
        """
        Stop the task scheduler.
        
        Returns:
            bool: Success status
        """
        if not self.running:
            logging.warning("TaskScheduler is not running")
            return False
        
        self.running = False
        
        # Cancel all scheduled events
        with self.lock:
            for event in self.scheduler.queue:
                try:
                    self.scheduler.cancel(event)
                except:
                    pass
        
        logging.info("TaskScheduler stopped")
        return True

    def _run_scheduler(self):
        """
        Run the scheduler in a loop.
        """
        while self.running:
            try:
                # Run any due events
                self.scheduler.run(blocking=False)
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error in scheduler: {e}")
                time.sleep(1)

    def _schedule_task(self, task):
        """
        Schedule a task for execution.
        
        Args:
            task (dict): Task to schedule
        """
        if not task["enabled"]:
            return
            
        delay = max(0, task["next_run"] - time.time())
        
        # Schedule the task execution
        self.scheduler.enter(
            delay,
            1,
            self._execute_task,
            (task,)
        )

    def _execute_task(self, task):
        """
        Execute a scheduled task and reschedule.
        
        Args:
            task (dict): Task to execute
        """
        if not self.running or not task["enabled"]:
            return
            
        # Update task stats
        task["last_run"] = time.time()
        task["runs"] += 1
        
        # Execute task
        try:
            logging.info(f"Executing task: {task['name']}")
            task["function"]()
        except Exception as e:
            logging.error(f"Error executing task {task['name']}: {e}")
        
        # Reschedule if running
        if self.running and task["enabled"]:
            # Calculate next run time
            if task["interval"]:
                task["next_run"] = time.time() + task["interval"]
            elif task["schedule"]:
                task["next_run"] = self._calculate_next_run(task["schedule"])
            
            # Schedule next execution
            self._schedule_task(task)

    def get_tasks(self):
        """
        Get all tasks and their status.
        
        Returns:
            list: List of task information dictionaries
        """
        task_info = []
        
        with self.lock:
            for task in self.tasks:
                info = {
                    "id": task["id"],
                    "name": task["name"],
                    "enabled": task["enabled"],
                    "interval": task["interval"],
                    "schedule": task["schedule"],
                    "last_run": task["last_run"],
                    "next_run": task["next_run"],
                    "runs": task["runs"]
                }
                task_info.append(info)
                
        return task_info

    def enable_task(self, task_id):
        """
        Enable a task by ID.
        
        Args:
            task_id (str): ID of the task to enable
            
        Returns:
            bool: Success status
        """
        with self.lock:
            for task in self.tasks:
                if task["id"] == task_id:
                    task["enabled"] = True
                    
                    # Schedule if running
                    if self.running:
                        if task["interval"]:
                            task["next_run"] = time.time() + task["interval"]
                        elif task["schedule"]:
                            task["next_run"] = self._calculate_next_run(task["schedule"])
                        self._schedule_task(task)
                    
                    logging.info(f"Task {task_id} enabled")
                    return True
                    
        logging.warning(f"Task {task_id} not found")
        return False

    def disable_task(self, task_id):
        """
        Disable a task by ID.
        
        Args:
            task_id (str): ID of the task to disable
            
        Returns:
            bool: Success status
        """
        with self.lock:
            for task in self.tasks:
                if task["id"] == task_id:
                    task["enabled"] = False
                    logging.info(f"Task {task_id} disabled")
                    return True
                    
        logging.warning(f"Task {task_id} not found")
        return False