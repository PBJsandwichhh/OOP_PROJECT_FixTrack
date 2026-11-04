from dataclasses import dataclass, asdict

@dataclass
class RepairJob:
    job_id: str
    customer_name: str
    item: str
    problem: str
    status: str = "Received"
    cost: float = 0.0
    date_received: str = ""
    date_completed: str = ""
    notes: str = ""
    problem_type: str = "Other"
    parts_needed: bool = False

    def to_dict(self):
        return asdict(self)