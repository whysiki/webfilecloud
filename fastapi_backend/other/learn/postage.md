# PostgreSQL User and Database Management

## How do I create a user and database, and grant permissions?

### Steps:
1. **Create a user:**
    ```sql
    CREATE USER whyski WITH PASSWORD '778899vvbbnnmm';
    ```

2. **Create a database:**
    ```sql
    CREATE DATABASE filecloud;
    ```

3. **Grant all privileges on the database to the user:**
    ```sql
    GRANT ALL PRIVILEGES ON DATABASE filecloud TO whyski;
    ```

4. **Grant all privileges on the public schema to the user:**
    ```sql
    GRANT ALL PRIVILEGES ON SCHEMA public TO whyski;
    ```

## How can I log in to PostgreSQL and verify user permissions?

### Login as the new user:
```bash
psql -U whyski -d filecloud -h localhost -p 5432
```

### Verify user permissions:
```sql
SELECT usename AS username, passwd AS password FROM pg_shadow;
```

## How can I view all tables in a PostgreSQL database?

### List all tables:
```sql
\dt
```

## How can I view the structure of a specific table?

### View table structure:
```sql
\d table_name
```

## How can I create a table, insert a record, and view the data?

### Create a table:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);
```

### Insert a record:
```sql
INSERT INTO users (username, password) VALUES ('john_doe', 'password123');
```

### View table data:
```sql
SELECT * FROM users;
```

## How can I grant privileges on a schema?

### Grant privileges on a schema:
```sql
GRANT ALL PRIVILEGES ON SCHEMA public TO whyski;
```

## How can I create a schema and a table within it?

### Create a schema:
```sql
CREATE SCHEMA myschema;
CREATE SCHEMA whyshi;
```

### Delete a schema:
```sql
DROP SCHEMA whyshi CASCADE;
```

### Create a table within the schema:
```sql
CREATE TABLE whyshi.mytable (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);
```

## How can I use SQLAlchemy to create tables in a specific schema?

### Using SQLAlchemy to connect and create tables:
```python
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String

engine = create_engine('postgresql://whysiki:password@localhost:5432/filecloud')

metadata = MetaData()

my_table = Table('mytable', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    schema='myschema'
)

metadata.create_all(engine)
```

### Using SQLAlchemy ORM to define tables:
```python
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'myschema'}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Not plain text password
    files = relationship("File", secondary=association_table)
    register_time = Column(String, default="")

class File(Base):
    __tablename__ = "files"
    __table_args__ = {'schema': 'myschema'}
    id = Column(Integer, primary_key=True, index=True)  # The hash value of the file content + hash(username) as the file ID
    filename = Column(String, unique=False, index=True)
    file_path = Column(String)
    file_size = Column(String)
    file_owner_name = Column(String)
    file_create_time = Column(String)
    file_type = Column(String, default="binary")
```

## How can I revoke privileges from a user?

### Revoke all privileges on a schema:
```sql
REVOKE ALL PRIVILEGES ON SCHEMA public FROM whyski;
```

## How can I clear a database?

### Drop all tables in the current schema:
```sql
DO $$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;
```

## How can I switch databases in PostgreSQL?

### Switch database:
```bash
\c your_database_name
```

## How can I view the structure of a table?

### View table structure:
```sql
\d your_table_name
```

## Why can't I find the table I created?

If you created a table but can't find it, you might be looking in the wrong schema.

### Check specific schema:
```sql
\dt whyshi.*
```

## How can I view all schemas?

### List all schemas:
```sql
SELECT schema_name FROM information_schema.schemata;
```

## How can I view all contents of a schema?

### List all tables in a specific schema:
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'whyshi';
```

## How can I modify the association_table definition to specify a schema?

### Specify schema in association_table:
```sql
CREATE TABLE whyshi.association (
    column1 datatype,
    column2 datatype,
    ...
);
```

## How can I drop a table with CASCADE?

### Drop table with CASCADE:
```sql
DROP TABLE whyshi.users CASCADE;
```

## what the CASCADE?

In PostgreSQL, the `CASCADE` option in the `DROP TABLE` statement is used to automatically drop objects that depend on the table being dropped. This includes foreign key constraints, views, and other dependent objects. Using `CASCADE` ensures that the table and all related dependencies are removed from the database.

#### Example of using `CASCADE`:

```sql
DROP TABLE mytable CASCADE;
```



### clear a db
```sql
DO $$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;
```


## how can i view all db in psql?

```sql
\l
```
or
```sql
\list
```