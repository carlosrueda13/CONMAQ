from locust import HttpUser, task, between
import random

class ConmaqUser(HttpUser):
    wait_time = between(1, 5)
    
    # Store machine IDs to query availability later
    machine_ids = []

    def on_start(self):
        """
        Executed when a user starts.
        We could log in here if needed, but for public endpoints it's fine.
        """
        pass

    @task(3)
    def list_machines(self):
        """
        List machines. High weight (3) as it's a common operation.
        """
        with self.client.get("/api/v1/machines/", catch_response=True) as response:
            if response.status_code == 200:
                machines = response.json()
                if machines:
                    self.machine_ids = [m["id"] for m in machines]
            else:
                response.failure(f"Failed to list machines: {response.status_code}")

    @task(1)
    def check_availability(self):
        """
        Check availability for a random machine.
        """
        if not self.machine_ids:
            return
        
        machine_id = random.choice(self.machine_ids)
        self.client.get(f"/api/v1/machines/{machine_id}/availability")

    @task(1)
    def view_machine_details(self):
        """
        View details of a specific machine.
        """
        if not self.machine_ids:
            return
            
        machine_id = random.choice(self.machine_ids)
        self.client.get(f"/api/v1/machines/{machine_id}")
