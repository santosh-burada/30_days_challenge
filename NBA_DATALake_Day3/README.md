# 30 Days of Cozy Cloud Crew Challenge: Day 3 - Building a Serverless Data Lake

## Overview
In this challenge, we will create a serverless data lake on AWS using Amazon S3, AWS Glue, and Amazon Athena. This data lake will enable us to fetch, store, catalog, and query NBA player data efficiently without the need for managing servers.

---

## What Happens in AWS When Running the Script

### 1. **S3 Bucket Creation (`create_s3_bucket`)**
- The script attempts to create an S3 bucket named `sports-data-lake`.
- If the bucket already exists, the creation step is skipped.
- If the bucket does not exist, AWS provisions the bucket in the specified region (e.g., `us-east-1`).
- The bucket serves as a central repository to store raw and processed data for our data lake.

### 2. **Glue Database Creation (`create_glue_database`)**
- A Glue database named `glue_nba_data_lake` is created to organize data assets.
- Glue databases act as metadata catalogs, defining where data is stored (e.g., in S3) and its schema (table structure).

### 3. **Data Fetching and Storage (`fetch_nba_data` and `upload_data_to_s3`)**
- NBA data is fetched from an external API and temporarily stored in memory.
- The fetched data is uploaded to the S3 bucket as a JSON file under `raw-data/nba_player_data.json`.

### 4. **Glue Table Creation (`create_glue_table`)**
- A Glue table named `nba_player_data` is created within the `glue_nba_data_lake` database.
- The table defines the schema of the JSON data stored in S3 (e.g., columns like `player_id`, `team`, `points_per_game`).
- AWS Glue connects the schema to the raw data in S3, making it queryable by Athena.

### 5. **Athena Configuration and Querying (`configure_athena`)**
- Athena is configured to output query results to a specific S3 location (`s3://sports-data-lake/athena-results/`).
- Athena enables SQL-like querying of the data defined in the Glue table.
- This allows for analysis of the NBA data without extensive preprocessing.

---

## Relationship Between S3, Glue, and Athena

### **Amazon S3 (Data Storage)**
- S3 acts as the backbone of the data lake, serving as the storage layer for raw and processed data.
- In this script, fetched NBA data is uploaded to the S3 bucket as a JSON file.
- S3 provides high durability, availability, and scalability for storing large datasets.

### **AWS Glue (Data Catalog and ETL)**
- Glue acts as the metadata catalog for the data stored in S3.
- It defines the schema (table structure) of the raw data in S3, organizing it for querying.
- Glue also supports ETL (Extract, Transform, Load) operations for cleaning and transforming data.
- In this script, Glue links the `nba_player_data` table to the raw JSON data in S3.

### **Amazon Athena (Data Querying and Analysis)**
- Athena is a serverless query engine that allows SQL-like queries on data stored in S3.
- It uses the Glue catalog to understand the structure of the data (e.g., columns and data types).
- Athena executes SQL queries directly on the data in S3, and query results are stored back in S3 for later use.
- In this script, Athena queries the Glue table (`nba_player_data`) and outputs results to the specified S3 location.

---

## How These Components Work Together

1. **Data Ingestion:**
   - Data is fetched from an external API and stored in S3.

2. **Metadata Cataloging:**
   - Glue catalogs the S3 data by creating a database and table that define its schema.

3. **Data Querying:**
   - Athena uses the Glue metadata to run SQL queries on the S3 data.
   - This makes the data immediately available for analysis without needing a dedicated database or data warehouse.

---

## Benefits of This Architecture

1. **Serverless and Scalable:**
   - No need to manage servers for storage, ETL, or querying. AWS automatically scales resources based on usage.

2. **Cost-Effective:**
   - Pay only for S3 storage and Athena query execution.
   - Glue charges minimal costs for metadata storage and ETL jobs.

3. **Seamless Integration:**
   - S3 stores the data, Glue provides schema and metadata, and Athena allows SQL queries—all working together seamlessly.

---

This approach creates a robust and efficient data lake for analyzing NBA data using AWS services.

### Below Links helped me to get started with the project



Linkedin: [LinkedIn concept of Location Contraint](https://www.linkedin.com/pulse/quick-fix-location-constraints-s3-createbucket-api-imoh-etuk-e5juf/)

Medium: [About sessions and origin of boto3](https://ben11kehoe.medium.com/boto3-sessions-and-why-you-should-use-them-9b094eb5ca8e)