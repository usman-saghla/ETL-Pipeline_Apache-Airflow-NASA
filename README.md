# Airflow ETL Pipeline with Postgres and API Integration

## Project Overview

This project implements an end-to-end ETL (Extract, Transform, Load) pipeline using Apache Airflow that integrates with NASA's Astronomy Picture of the Day (APOD) API and persists data to a PostgreSQL database. Airflow orchestrates the entire workflow, enabling scheduling, monitoring, and reliable management of data ingestion tasks.

The solution is containerized using Docker, providing an isolated and reproducible environment for both Airflow and PostgreSQL services, while leveraging Airflow's hooks and operators for efficient ETL processing.

## Key Components

### 1. Apache Airflow for Orchestration
- Defines, schedules, and monitors the complete ETL pipeline
- Manages task dependencies to ensure sequential and reliable execution
- Uses a DAG (Directed Acyclic Graph) structure containing data extraction, transformation, and loading tasks

### 2. PostgreSQL Database
- Stores extracted and transformed data
- Runs in a Docker container for easy management and data persistence via volumes
- Accessed through Airflow's PostgresHook and PostgresOperator

### 3. NASA APOD API
- External data source providing daily astronomy picture information
- Returns JSON responses with metadata including title, explanation, and image URL
- Accessed via Airflow's SimpleHttpOperator for HTTP requests

## Project Objectives

- **Extract**: Retrieve astronomy data from NASA's APOD API on a daily schedule
- **Transform**: Process and filter API responses to ensure database-ready formatting
- **Load**: Persist transformed data into PostgreSQL for analysis, reporting, and visualization

## Architecture and Workflow

The pipeline executes three sequential stages within an Airflow DAG:

### Extract Phase (E)
- SimpleHttpOperator performs HTTP GET requests to NASA's APOD API
- API responses are received in JSON format containing picture title, explanation, and image URL

### Transform Phase (T)
- Airflow TaskFlow API (@task decorator) processes extracted JSON data
- Extracts and validates key fields: title, explanation, URL, and date
- Formats data according to database schema requirements

### Load Phase (L)
- PostgresHook loads transformed data into PostgreSQL tables
- Automatically creates target table if it doesn't exist during DAG execution
