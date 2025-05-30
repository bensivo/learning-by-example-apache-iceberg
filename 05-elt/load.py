from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name,current_timestamp 

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

builder.appName("Load page_load")
builder.master("spark://spark-master:7077")
spark = builder.getOrCreate()


spark.sql(f"""
    CREATE SCHEMA IF NOT EXISTS staging LOCATION 's3a://iceberg/staging'
""")

df = spark.read \
        .option("recursiveFileLookup", "true") \
        .json("s3a://raw/page_load/v1/")

df =  df.withColumn("loaded_at", current_timestamp())
df =  df.withColumn("loaded_from", input_file_name())

df.printSchema()
df.show()


df.write \
.format('iceberg') \
.mode('overwrite') \
.partitionBy('loaded_from') \
.saveAsTable("staging.page_load_v1")
