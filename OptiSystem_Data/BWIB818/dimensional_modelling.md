## What is the main goal of dimensional modeling?
* Its main goal is simplicity.

---

## What kind of technique is dimensional modeling?
* Dimensional modeling is a logical design technique for structuring data so that it’s intuitive to business users and delivers fast query performance.

---

## Is dimensional modeling the preferred approach?
* Yes, dimensional modeling is widely accepted as the preferred approach for DW/BI (Data Warehouse/Business Intelligence) presentation.

---

## What must a dimensional model support?
* It must support the full range of analyses both now and for the foreseeable future.

---

## What are the three core design goals of dimensional modeling?
* **Goal 1 (Simplicity):** Information presented to the user must be as simple as possible and easy to understand. Information is grouped into coherent business categories. This information reflects the complex business processes. DM usually presents the same information in a normalized database with much fewer tables.
* **Goal 2 (Speed):** Query results should be returned as quickly as possible. This is done differently in relational and OLAP environments. 
    * In **relational environments**, we **denormalize**, **pre-join** hierarchies and lookup tables, and create **predictable** frameworks. 
    * In **OLAP environments**, we use **engines** which support DM, and **aggregation** across and within dimensions.
* **Goal 3 (Accuracy):** Relevant information should be presented to accurately track underlying business processes.

---

## What are the key benefits of dimensional modeling?
* Understandability.
* Fast query performance.
* Each dimension is an equivalent entry point into the fact table.
* Graceful extensibility to add new data.

---

## What is a "Star Join"?
* This is a normalized table surrounded by denormalized dimensions.
* In a relational database, it is called a star schema, and in MOLAP environments, it is a cube.

---

## What is a fact table and how is it structured?
* A fact table is a highly normalized structure which consists of measurements associated with the business process. 
* A record is a measurement of the entire business event. 
* The primary key is a composite key consisting of the subset of foreign keys from the different dimensions. 
* A fact table always has many-to-many relationships between dimensions.

---

## What are facts and how are they classified?
* Facts are numeric values which quantify the magnitude of an event. 
* There are 3 types of facts, namely: additive, semi-additive, and non-additive.
* **Additive facts** can be meaningfully aggregated across dimensions.
* Not all numeric data are facts and will behave more as descriptive attributes that will constrain a query.
* Some facts are derived from other facts. 
* Facts conform if they have the same definition in different fact tables.

---

## What is a "grain" in a fact table?
* The grain is the level of detail.
* The lowest level of detail is atomic, and it can be rolled up to a summary level.
* The fact table should be single grain.
* The fundamental grains for a fact table are transactions, periodic snapshots, and accumulating snapshots.
* Sometimes a single business process produces different levels of detail. We need to perform allocation to force the facts to be at the lowest level of detail.
* If allocation cannot be done, then we need to create separate fact tables.

---

## What are dimension tables and how do they function?
* Dimension tables are translated from nouns.
* They describe the objects that participate in the business process.
* They provide entry points into the data.
* They have single surrogate primary keys.
* **Conformed dimensions** are dimensions that are shared by 2 or more business processes.
* Some dimensions have an embedded hierarchy. This is a consequence of denormalization.
* *Note on design:* Relational transactional systems are designed using normalization (redundancies are removed, transaction update/loading is simple and fast), but spider-web joins make it complex to understand. Denormalization is the process of recombining attributes into a single dimension.

---

## What makes dimensions "conformed"?
* If 2 dimensions have one or more of the **same fields**, then they are **conformed**.
* These dimensions can either be **identical** or be a **subset** of a more granular dimension.
* They are the foundation of data warehouses.

---

## What are bus matrices used for?
* They represent the participation of conformed dimensions in multiple business processes.
* Each row is a business process and defines at least one fact table.

---

## What does it mean to "drill across"?
* It is analysis involving data from more than one business process.

---

## What are surrogate keys?
* These are a new set of keys, separate from the keys in the source system.
* They are unique values assigned to each row in a dimension (meaningless, artificial).
* These become the **primary key of the dimensional table** used to join with the foreign key in the fact table.

---

## What is snowflaking and why is it generally discouraged?
* Snowflaking involves **connecting** lookup tables to fields in dimension tables.
* It re-normalizes dimensions.
* This is a discouraged technique because the model becomes more complex.
* **Outrigger tables** are supported techniques instead. Outrigger tables are created to address rarely used lookups, a large number of attributes, different grains, and different update frequencies.

---

## How do we handle Slowly Changing Dimensions (SCDs)?
* SCDs deal with attributes which change over time, and we need to be able to track these changes.
* There are 4 main types of changes over time:
    * **Type 1:** Changes that the business does not care about. We overwrite existing attribute values with a new value.
    * **Type 2:** The creation of new rows, surrogate keys, and date stamps.
    * **Type 3:** Keeping separate columns for old and new attribute values.
    * **Type 4:** Separate frequently changing attributes into their own dimension tables. We create a new surrogate key for this.

---

## What are the steps in the dimensional modeling process?
* The introduction
* The preparation
* The data profiling and source system exploration
* Building the dimensional model
* The process flow
* Avoiding common misconceptions about the DM