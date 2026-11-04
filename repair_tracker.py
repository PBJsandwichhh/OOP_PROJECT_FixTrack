import json
from pathlib import Path
from datetime import date, datetime
from repair_job import RepairJob

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "repair_jobs.json"

class RepairJobTracker:
    def __init__(self):
        self.jobs = []
        self.next_id = 1
        self.load()

    def generate_job_id(self):
        job_id = f"RJ-{self.next_id:04d}"
        self.next_id += 1
        return job_id

    def add_job(
        self,
        customer_name,
        item,
        problem,
        date_received="",
        notes="",
        problem_type="Other",
        parts_needed=False
    ):
        job = RepairJob(
            job_id=self.generate_job_id(),
            customer_name=customer_name,
            item=item,
            problem=problem,
            date_received=date_received,
            notes=notes,
            problem_type=problem_type,
            parts_needed=parts_needed
        )

        self.jobs.append(job)
        self.save()

        return job

    def get_job(self, job_id):
        for job in self.jobs:
            if job.job_id.lower() == job_id.lower():
                return job

        return None

    def search_jobs(self, keyword):
        keyword = keyword.lower().strip()

        if not keyword:
            return self.jobs

        return [
            job for job in self.jobs
            if keyword in job.job_id.lower()
            or keyword in job.customer_name.lower()
            or keyword in job.item.lower()
            or keyword in job.problem.lower()
            or keyword in job.status.lower()
            or keyword in job.notes.lower()
            or keyword in job.problem_type.lower()
        ]

    def update_job(
        self,
        job_id,
        customer_name,
        item,
        problem,
        status,
        cost,
        date_received,
        date_completed="",
        notes="",
        problem_type="Other",
        parts_needed=False
    ):
        job = self.get_job(job_id)

        if not job:
            return False

        job.customer_name = customer_name
        job.item = item
        job.problem = problem
        job.status = status
        job.cost = cost
        job.date_received = date_received
        job.date_completed = date_completed
        job.notes = notes
        job.problem_type = problem_type
        job.parts_needed = parts_needed

        if status == "Completed" and not job.date_completed:
            job.date_completed = date.today().isoformat()

        if status != "Completed":
            job.date_completed = ""

        self.save()

        return True

    def update_status(self, job_id, status):
        job = self.get_job(job_id)

        if not job:
            return False

        job.status = status

        if status == "Completed":
            if not job.date_completed:
                job.date_completed = date.today().isoformat()
        else:
            job.date_completed = ""

        self.save()

        return True

    def update_cost(self, job_id, cost):
        job = self.get_job(job_id)

        if not job:
            return False

        job.cost = cost
        self.save()

        return True

    def delete_job(self, job_id):
        job = self.get_job(job_id)

        if not job:
            return False

        self.jobs.remove(job)
        self.save()

        return True

    # DELAY RISK CALCULATION
    def calculate_delay_risk(self, job):
        score = 0
        reasons = []

        # Parts needed
        if job.parts_needed:
            score += 40
            reasons.append("Parts may be required")

        # Current workload
        active_jobs = sum(
            j.status != "Completed"
            for j in self.jobs
        )

        if active_jobs >= 8:
            score += 30
            reasons.append("Current repair workload is high")

        elif active_jobs >= 5:
            score += 15
            reasons.append("Current repair workload is moderate")

        # Still diagnosing
        if job.status == "Diagnosing":
            score += 20
            reasons.append("Repair is still being diagnosed")

        # Age of repair
        if job.date_received:
            try:
                received_date = datetime.strptime(
                    job.date_received,
                    "%Y-%m-%d"
                ).date()

                days_open = (
                    date.today() - received_date
                ).days

                if days_open > 3:
                    score += 10
                    reasons.append(
                        f"Repair has been open for {days_open} days"
                    )

            except ValueError:
                pass

        score = min(score, 100)

        # Risk level
        if score >= 60:
            level = "High"
            icon = "🔴"

        elif score >= 30:
            level = "Medium"
            icon = "🟡"

        else:
            level = "Low"
            icon = "🟢"

        return {
            "score": score,
            "level": level,
            "icon": icon,
            "reasons": reasons
        }

    # SAVE / LOAD
    def save(self):
        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        DATA_FILE.write_text(
            json.dumps(
                [job.to_dict() for job in self.jobs],
                indent=4
            ),
            encoding="utf-8"
        )

    def load(self):
        if not DATA_FILE.exists():
            return

        try:

            data = json.loads(
                DATA_FILE.read_text(
                    encoding="utf-8"
                )
            )

            self.jobs = []

            for item in data:

                # Support older records
                item.setdefault(
                    "date_received",
                    ""
                )

                item.setdefault(
                    "date_completed",
                    ""
                )

                item.setdefault(
                    "notes",
                    ""
                )

                item.setdefault(
                    "problem_type",
                    "Other"
                )

                item.setdefault(
                    "parts_needed",
                    False
                )

                self.jobs.append(
                    RepairJob(**item)
                )

            # Continue Job IDs correctly
            numbers = []

            for job in self.jobs:

                try:
                    numbers.append(
                        int(
                            job.job_id.split("-")[1]
                        )
                    )

                except (
                    IndexError,
                    ValueError
                ):
                    pass

            if numbers:
                self.next_id = max(numbers) + 1

        except (
            json.JSONDecodeError,
            TypeError,
            KeyError
        ):
            self.jobs = []