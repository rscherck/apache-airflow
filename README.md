```
Creates a local set of local docker containers for building, running, and testing an Apache
Airflow environment and Directed Acyclic Graphs (DAGs)

https://airflow.apache.org/docs/apache-airflow/stable/index.html

```

```
Initialization
docker compose up airflow-init

```

```
Running the environment
docker compose up

http://localhost:8080

```

```
Cleaning up
docker compose down --volumes --rmi all

```
