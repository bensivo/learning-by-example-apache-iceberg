from pyspark.sql import SparkSession

builder = SparkSession.builder
builder.appName("Hello World")
builder.master("spark://spark-master:7077")

spark = builder.getOrCreate()

rows = [
    ('Hello', 'Alice'),
    ('Hello', 'Bob'),
    ('Hello', 'Charlie'),
]
cols = ['greeting', 'name']
df = spark.createDataFrame(rows, cols)

df.show()

spark.stop()