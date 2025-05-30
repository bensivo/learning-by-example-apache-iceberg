from pyspark.sql import SparkSession

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

builder.appName("Model page_load")
builder.master("spark://spark-master:7077")
spark = builder.getOrCreate()


spark.sql(f"""
    CREATE SCHEMA IF NOT EXISTS model LOCATION 's3a://iceberg/model'
""")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS model.page_load (
        event_name STRING,
        event_version STRING,
        event_ts TIMESTAMP,
        page STRING,
        user_name STRING,
        browser STRING
    )
    USING ICEBERG
    PARTITIONED BY (event_ts);
""")

# Convert rows from the staging table into the model schema
df = spark.sql(f"""
SELECT
    metadata.name AS event_name,
    metadata.version AS event_version,
    CAST(metadata.timestamp AS TIMESTAMP) AS event_ts,
    payload.page AS page,
    payload.user_name AS user_name,
    payload.browser AS browser
FROM staging.page_load_v1
ORDER BY event_ts
""")
df.show()
print(f"Number of rows {df.count()}")

# Remove duplicates
df = df.dropDuplicates()
df.show()

# Write the output to the model table
df.write \
    .format("iceberg") \
    .mode("overwrite") \
    .saveAsTable("model.page_load")
print('Done')