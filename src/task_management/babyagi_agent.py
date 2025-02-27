import os
import logging
import subprocess
import uuid
from src.ai_core.model_integration import AIModel
from src.ai_core.real_time_learning import SelfLearningAI
from src.ai_core.web_browsing import WebBrowsing
from src.ai_core.self_improvement import SelfImprovement
from src.ai_core.image_processing import ImageProcessing
from src.ai_core.video_processing import VideoProcessing

class BabyAgiAgent:
    """
    A basic autonomous agent inspired by BabyAGI.
    """
    
    def __init__(self, model_type="llama3", model_path="models/llama-7b.ggmlv3.q4_0.bin"):
        self.ai_model = AIModel(model_type, model_path)
        self.memory = SelfLearningAI()
        self.task_queue = []
        logging.info("BabyAGI Agent Initialized.")

    def add_task(self, objective, priority=1):
        task_id = str(uuid.uuid4())
        task_prompt = f"Objective: {objective}. Generate a detailed task plan."
        generated_task = self.ai_model.generate_response(task_prompt)
        task = {
            "id": task_id,
            "objective": objective,
            "task": generated_task,
            "priority": priority,
            "status": "pending"
        }
        self.task_queue.append(task)
        logging.info(f"Task added: {task}")
        self.memory.store_interaction(task_prompt, generated_task)

    def execute_task(self):
        if not self.task_queue:
            logging.info("No tasks to execute.")
            return None
        
        self.task_queue.sort(key=lambda x: x["priority"], reverse=True)
        task = self.task_queue.pop(0)
        logging.info(f"Executing task: {task['task']}")
        task_result = self.ai_model.generate_response(task["task"])
        self.memory.store_interaction(task["task"], task_result)
        task["status"] = "completed"
        logging.info(f"Task completed with result: {task_result}")
        return task_result

    def refine_tasks(self):
        completed_tasks = [t for t in self.task_queue if t["status"] == "completed"]
        if not completed_tasks:
            logging.info("No completed tasks to refine.")
            return None
        refinement_prompt = "Analyze past task executions and suggest an optimized workflow."
        refined_plan = self.ai_model.generate_response(refinement_prompt)
        logging.info(f"Refinement plan generated: {refined_plan}")
        return refined_plan

    def run(self, iterations=3):
        logging.info(f"Starting BabyAGI agent for {iterations} iterations.")
        for i in range(iterations):
            if self.task_queue:
                result = self.execute_task()
                logging.info(f"Iteration {i+1} executed. Result: {result}")
            else:
                logging.info("No tasks available. Waiting for new tasks.")
            subprocess.run("sleep 2", shell=True)
        logging.info("BabyAGI agent run completed.")

# Example Usage
if __name__ == "__main__":
    agent = BabyAgiAgent(model_type="llama3", model_path="models/llama-7b.ggmlv3.q4_0.bin")
    agent.add_task("Research AI ethics and summarize key challenges", priority=2)
    agent.add_task("Write a Python script to automate file backups", priority=1)
    agent.run(iterations=5)
    refined_plan = agent.refine_tasks()
    if refined_plan:
        print("Optimized Workflow Plan:", refined_plan)
    else:
        print("No refinement available.")
