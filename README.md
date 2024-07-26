# Monitoring the growth of crops

## Installing

### Prerequisites:

1. Python (≥ `3.11`) installed on your system.
2. Ensure [Docker](https://docs.docker.com/get-docker/) is installed.
3. Ensure you have `poetry` installed (you can also use `pip`)

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

   Change default values for DB credentials if you want to use an existing postgre DB.

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
   You may need to wait few seconds before running this command to enable container to run.

3. **Upload sample data with parcels from RPG database**
   
   ```bash
   python alembic/init_scripts/load_sample_rpg_data.py
   ```

## Run pipelines
1. **To query sentinel-2 data with chosen dates range**

   ```bash
   python src/run_pipeline_request_sentinel_2_data.py --from "2024-06-01" --to "2024-06-30"
   ```
   
2. **To run pending computations index (NDVI & NDMI) for parcels**

   ```bash
   python src/run_pipeline_compute_pending_parcels_index.py --max 5 --resolution 0.0001
   ```
   - max : max number of parcels index computations, if none provided, all will be computed.
   - resolution : spacial resolution for index computations (default = 0.0001)

## Storage

### Database schema

**4 tables available :**
- parcels : store parcels with their geometry.
- catalog_queries : log catalog API queries to sentinel-2-12a collection with path to json file with results.
- parcels_queries : link between parcels and catalog queries. Used to know if and when index computations have been done.
- parcels_index : store values of index (NDVI & NDMI) for each time and parcel (mean values and path to COG files).

### Files

- Catalogs queries results to sentinel-2-12a collection are stored as JSON files.
- COG files are also stored for each parcel.
 
All these files are referenced in database.
