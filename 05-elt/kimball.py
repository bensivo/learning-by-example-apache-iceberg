from pyspark.sql import SparkSession
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.functions import col, to_date, year, month, dayofmonth, dayofweek, weekofyear

builder = SparkSession.builder

# Configurations for Iceberg and the Nessie Catalog
builder.config("spark.sql.extensions","org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
builder.config("spark.sql.catalog.nessie","org.apache.iceberg.spark.SparkCatalog")
builder.config("spark.sql.catalog.nessie.type", "nessie")
builder.config("spark.sql.catalog.nessie.uri", "http://nessie:19120/api/v1")
builder.config("spark.sql.catalog.nessie.ref", "main")
builder.config("spark.sql.catalog.nessie.authentication.type", "NONE")
builder.config("spark.sql.catalog.nessie.warehouse", "s3a://")
builder.config("spark.sql.defaultCatalog", "nessie")

# Configurations for MinIO
builder.config("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
builder.config("spark.hadoop.fs.s3a.access.key", "my-access-key")
builder.config("spark.hadoop.fs.s3a.secret.key", "my-secret-key")
builder.config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
builder.config("spark.hadoop.fs.s3a.path.style.access", "true")
builder.config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

builder.appName("Kimball page_load")
builder.master("spark://spark-master:7077")
spark = builder.getOrCreate()


spark.sql(f"""
    CREATE SCHEMA IF NOT EXISTS star LOCATION 's3a://iceberg/star'
""")

# Create dimension tables (deduplicated, with surrogate keys)
spark.sql("""
CREATE TABLE IF NOT EXISTS star.dim_user (
    user_id BIGINT,
    user_name STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS star.dim_page (
    page_id BIGINT,
    page STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS star.dim_browser (
    browser_id BIGINT,
    browser STRING
)
""")




# Load distinct dimension values and assign surrogate keys
user_df = spark.sql("SELECT DISTINCT user_name FROM model.page_load").withColumn("user_id", monotonically_increasing_id())
page_df = spark.sql("SELECT DISTINCT page FROM model.page_load").withColumn("page_id", monotonically_increasing_id())
browser_df = spark.sql("SELECT DISTINCT browser FROM model.page_load").withColumn("browser_id", monotonically_increasing_id())

# Write dimension tables
user_df.select("user_id", "user_name").write.mode("overwrite").format("iceberg").saveAsTable("star.dim_user")
page_df.select("page_id", "page").write.mode("overwrite").format("iceberg").saveAsTable("star.dim_page")
browser_df.select("browser_id", "browser").write.mode("overwrite").format("iceberg").saveAsTable("star.dim_browser")

# Date dimension takes a little more processing
spark.sql("""
CREATE TABLE IF NOT EXISTS star.dim_date (
    date_id BIGINT,
    date DATE,
    year INT,
    month INT,
    day INT,
    day_of_week INT,
    week_of_year INT
)
""")
date_df = spark.sql("SELECT DISTINCT to_date(event_ts) AS date FROM model.page_load")
date_df = date_df \
    .withColumn("year", year("date")) \
    .withColumn("month", month("date")) \
    .withColumn("day", dayofmonth("date")) \
    .withColumn("day_of_week", dayofweek("date")) \
    .withColumn("week_of_year", weekofyear("date")) \
    .withColumn("date_id", monotonically_increasing_id())
date_df.select("date_id", "date", "year", "month", "day", "day_of_week", "week_of_year") \
    .write.mode("overwrite").format("iceberg").saveAsTable("star.dim_date")

# Create the fact table structure
fact_df = spark.sql("SELECT * FROM model.page_load") \
    .withColumn("date", to_date("event_ts")) \
    .join(user_df, on="user_name", how="left") \
    .join(page_df, on="page", how="left") \
    .join(browser_df, on="browser", how="left") \
    .join(date_df, on="date", how="left") \
    .select(
        "event_name",
        "event_version",
        "event_ts",
        "date_id",
        "user_id",
        "page_id",
        "browser_id",
    )


# Update fact table definition
spark.sql("""
CREATE TABLE IF NOT EXISTS star.fact_page_load (
    event_name STRING,
    event_version STRING,
    event_ts TIMESTAMP,
    date_id BIGINT,
    user_id BIGINT,
    page_id BIGINT,
    browser_id BIGINT
)
""")

# Write updated fact table
fact_df.write.mode("overwrite").format("iceberg").saveAsTable("star.fact_page_load")