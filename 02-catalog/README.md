# 02 Catalog

## The Iceberg Catalog
Before we can create tables using Apache Iceberg, we need to talk about catalogs. 

Iceberg Catalogs solve 1 very necessary problem that you encounter in a Lakehouse. 
Technically, in a Lakehouse, tables are just files saved object-storage. 
However, when we read or write to tables, we refer to them using a name like "my_schema.my_table". 

The catalog is simply the service that translates between a table's name, and it's location in object-storage. 
In practice, many catalog implementations also include other features like RBAC, logging, and lineage tracking.

In this module, we'll run a very simple open-source Iceberg catalog called Nessie.

## Running the Nessie Catalog
Run nessie with the script below:
```
./nessie.sh
```

Nessie will be available in your browser at http://localhost:19120

![Nessie UI](./images/nessie.png)


That's it for this module, we'll actaully use nessie in the next one.