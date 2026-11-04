FixTrack: Repair Job Tracker with Delay Risk Monitor

Project Description
FixTrack is a Python-based Repair Job Tracking System designed for small repair shops and technicians. It helps users organize customer repair records, monitor repair progress, manage repair costs, and identify jobs that may experience delays. The system provides a simple interface for recording repair jobs, searching existing records, updating job information, and monitoring repair statuses. It also includes a Delay Risk Monitor that evaluates repair jobs using predefined conditions to help technicians identify possible delays before they happen.

Features
- Dashboard – Displays total, active, ready-for-pickup, and completed repair jobs.
- Add Repair Job – Records customer details, item information, reported problems, and repair dates.
- Automatic Job ID – Generates a unique ID for every repair job.
- View Repair Jobs – Displays all recorded repair jobs.
- Search Jobs – Finds repair records using keywords.
- Update Job – Allows users to edit repair details, status, cost, and notes.
- Delete Job – Removes repair records.
- Repair Status Tracking – Monitors the progress of repairs, from receiving the item to completion.
- Delay Risk Monitor – Evaluates repair jobs and assigns a Low, Medium, or High delay risk level.
- JSON Data Storage – Saves repair records so they can be loaded again when the application is reopened.

Delay Risk Monitor
The Delay Risk Monitor uses a simple rule-based scoring system to identify repair jobs that may be delayed.

Risk Factors
| Condition | Risk Score |
| --- | --- |
| Parts are needed | +40 |
| High active workload (8 or more jobs) | +30 |
| Moderate active workload (5–7 jobs) | +15 |
| Job is still diagnosing | +20 |
| Job is older than 3 days | +10 |

Risk Levels
| Total Score | Risk Level |
| --- | --- |
| 0–29 | Low |
| 30–59 | Medium |
| 60 or higher | High |

The system uses these scores to help technicians prioritize jobs and pay attention to repairs that may take longer than expected.

Object-Oriented Programming Implementation
FixTrack uses Python classes to organize its program and manage repair job records.

1. RepairJob
Represents an individual repair job.

Attributes:
- job_id
- customer_name
- item
- problem
- status
- cost
- date_received
- date_completed
- notes

Methods:
- `to_dict()` – Converts the repair job object into a dictionary.
- `mark_completed()` – Marks a repair job as completed and records its completion date.

2. RepairJobTracker
Manages the collection of repair jobs and their operations.

Methods:
- `generate_job_id()` – Generates a unique repair job ID.
- `add_job()` – Creates and adds a new repair job.
- `get_job()` – Retrieves a repair job using its ID.
- `search_jobs()` – Searches repair records using keywords.
- `update_job()` – Updates repair job information.
- `update_status()` – Changes the repair status.
- `update_cost()` – Updates the repair cost.
- `delete_job()` – Removes a repair job.
- `calculate_delay_risk()` – Evaluates the possible delay risk of a repair job.
- `save()` – Saves repair records to a JSON file.
- `load()` – Loads previously saved repair records.

OOP Principles
- Encapsulation: Groups related repair job data and operations inside classes.
- Abstraction: Allows the application interface to use simple methods without handling their internal implementation.

Inheritance and polymorphism are not required in the current design.

Technologies Used
- Python
- Streamlit
- Pandas
- Streamlit Option Menu
- JSON

Project Structure
```text
FixTrack/
├── app.py
├── repair_job.py
├── repair_tracker.py
├── requirements.txt
├── README.md
└── data/
    └── repair_jobs.json
```

Installation and Setup
1. Download the repository

2. Install the Required Packages
FixTrack requires the following Python packages: Streamlit, Pandas, & Streamlit Option Menu

To install them manually:

I. Open Command Prompt or Terminal.

II. Enter the following commands one at a time:

- python -m pip install streamlit
- python -m pip install pandas
- python -m pip install streamlit-option-menu
  
Wait for each package to finish installing before entering the next command.
   
3. Run the application
   
I. Navigate to the extracted FixTrack project folder.

II. Open Command Prompt or Terminal in the folder.

III. Enter the following command:

- python -m streamlit run app.py

The application will open in your web browser.

Data Storage
FixTrack uses JSON to store repair job records.

The data file is located at:

```text
data/repair_jobs.json
```

This allows repair records to remain available when the application is reopened.

Project Purpose
FixTrack aims to help small repair businesses manage repair records more efficiently, monitor repair progress, reduce forgotten jobs, and identify repairs that may be delayed.

Future Improvements
Possible future enhancements include:
- Customer notification system
- User login and account management
- More advanced repair analytics
- Improved delay prediction based on historical repair records
