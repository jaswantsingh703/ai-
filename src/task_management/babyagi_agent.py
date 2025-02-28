import logging
import time
import uuid
import os
import threading
from src.ai_core.model_integration import AIModel
from src.ai_core.real_time_learning import SelfLearningAI
from src.utils.config import Config

class BabyAgiAgent:
    """
    An autonomous AI agent inspired by BabyAGI.
    Manages task generation, execution, and refinement with memory.
    """
    
    def __init__(self, model_type=None, model_path=None):
        """
        Initialize the BabyAGI agent.
        
        Args:
            model_type (str): AI model type to use (llama3, gpt4all, etc.)
            model_path (str): Path to the model file
        """
        # Use config values if parameters not provided
        model_type = model_type or Config.get("default_model_type")
        model_path = model_path or Config.get("default_model_path")
        
        # Initialize components
        self.ai_model = AIModel(model_type, model_path)
        self.memory = SelfLearningAI()
        self.task_queue = []
        self.history = []
        self.is_running = False
        self.lock = threading.Lock()
        
        logging.info("BabyAGI agent initialized")
    
    def add_task(self, objective, task_type="general", priority=1):
        """
        Add a task to the queue.
        
        Args:
            objective (str): Task objective/description
            task_type (str): Type of task
            priority (int): Priority level (higher = more important)
            
        Returns:
            str: Task ID
        """
        task_id = str(uuid.uuid4())
        
        with self.lock:
            task = {
                "id": task_id,
                "objective": objective,
                "type": task_type,
                "priority": priority,
                "status": "pending",
                "created_at": time.time(),
                "completed_at": None,
                "result": None
            }
            
            self.task_queue.append(task)
            logging.info(f"Task added: {objective} (ID: {task_id})")
        
        return task_id
    
    def get_task(self, task_id):
        """
        Get a task by ID.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            dict: Task data or None if not found
        """
        with self.lock:
            for task in self.task_queue:
                if task["id"] == task_id:
                    return task.copy()
        return None
    
    def get_tasks(self, status=None):
        """
        Get all tasks, optionally filtered by status.
        
        Args:
            status (str, optional): Filter by status
            
        Returns:
            list: List of tasks
        """
        with self.lock:
            if status:
                return [task.copy() for task in self.task_queue if task["status"] == status]
            else:
                return [task.copy() for task in self.task_queue]
    
    def execute_task(self, task_id=None):
        """
        Execute a specific task or the highest priority pending task.
        
        Args:
            task_id (str, optional): Task ID to execute
            
        Returns:
            dict: Execution result with task info
        """
        with self.lock:
            # Find the task to execute
            task = None
            if task_id:
                # Find by ID
                for t in self.task_queue:
                    if t["id"] == task_id and t["status"] == "pending":
                        task = t
                        break
                
                if not task:
                    logging.warning(f"Task {task_id} not found or not pending")
                    return {"success": False, "error": "Task not found or not pending"}
            else:
                # Find highest priority pending task
                pending_tasks = [t for t in self.task_queue if t["status"] == "pending"]
                if not pending_tasks:
                    logging.info("No pending tasks to execute")
                    return {"success": False, "error": "No pending tasks"}
                
                # Sort by priority (highest first)
                pending_tasks.sort(key=lambda x: x["priority"], reverse=True)
                task = pending_tasks[0]
            
            # Mark as in progress
            task["status"] = "in_progress"
        
        # Execute task outside the lock
        logging.info(f"Executing task: {task['objective']} (ID: {task['id']})")
        
        try:
            # Get context from memory
            context = self.memory.retrieve_context(task["objective"])
            
            # Prepare prompt
            prompt = f"Task: {task['objective']}\n\n"
            if context:
                prompt += f"Context:\n{context}\n\n"
            prompt += "Execute this task and provide a detailed response."
            
            # Generate response
            response = self.ai_model.generate_response(prompt)
            
            # Store in memory
            self.memory.store_interaction(prompt, response)
            
            # Update task with result
            with self.lock:
                task["status"] = "completed"
                task["completed_at"] = time.time()
                task["result"] = response
                
                # Add to history
                self.history.append({
                    "task_id": task["id"],
                    "objective": task["objective"],
                    "result": response,
                    "completed_at": task["completed_at"]
                })
            
            logging.info(f"Task completed: {task['objective']} (ID: {task['id']})")
            return {
                "success": True,
                "task_id": task["id"],
                "result": response
            }
        except Exception as e:
            logging.error(f"Error executing task {task['id']}: {str(e)}")
            
            # Update task status
            with self.lock:
                task["status"] = "failed"
                task["result"] = f"Error: {str(e)}"
            
            return {
                "success": False,
                "task_id": task["id"],
                "error": str(e)
            }
    
    def refine_tasks(self):
        """
        Analyze task history and generate new optimized tasks.
        
        Returns:
            list: Newly created task IDs
        """
        if not self.history:
            logging.info("No task history to refine")
            return []
        
        logging.info("Refining tasks based on execution history")
        
        # Prepare prompt with task history
        history_text = "\n\n".join([
            f"Task: {h['objective']}\nResult: {h['result']}"
            for h in self.history[-5:]  # Last 5 tasks
        ])
        
        prompt = f"""Based on these previously completed tasks:

{history_text}

Generate three new tasks that would be valuable to execute next. Consider dependencies, logical next steps, and potential optimizations.
Format each task as a separate paragraph with a clear objective.
"""
        
        # Generate tasks
        response = self.ai_model.generate_response(prompt)
        
        # Parse response into tasks
        new_task_ids = []
        
        # Simple parsing - split by paragraphs
        paragraphs = response.split("\n\n")
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # Add as a new task with medium priority
                task_id = self.add_task(paragraph.strip(), priority=2)
                new_task_ids.append(task_id)
        
        logging.info(f"Created {len(new_task_ids)} refined tasks")
        return new_task_ids
    
    def run(self, iterations=5, interval=2):
        """
        Run the agent for a specified number of iterations.
        
        Args:
            iterations (int): Number of iterations to run
            interval (float): Seconds between iterations
            
        Returns:
            list: Results from all iterations
        """
        if self.is_running:
            logging.warning("BabyAGI is already running")
            return []
        
        self.is_running = True
        logging.info(f"Starting BabyAGI agent for {iterations} iterations")
        
        results = []
        
        try:
            for i in range(iterations):
                logging.info(f"Iteration {i+1}/{iterations}")
                
                # Execute highest priority task
                result = self.execute_task()
                results.append(result)
                
                # After every other iteration, refine tasks
                if i > 0 and i % 2 == 0:
                    self.refine_tasks()
                
                # Wait between iterations
                if i < iterations - 1:
                    time.sleep(interval)
        finally:
            self.is_running = False
            logging.info("BabyAGI agent run completed")
        
        return results
    
    def run_async(self, iterations=5, interval=2, callback=None):
        """
        Run the agent asynchronously in a separate thread.
        
        Args:
            iterations (int): Number of iterations to run
            interval (float): Seconds between iterations
            callback (callable): Function to call with results when done
            
        Returns:
            bool: Whether the async run was started successfully
        """
        if self.is_running:
            logging.warning("BabyAGI is already running")
            return False
        
        def _run_thread():
            results = self.run(iterations, interval)
            if callback:
                callback(results)
        
        thread = threading.Thread(target=_run_thread)
        thread.daemon = True
        thread.start()
        
        return True
    
    def stop(self):
        """
        Stop the running agent.
        
        Returns:
            bool: Whether the agent was stopped
        """
        if not self.is_running:
            return False
        
        self.is_running = False
        logging.info("BabyAGI agent stopped")
        return True