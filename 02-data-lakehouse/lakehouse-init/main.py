from trino.dbapi import connect

def main():
    connection = connect(
        host="trino",
        port=8080,
        user="admin",
        catalog="iceberg",
    )
    print("Connected")

    cursor = connection.cursor()

    print("Creating schema 'staging'")
    cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS staging WITH ( LOCATION = 's3://iceberg/staging' )
    """)
    cursor.fetchall()

    print("Creating table 'staging.hello_world'")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging.hello_world(
            greeting VARCHAR,
            name VARCHAR
        )
    """)
    cursor.fetchall()

    print("Inserting records into 'staging.hello_world'")
    cursor.execute("""
        INSERT INTO staging.hello_world VALUES
        ('Hello', 'Alice'),
        ('Hello', 'Bob'),
        ('Hello', 'Charlie')
    """)
    cursor.fetchall()

    print("Selecting from 'staging.hello_world'")
    cursor.execute("""
        SELECT * FROM staging.hello_world
    """)
    rows = cursor.fetchall()
    print(rows)


if __name__ == "__main__":
    main()
