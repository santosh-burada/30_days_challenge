import boto3
import json
import time
import requests
from dotenv import load_dotenv
import os

load_dotenv()
class DataLake:
    def __init__(self):
        self.region = os.getenv("AWS_REGION")
        self.bucket_name = "sports-data-lake"
        self.glue_database_name = "glue_nba_data_lake"
        self.athena_output_location = f"s3://{self.bucket_name}/athena-results/"
        self.sports_data_api_key = os.getenv("NBA_API_KEY")
        self.nba_endpoint = os.getenv("NBA_ENDPOINT")
        self.session = boto3.Session(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('AWS_REGION'))
        self.s3 = self.session.client("s3")
        self.glue = self.session.client("glue")
        self.athena = self.session.client("athena")

    def create_s3_bucket(self):
        """Create an S3 bucket for storing sports data."""
        try:
            try:
                self.s3.head_bucket(Bucket=self.bucket_name)
                print(f'Bucket {self.bucket_name} already exists')
            except Exception as e:
                print(f"Creating S3 bucket '{self.bucket_name}'")

            if self.region == "us-east-1":
                self.s3.create_bucket(Bucket=self.bucket_name)
                print(f"S3 bucket '{self.bucket_name }' created successfully.")
            else:
                self.s3.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.region},
                )
                print(f"S3 bucket '{self.bucket_name }' created successfully in region {self.region}.")
        except Exception as e:
            print(f"Error creating S3 bucket: {e}")
    
    def create_glue_database(self):
        """Create a Glue database for the data lake."""
        try:
            self.glue.create_database(
                DatabaseInput={
                    "Name": self.glue_database_name,
                    "Description": "Glue database for NBA sports analytics.",
                }
            )
            print(f"Glue database '{self.glue_database_name}' created successfully.")
        except Exception as e:
            print(f"Error creating Glue database: {e}")
    def fetch_nba_data(self):
        """Fetch NBA player data from sportsdata.io."""
        try:
            headers = {"Ocp-Apim-Subscription-Key": self.sports_data_api_key}
            response = requests.get(self.nba_endpoint, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
            print("Fetched NBA data successfully.")
            return response.json()  # Return JSON response
        except Exception as e:
            print(f"Error fetching NBA data: {e}")
            return []
    def upload_data_to_s3(self, data):
        """Upload NBA data to the S3 bucket."""
        try:
            # Define S3 object key
            file_key = "raw-data/nba_player_data.json"
            
            # Upload JSON data to S3
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=json.dumps(data)
            )
            print(f"Uploaded data to S3: {file_key}")
        except Exception as e:
            print(f"Error uploading data to S3: {e}")
    def create_glue_table(self):
        """Create a Glue table for the NBA player data."""
        try:
            response = self.glue.create_table(
                DatabaseName=self.glue_database_name,
                TableInput={
                    "Name": "nba_player_data",
                    "Description": "NBA player data table",
                    "StorageDescriptor": {
                        "Columns": [
                            {"Name": "player_id", "Type": "string"},
                            {"Name": "first_name", "Type": "string"},
                            {"Name": "last_name", "Type": "string"},
                            {"Name": "team", "Type": "string"},
                            {"Name": "position", "Type": "string"},
                            {"Name": "points_per_game", "Type": "double"},
                            {"Name": "assists_per_game", "Type": "double"},
                            {"Name": "rebounds_per_game", "Type": "double"},
                        ],
                        "Location": f"s3://{self.bucket_name}/raw-data/",
                        "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                        "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",

                        "SerdeInfo": {
                            "SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe",
                        },
                    },
                    "TableType": "EXTERNAL_TABLE",
                },
            )
            print("Glue table 'nba_player_data' created successfully.")
        except Exception as e:
            print(f"Error creating Glue table: {e}")
    def configure_athena(self):
        """Set up Athena output location and create necessary tables."""
        try:
            # Create the database if it doesn't exist
            try:
                self.athena.start_query_execution(
                    QueryString="CREATE DATABASE IF NOT EXISTS nba_analytics",
                    QueryExecutionContext={"Database": self.glue_database_name},
                    ResultConfiguration={"OutputLocation": self.athena_output_location},
                )
                print("Athena output location configured successfully.")
            except Exception as e:
                print(f"Error configuring Athena: {e}")

            time.sleep(5)  # Wait for the query to complete

            # Create a table for player statistics
            self.athena.start_query_execution(
            QueryString=f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS nba_analytics.player_stats (
                player_id STRING,
                first_name STRING,
                last_name STRING,
                team STRING,
                position STRING,
                points_per_game DOUBLE,
                assists_per_game DOUBLE,
                rebounds_per_game DOUBLE
            )
            ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
            LOCATION 's3://sports-data-lake/raw-data/player_statistics/'
            """,
            QueryExecutionContext={"Database": "nba_analytics"},
            ResultConfiguration={"OutputLocation": self.athena_output_location},
            )
            time.sleep(5)  # Wait for the query to complete

            # Create a table for team statistics
            # self.athena.start_query_execution(
            # QueryString=f"""
            # CREATE EXTERNAL TABLE IF NOT EXISTS nba_analytics.team_stats (
            #     team STRING,
            #     wins INT,
            #     losses INT,
            #     win_percentage DOUBLE
            # )
            # ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
            # LOCATION 's3://sports-data-lake/raw-data/team_stats/'
            # """,
            # QueryExecutionContext={"Database": "nba_analytics"},
            # ResultConfiguration={"OutputLocation": self.athena_output_location},
            # )
            # time.sleep(5)  # Wait for the query to complete

            print("Athena output location and tables configured successfully.")
        except Exception as e:
            print(f"Error configuring Athena: {e}")

      

def main():
    print("Setting up data lake for NBA sports analytics...")
    data_lake = DataLake()
    data_lake.create_s3_bucket()
    time.sleep(5) # Wait for bucket creation
    data_lake.create_glue_database()
    data = data_lake.fetch_nba_data()
    if data:
        data_lake.upload_data_to_s3(data)
   
    data_lake.create_glue_table()
    data_lake.configure_athena()
    print("Data lake setup completed successfully.")

if __name__ == "__main__":
    main()