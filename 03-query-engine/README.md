# 03 Query Engine

## Introduction
The next main component of our Lakehouse, the query engine is what actually executes our SQL queries. This is where the Open Lakehouse truly shines. Becuase our storage and catalog layers are both independent services, we can plug in any number of query engines, choosing the one that is most appropriate for our needs. Here are a few options popular with Iceberg Lakehouses:
- DuckDB - a small, local query engine allowing users to query iceberg tables directly from a single client process.
- Apache Spark - a large-scale, distributed compute engine, which plans and executes queries using parallel computation and fleets of nodes. Used for very large scale data processing.
- Apache Presto / Trino - a standalone query engine which can query a wide range of data-sources (including iceberg), while exposing just a single accessible endpoint. Frequently used as an adapter / entrypoint for  traditional SQL clients (which may expect JDBC protocols or similar) accessing the Data Lakehouse.



In this module, we'll deploy the Trino Query engine, which started as a fork of Apache Presto, but has since eclipsed Presto in popularity and maturity.

## Running Trino
Run the trino query engine using the script below:
```
./trino.sh
```

Then open your browser to http://localhost:8080, you'll see the trino login page. Just enter 'admin' and you'll be redirected to the trino dashboard. The Trino dashboard shows basic metrics and the actual SQL queries being executed.
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

## Running some SQL
As with any database, before we can insert data, we need to create schemas and tables with `CREATE SCHEMA` and `CREATE TABLE` commands.
The folder `sql` contains a some basic SQL queries, you can run them using any SQL application that supports Trino - I use the "sqltools" extension of vscode

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

Run through all the SQL queries to create a simple hello-world table with a few records in it.

After it runs, go to MinIO to see the new folders containing the Iceberg `staging.hello_world` table, at `iceberg/staging/hello_world-<random>/`
![alt text](images/minio-iceberg-table.png)

Additionally, if you go to nessie, you'll see that our table has also been registered there. You'll see a folder for the schema `staging`, and a table `hello_world`. Opening up that table, all it contains is a reference to the MinIO filepath where the iceberg metadata is stored (the metadata itself contains references to the data files):
![alt text](images/nessie-iceberg-table.png)


## Anatomy of an Iceberg Table

If you open MinIO, you'll see a new folder appears in the "bronze" bucket, called `hello_world_<uuid>`. This is the Apache Iceberg table. Inside this folder is 2 subfolders, 'metadata' and 'data':

- 'metadata' contains JSON and avro files, with a variety of information including the table's schema, snapshot information, and indexes of the table's values. These files are mostly used in query planning.

- 'data' contains the actual contents of the table, stored in .parquet format. A single table will by split into several parquet files, to enable horizontal scale and parallel computation.
![alt text](images/minio-iceberg-table.png)

And because we used a nessie catalog to write this table, if you open Nessie, you'll see the "bronze" schema with a single "hello_world" table in it. If you click on the table, you'll find that all it contains is a reference to the filepath of the table in MinIO.

![alt text](images/nessie-table.png)


Now, if you want further process this iceberg table, you have 2 options for referencing it:
- Directly access the file location in MinIO
- Use a nessie-compatible client, and access it by its name in the catalog

In most cases, we'll prefer to use Nessie and a Table name.