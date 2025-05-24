# 01 Data Lake

## Introduction
Apache Iceberg is one of the core technologies used to build a modern Open Data LakeHouse. However, in practice, we often start with just a Data Lake.

A Data Lake is a single location for storing all the raw data relevant to your organization / company, and is the foundation of analytics at any organization. 
Keeping an original, untouched record of events is invaluable as you move into the future, because you never know what use-cases for this data will come up.

Data Lakes today are usually built on cloud-based object storage services (AWS S3, Azure Blob, etc.), because of their reliability and low price.
To build a Data Lake, all you need to do is define some standardized folder-structure for your data, then start inserting data into that folder structure. 

In this module, we'll run MinIO, an open-sourced object-storage service mimicing the AWS S3 APIs. Then, we'll run a script to insert a bunch of fake data into the datalake. 


## Running MinIO
First, run the minio docker image defined in our `compose.yml`:
```
./minio.sh
```

Open your browser to http://localhost:9001/login. You will see the MinIO login page, where you can provide the username and password (which were set via Env Variables in compose.yml) `my-access-key` and `my-secret-key`.

![The MinIO login page](images/minio-login.png)

After you login, you'll see 2 buckets, "raw" and "iceberg". For this project, "raw" will be our data lake, and "iceberg" will be our data lakehouse.
![alt text](images/minio-buckets.png)

## Inserting Data
We'll generate some data to fill this data lake using a python script:
```
./generator.sh
```

For this datalake, we've decided on the following naming convention for data:
```
raw/${event_name}/${event_version}/${year}/${month}/${day}/${uuid}.${extension}
```

The script generates 10000 'page_load' events (split into 10 files with 1000 records each), and inserts them into the appropriate filepath using the current date.

![alt text](images/minio-data.png)

If you download and open one of these files, you'll see it's just JSON records. 
![alt text](images/jsonl.png)

These raw JSON records are definitely useful, but they're not exactly ready for querying and analytics. In the next module, we'll initialize our Data LakeHouse in the "iceberg" bucket of MinIO. Then we'll see how we can use the Apache Iceberg Open Table Format (OTF) to turn our object-storage bucket into a queryable, SQL-compatible Data Warehouse. 