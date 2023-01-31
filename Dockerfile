# Use an official Python runtime as the base image
FROM python:3.8

# Set the working directory
WORKDIR /app

# Install the necessary packages for data engineering and analytics
RUN pip install psycopg2-binary airflow pandas numpy

# Install PostgreSQL
RUN apt-get update && apt-get install -y postgresql postgresql-contrib

# Install Airflow
RUN pip install apache-airflow

# Install Power BI dependencies
RUN apt-get install -y libssl1.1 libcurl4 libunwind8 libgdiplus liblttng-ust0

# Add the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Expose the necessary ports
EXPOSE 8080 5432
