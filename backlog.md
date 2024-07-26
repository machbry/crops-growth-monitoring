## TODO
- don't requests all parcels for pipeline request_sentinel_2_data
- create groups of parcels (related to sentinel-2 grids or contiguous zones)
- add database schema instead of using public by default
- add unit tests for code coverage (> 70%)
- add error handling during pipelines execution (ex : no data from sentinel-2, ...)
- use async sql engine
- use Dask to speed up queries to STAC catalog
- use TimescaleDB for parcels_index
- use managed DB in production instead of a containerized one
- using SQL database for millions of parcels could be problem but can ease usages
- dump index data in another database + do purge regulary on database and files
- use S3 instead of file system to store cog files
- what to do for parcels with no usable data on some days after clouds filtering ?
- ...

## Architecture
- Datalake : to store COG files (ex : S3)
- Datawarehouse : to store time series (ex : TimescaleDB), geometries (ex : Postgis) or other needed data sources
- Orchestration : Airflow / Dagster, several pipelines :
    - request and clean new data on selected sentinel-2 grid - every week
    - filter data and compute index (on a maximum parcels at a time) - on new data for watched parcels
    - prepare tables / files to be ready for usage (analysis, visualisation on an application, ...) - every week
- Execution : use Databricks / Spark to execute pipelines (// on groups on parcels)
- Monitoring : Elastic (or equivalent) to gather logs / events during pipelines executions :
    - alert if a pipeline run fails, measure performances, measure data quality (and alerts if too low), debugging, ...
- others aspects to address : purge, versionning, code quality (ex : Ruff), CI/CD (ex : Jenkins / Cloudbees), 
multi-environments, security, documentation, ...

## Governance & traceability
- Set objectives for the data and identify usages
- Have data owners and processes
  - _Team A is reponsible for NDVI / NDMI data_
  - _Code review before any code / infra modification (pipeline, schema, infrastructure, ...)_
  - _Provide at least one environment for testing and validation before production_
  - _Large computations must be done and checked before on a small part of data_
  - _..._
- Measure data quality and related costs
  - _Ask data scientists for KPIs to measure data quality_
  - _Time spent on developments / maintenance_
  - _Infrastructure costs_
  - _..._
- Use identity and access management (IAM)
  - _to control and know who has access to the data_
- Watch for compliance with laws, regulations and confidentiality
