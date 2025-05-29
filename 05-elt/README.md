# 05 ELT

## Introduction
This module doesn't add any new technologies, but it goes through a basic Extract, Load, Transform process. All the raw data from module 01 is loaded into the lakehouse in a "staging" schema, then cleaned and organized into a "model" schema, and finally sliced into a dimensional-model in the "kimball" schema. 

## Running the scripts
First, read all the raw JSONL files and load them into an Iceberg table
```
./submit.sh load.py
```
You can query the results in your DBClient via Trino, using `load.sql`

Then, transform the loaded tale into a clean and modelled table:
```
./submit.sh model.py
```
You can query the results in your DBClient via Trino, using `model.sql`

And finally, slice up your model into a kimball star schema
```
./submit.sh kimball.py
```
You can query the results in your DBClient via Trino, using `kimball.sql`
