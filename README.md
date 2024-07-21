# Monitoring the growth of crops

## Installing

### Prerequisites:

1. Python (≥ `3.11`) installed on your system.
2. Ensure [Docker](https://docs.docker.com/get-docker/) is installed.
3. Ensure you have `poetry` installed. If not, you can install them using `pip`.

### Steps:

1. **Clone the GitHub Repository:**

   Clone the GitHub repository you want to install locally using the `git clone` command.

   ```bash
   git clone https://github.com/machbry/crops-growth-monitoring
   ```

2. **Navigate to the Repository Directory:**

   Use the `cd` command to navigate into the repository directory.

   ```bash
   cd crops-growth-monitoring/
   ```

3. **Configure `poetry` to create a Virtual Environment inside the project:**

   Ensure that poetry will create a `.venv` directory into the project with the command:

   ```bash
   poetry config virtualenvs.in-project true
   ```

4. **Install Project Dependencies using `poetry`:**

   Use `poetry` to install the project dependencies.

   ```bash
   poetry install
   ```

   This will read the `pyproject.toml` file in the repository and install all the dependencies specified.

5. **Make sure everything is all right using `poetry env info`:**

   ```bash
   poetry env info
   ```

6. **Activate the Virtual Environment:**

   ```bash
   poetry shell
   ```

## Setup env variables
1. **Create a .env file from env.template**

   Change default values for DB credentials if you want to use another postgre DB.

   You don't need to change them if using DB from docker-compose for a dev environnement.

## Init database

1. **Build and run postgre db for dev (if you don't have your own)**

   ```bash
   docker-compose -f docker-compose-db.yaml up -d
   ```
   
2. **Update DB schema with alembic**

   ```bash
   alembic upgrade head
   ```

3. **Upload sample data from RPG database**
   
   ```bash
   python alembic/init_scripts/load_sample_rpg_data.py
   ```

3. **Upload sample data from RPG database**
   
   ```bash
   python alembic/init_scripts/load_sample_rpg_data.py
   ```
