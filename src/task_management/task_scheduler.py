import time
import threading
import logging

class TaskScheduler:
    """
    A simple task scheduler that executes tasks at scheduled intervals.
    """
    
    def __init__(self):
        self.tasks = []
        self.running = False
        logging.info("Task Scheduler initialized.")

    def add_task(self, task_function, interval, task_name="Unnamed Task"):
        """
        Adds a task to the scheduler.
        :param task_function: The function to execute.
        :param interval: The time interval (in seconds) between executions.
        :param task_name: A friendly name for the task.
        """
        self.tasks.append({
            "function": task_function,
            "interval": interval,
            "name": task_name
        })
        logging.info(f"Added task: {task_name}, Interval: {interval}s")

    def start(self):
        """
        Starts the task scheduler.
        """
        self.running = True
        logging.info("Task Scheduler started.")
        threading.Thread(target=self._run_tasks, daemon=True).start()

    def stop(self):
        """
        Stops the task scheduler.
        """
        self.running = False
        logging.info("Task Scheduler stopped.")

    def _run_tasks(self):
        """
        Internal method to run tasks in a loop.
        """
        while self.running:
            for task in self.tasks:
                threading.Thread(target=self._execute_task, args=(task,)).start()
            time.sleep(1)  # Prevents excessive CPU usage

    def _execute_task(self, task):
        """
        Executes a task based on its interval.
        """
        while self.running:
            logging.info(f"Executing task: {task['name']}")
            task["function"]()
            time.sleep(task["interval"])

# Example Usage
if __name__ == "__main__":
    def sample_task():
        print("Sample task executed.")

    scheduler = TaskScheduler()
    scheduler.add_task(sample_task, interval=5, task_name="Print Task")
    scheduler.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
