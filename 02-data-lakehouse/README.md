# 02 Data Lakehouse

## Introduction
In the previous module, we initialized a Data Lake, a storage layer for all the raw data produced in our company. 
However, for running analytics, we need to be able to query and manipulate this data, and raw JSON records in object-storage are not very efficient for querying.

Consider this simple SQL Query:
```
    SELECT * FROM page_loads
    WHERE payload.page = '/home'
```

To resolve this query, we would have to load every single file in our data lake one-by-one, then extract just the matching records. It would be horribly inefficient and expensive. Instead, we're going to first 'load' our data into our Data Lakehouse, which will enable us to query it much more efficiently.

A Data Lakehouse consists of 3 components:
- A data storage layer (MinIO in this case), with tables written in an Open Table Format (OTF)
- A data catalog
- A query /compute engine


The Open Table Format is a structured format for saving tabular data, including both the data itself plus metadata which enables more efficient querying and computation. In this project, our Open Table Format is Apache Iceberg.

Next, the catalog is a service that maps OTF file locations to SQL-like table names. This simplifies our queries - allowing us to write `SELECT * FROM raw.page_loads` instead of `SELECT * FROM 's3://iceberg/staging/page_loads_{uuid}/metadata.json'`. In this project, we'll use a simple open-source catalog called Nessie. 

And finally, the query engine is what actually executes our SQL queries. This is where the Open Lakehouse truly shines. Becuase our storage and catalog layers are both independent services, we can plug in any number of query engines, choosing the one that is most appropriate for our needs. Here are a few options popular with Iceberg Lakehouses:
- DuckDB - a small, local query engine allowing users to query iceberg tables directly from a single client process.
- Apache Spark - a large-scale, distributed compute engine, which plans and executes queries using parallel computation and fleets of nodes. Used for very large scale data processing.
- Apache Presto / Trino - a standalone query engine which can query a wide range of data-sources (including iceberg), while exposing just a single accessible endpoint. Frequently used as an adapter / entrypoint for  traditional SQL clients (which may expect JDBC protocols or similar) accessing the Data Lakehouse.

Apache Spark and Trino are often deployed side-by-side. Teams use Spark for ETL, loading raw data into the lakehouse, then cleaning and transforming it. Then they use Trino to query the cleaned, ready-to-go datasets. However, you can technically write tables using Trino as well (just not very large tables), so in this project, we'll just use Trino.


In this module, we'll just use DuckDB for its simplicity. We may do entirely differnet LBE projects for Apache Spark and Presto in the future.

## Running Nessie
Run the nessie catalog using the script below:
```
./nessie.sh
```

Then open your browser to http://localhost:19120 to see the nessie homepage. It'll be empty for now, becuase we don't have any tables registered.
![alt text](images/nessie.png)


## Running Trino
Run the trino query engine using the script below:
```
./trino.sh
```

Then open your browser to http://localhost:8080, you'll see the trino login page. Just enter 'admin' and you'll be redirected to the trino dashboard. The Trino dashboard shows metrics and the actual SQL queries being executed.
![alt text](images/trino.png)

It's worth looking at how trino itself is configured. To access tables stored in MinIO, cataloged in Nessie, we need to create a catalog configuration file, and mount it to the Trino docker container. The file `trino/iceberg.properties` (mounted to `/etc/trino/catalog/iceberg.properties` in the docker container) contains the configurations for nessie and minio:
```
# Specify the format of tables in this catalog
connector.name=iceberg

# Nessie configuration
iceberg.catalog.type=nessie
iceberg.nessie-catalog.uri=http://nessie:19120/api/v1
iceberg.nessie-catalog.ref=main
iceberg.nessie-catalog.default-warehouse-dir=s3://iceberg

# S3 / MinIO configuration
fs.native-s3.enabled=true
s3.endpoint=http://minio:9000
s3.region=us-east-1
s3.path-style-access=true
s3.aws-access-key=my-access-key
s3.aws-secret-key=my-secret-key
```

## Initializing the Lakehouse
As with any database, before we can insert data, we need to create schemas and tables with `CREATE SCHEMA` and `CREATE TABLE` commands.
The folder `lakehouse-init` contains a basic python application which uses the Trino Python SDK to create a `staging` schema and a `staging.hello_world` table, using SQL.

Looking at the code, you'll notice that when we create a schema, we also specifiy a "LOCATION". This maps the schema to a directory in our object-storage bucket. Any tables created in that schema will live under that folder-path.
``` SQL
CREATE SCHEMA IF NOT EXISTS staging WITH ( LOCATION = 's3://iceberg/staging' )
```

Other than that one change, interacting with tables is the same as standard SQL:
``` SQL
CREATE TABLE IF NOT EXISTS staging.hello_world(
    greeting VARCHAR,
    name VARCHAR
)
```

Run the full init script with :
```
./lakehouse-init.sh
```

After it runs, you should see new folders MinIO for the `staging.hello_world` table, at `iceberg/staging/hello_world-<random>/`
![alt text](images/minio-iceberg-table.png)

If you look into this `hello_world` folder, you'll see 2 subfolders, 'metadata' and 'data':

- 'metadata' contains JSON and avro files, with a variety of information including the table's schema, snapshot information, and indexes of the table's values. These files are mostly used in query planning.

- 'data' contains the actual contents of the table, stored in .parquet format. A single table will by split into several parquet files, to enable horizontal scale and parallel computation.



Additionally, if you go to nessie, you'll see that our table has also been registered there. You'll see a folder for the schema `staging`, and a table `hello_world`. Opening up that table, all it contains is a reference to the MinIO filepath where the iceberg metadata is stored (the metadata itself contains references to the data files):
![alt text](images/nessie-iceberg-table.png)

