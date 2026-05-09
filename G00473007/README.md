# Conference Management System

A Python-based application for managing conference attendees, rooms, and speakers, utilizing both relational (**MySQL**) and graph (**Neo4j**) databases.

## Requirement

Before running the application, ensure you have the following installed:
* Python 3.x
* MySQL Server
* Neo4j Desktop / Neo4j Database
* Required Python libraries: `mysql-connector-python`, `neo4j`

## Installation

1.  Clone the repository or extract the ZIP file.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

### 1. MySQL
* Create a database named `appdbproj`.
* Import the provided `appdbproj.sql` file to create the necessary tables (`attendee`, `room`, `session`, `company`).

### 2. Neo4j
* Ensure your Neo4j instance is running on `bolt://127.0.0.1:7687`.
* Default credentials are set to `neo4j` / `password123` (update in `main.py` if necessary).

## How to Run

Execute the main script from your terminal:
```bash
python main.py
