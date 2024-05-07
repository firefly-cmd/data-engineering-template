# Use an official Spark base image with Python support
FROM apache/spark:python3

# Set the working directory in the container
WORKDIR /app

# Change to root to install packages
USER root

# Copy the Python dependencies file to the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code of the Spark job into the container
COPY ./src /app/

# Command to run the Spark job script
CMD ["/opt/spark/bin/spark-submit", "--master", "spark://spark-master:7077", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.2.18", "--conf", "spark.jars.ivy=/tmp/.ivy", "/app/spark_streaming_job.py"]



