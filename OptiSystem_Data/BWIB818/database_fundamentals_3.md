## What are the characteristics of a relational table?
* It is a 2-dimensional structure consisting of rows and columns.
* Each row is called an entity occurrence.
* Each column is called an attribute.
* A single row/column intersection is called a data value.
* All values in a column must have the same format.
* The specific range of values that an attribute/column can have is called the attribute domain.
* The order of rows and columns is immaterial.
* Each table must have an attribute or a combination of attributes that uniquely identifies each row.

---

## How do attributes, domains, degree, and cardinality function?
* An **attribute** is a named column in a relational table.
* An attribute draws its values from a **domain**, which is simply all possible values that an attribute may have.
* The **degree** is the number of attributes in a table.
* The **cardinality** is the number of rows in a table.

---

## What are keys and what types of keys are used in databases?
* Keys are attributes or combinations of attributes that uniquely identify each row.
* Keys work on determination, which means that knowing the value of A would determine the value of B.
* A **composite key** consists of more than one attribute.
* A **key attribute** is an attribute which is part of a composite key.
* **Superkeys** are those attributes which uniquely identify each row in a table.
* **Primary keys** are candidate keys which uniquely identify all other attributes in the given row. Primary keys cannot be null.
* **Secondary keys** are attributes which are used for data retrieval purposes.
* **Foreign keys** are attributes which must match with a primary key in another table or be null.

---

## What are nulls and why should they be handled carefully?
* Nulls mean there are no data entries.
* They are not permitted in primary keys.
* They should be avoided in other attributes because they potentially give rise to other problems in functions and relationships between tables.

---

## What is controlled redundancy and how do foreign keys help?
* Typically, data redundancy is bad (leads to issues like data anomalies) and occurs due to unnecessary duplication of data.
* However, sometimes multiple occurrences of values are required to make relationships work.
* Foreign keys are an example of this; they control data redundancies by using common attributes in many tables, which enables tables to be linked.

---

## What are the core database integrity rules?
* We need to have entity and referential integrity. Some RDBMSs automatically enforce these.
* **Entity integrity** requires that all primary keys be unique and not null so that foreign keys can reference them.
* **Referential integrity** requires that a foreign key either have a null entry or have an entry which matches with the primary key of another table.
* Referential integrity makes it impossible to delete a row with a primary key in a table which has a corresponding foreign key entry in another table.

---

## What is a Data Dictionary?
* It is a detailed accounting of all the tables in the databases.
* It contains all the attribute names and characteristics of the table.
* It contains the metadata and is known as the metadata repository.

---

## What are the different types of relationships within a relational database?
* **1:M (One-to-Many) relationships:** This should be the norm in any relational database design.
* **1:1 (One-to-One) relationships:** These should be rare. It means one entity is related to one other entity. This may sometimes mean that entity components were not defined properly and 2 entities could actually belong in the same table. However, certain conditions absolutely require their use.
* **M:N (Many-to-Many) relationships:** These cannot be implemented as such in a relational model. We must create composite/bridge entities to address the problems which come with many-to-many relationships.

---

## What is the purpose and structure of indexes?
* The aim of indexes is to optimize query speeds.
* The components of an index are the index key and the pointer.
* A unique index will only have one pointer.
* Each index is associated with only one table.

---

## How can we summarize the logical view of data?
* The logical view of data relies on 2D tables containing entity occurrences (rows) and attributes (columns). 
* Keys are essential for uniquely identifying rows and linking tables together through controlled redundancy. 
* Maintaining data integrity (entity and referential) and carefully managing relationships (aiming for 1:M) are critical for a functional relational database. 
* Indexes help speed up queries, and a data dictionary acts as a metadata repository to keep track of table characteristics.