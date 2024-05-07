from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    from_json,
    sum,
    avg,
    to_timestamp,
    when,
    window,
)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


def write_to_postgres(df, epoch_id, table_name: str) -> None:
    """
    Writes a DataFrame to PostgreSQL using JDBC.

    Args:
        df: DataFrame to write.
        epoch_id: Epoch ID of the streaming batch.
        table_name: Name of the PostgreSQL table.

    This function uses JDBC to append data to a PostgreSQL table, ensuring that
    data is persisted in a relational database for later analysis and reporting.
    """
    jdbc_url = "jdbc:postgresql://postgres:5432/logs"
    properties = {
        "user": "admin",
        "password": "admin",
        "driver": "org.postgresql.Driver",
    }
    df.write.jdbc(url=jdbc_url, table=table_name, mode="append", properties=properties)


def main() -> None:
    """
    Main function to initialize Spark session and process streaming data.
    """
    # Initialize Spark session for processing
    spark = SparkSession.builder.appName("KafkaStreamExample").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Kafka configuration details
    kafka_topic_name = "logs"
    kafka_bootstrap_servers = "kafka:9092"

    # Define the schema for the incoming logs
    schema = StructType(
        [
            StructField("timestamp", StringType(), True),
            StructField("application_id", StringType(), True),
            StructField("log_level", StringType(), True),
            StructField("error_code", IntegerType(), True),
            StructField("message", StringType(), True),
            StructField("request_type", StringType(), True),
            StructField("url", StringType(), True),
            StructField("user_agent", StringType(), True),
            StructField("session_id", IntegerType(), True),
            StructField("response_time_ms", IntegerType(), True),
        ]
    )

    # Read data from Kafka using structured streaming
    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
        .option("subscribe", kafka_topic_name)
        .option("startingOffsets", "earliest")
        .load()
    )

    # Parse the JSON data and apply the schema
    json_df = df.selectExpr("CAST(value AS STRING) as json").select(
        from_json(col("json"), schema).alias("data")
    )

    # Extract relevant fields from the JSON data
    exploded_df = json_df.select(
        to_timestamp(col("data.timestamp")).alias("timestamp"),
        "data.application_id",
        "data.log_level",
        "data.error_code",
        "data.request_type",
        "data.response_time_ms",
        "data.user_agent",
    )

    # Aggregate data based on application ID and a sliding window
    app_metrics_df = (
        exploded_df.groupBy("application_id", window("timestamp", "10 seconds"))
        .agg(
            (
                sum(when(col("error_code") >= 400, 1).otherwise(0)) / count("*") * 100
            ).alias("error_rate"),
            avg("response_time_ms").alias("average_latency"),
            count(when(col("request_type") == "GET", True)).alias("get_requests"),
            count(when(col("request_type") == "POST", True)).alias("post_requests"),
            count(when(col("request_type") == "PUT", True)).alias("put_requests"),
            count(when(col("request_type") == "DELETE", True)).alias("delete_requests"),
        )
        .select(
            "application_id",
            col("window.start").alias("startdate"),
            col("window.end").alias("enddate"),
            "error_rate",
            "average_latency",
            "get_requests",
            "post_requests",
            "put_requests",
            "delete_requests",
        )
    )

    # Setup the streaming query to write the aggregated results to PostgreSQL
    app_query = (
        app_metrics_df.writeStream.outputMode("update")
        .foreachBatch(
            lambda df, epoch_id: write_to_postgres(df, epoch_id, "application_metrics")
        )
        .start()
    )

    # Wait for all processing to be done
    app_query.awaitTermination()


if __name__ == "__main__":
    main()
