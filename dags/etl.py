from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import json   # added

# DAG definition
with DAG(
    dag_id="nasa_apod_postgres",
    start_date=datetime.now() - timedelta(days=1),
    schedule="@daily",   # updated from schedule_interval
    catchup=False,
) as dag:

    # Step 1. Create the table
    @task
    def create_table():
        hook = PostgresHook(postgres_conn_id="my_postgres_connection")

        query = """
            CREATE TABLE IF NOT EXISTS apod_data (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                explanation TEXT,
                url TEXT,
                date DATE,
                media_type VARCHAR(50)
            );
        """
        hook.run(query)

    # Step 2. Call NASA APOD API
    extract_apod = HttpOperator(
        task_id="extract_apod",
        http_conn_id="nasa_api",
        endpoint="planetary/apod",
        method="GET",
        data={"api_key": "{{ conn.nasa_api.extra_dejson.api_key }}"},
        log_response=True,   # changed: response_filter removed
    )

    # Step 3. Transform API response
    @task
    def transform_apod_data(response_text):  # changed name
        response = json.loads(response_text)  # changed: parse JSON
        return {
            "title": response.get("title", ""),
            "explanation": response.get("explanation", ""),
            "url": response.get("url", ""),
            "date": response.get("date", ""),
            "media_type": response.get("media_type", "")
        }

    # Step 4. Load the transformed data into Postgres
    @task
    def load_data_to_postgres(apod):
        hook = PostgresHook(postgres_conn_id="my_postgres_connection")

        insert_sql = """
            INSERT INTO apod_data (title, explanation, url, date, media_type)
            VALUES (%s, %s, %s, %s, %s);
        """

        hook.run(
            insert_sql,
            parameters=(
                apod["title"],
                apod["explanation"],
                apod["url"],
                apod["date"],
                apod["media_type"],
            )
        )

    # Step 6. Set task order
    table_task = create_table()
    transformed = transform_apod_data(extract_apod.output)
    load_task = load_data_to_postgres(transformed)

    table_task >> extract_apod >> transformed >> load_task
