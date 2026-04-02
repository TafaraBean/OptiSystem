## How are tables, attributes, and keys represented in ERD shorthand notation?
* In shorthand notation, the table name is written first, followed by its attributes in parentheses. 
* Primary keys are underlined (using the `<ins>` tag here).
* **Examples:**
  * CAR (<ins>CAR_VIN</ins>, MOD_CODE, CAR_YEAR, CAR_COLOUR)
  * CLASS (<ins>CRS_CODE</ins>, <ins>CLASS_SECTION</ins>, CLASS_TIME, ROOM_CODE, PROF_NUM)

---

## What is the difference between weak and strong relationships?
* **Weak relationships:** Exist if the Primary Key (PK) of the related entity does not contain a PK component of the parent entity.
* **Strong relationships:** Exist if the PK of the related entity contains a PK component of the parent entity.

---

## What are the characteristics of relationship participation and degrees?
* ![img_1774388117.png](/files/BWIB818/img_1774388117.png)
* Relationships can be unary, binary, or ternary.
* Unary relationships are recursive.

---

## What is a composite/bridge entity?
* ![img_1774388308.png](/files/BWIB818/img_1774388308.png)

---

## What are the steps in the database development process?
1. Create a description of operations.
2. Identify the business rules.
3. Identify entities and relationships.
4. Develop the initial ERD.
5. Identify the attributes and primary keys.
6. Revise the ERD and review.