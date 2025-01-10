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
        self.iam = self.session.client("iam")

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
    def convert_to_line_delimited_json(self, data):
        """Convert data to line-delimited JSON format."""
        print("Converting data to line-delimited JSON format...")
        return "\n".join([json.dumps(record) for record in data])
    def upload_data_to_s3(self, data):
        """Upload NBA data to the S3 bucket."""
        try:
            line_delimited_data = self.convert_to_line_delimited_json(data)
            # Define S3 object key
            file_key = "raw-data/nba_player_data.json"
            
            # Upload JSON data to S3
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=line_delimited_data
            )
            print(f"Uploaded data to S3: {file_key}")
        except Exception as e:
            print(f"Error uploading data to S3: {e}")
    def create_glue_crawler(self):
        """Create a Glue crawler to catalog the NBA player data."""
        try:
            existing_crawlers = self.glue.list_crawlers()["CrawlerNames"]
            if "nba_player_data_crawler" in existing_crawlers:
                print("Glue crawler 'nba_player_data_crawler' already exists.")
                return
            crawler = self.glue.create_crawler(
                Name="nba_player_data_crawler",
                Role= "glue_service_role",
                DatabaseName=self.glue_database_name,
                TablePrefix="nba_",
                Targets={"S3Targets": [{"Path": f"s3://{self.bucket_name}/raw-data/"}]},
            )
            print("Glue crawler 'nba_player_data_crawler' created successfully.")
            print(f"crawler = {self.glue.get_crawler(Name='nba_player_data_crawler')}")
        except Exception as e:
            print(f"Error creating Glue crawler: {e}")
    def run_glue_crawler(self):
        """Run the Glue crawler to catalog the NBA player data."""
        try:
            self.glue.start_crawler(Name="nba_player_data_crawler")
            print("Glue crawler 'nba_player_data_crawler' started successfully.")
        except Exception as e:
            print(f"Error starting Glue crawler: {e}")
    def create_glue_role(self):
        """Create an IAM role for Glue to access specific S3 bucket and Athena resources with least privilege."""
        try:
            role_name = "glue_service_role"
            # Check if the role already exists
            try:
                self.iam.get_role(RoleName=role_name)
                print(f"IAM role {role_name} already exists.")
                return
            except self.iam.exceptions.NoSuchEntityException:
                print(f"Creating IAM role: {role_name}")

            # Define assume role policy document
            assume_role_policy_document = {
                
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "glue.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                
            }
            # Create the IAM role
            role = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
                Description="IAM role for AWS Glue service",
            )
            role_arn = role["Role"]["Arn"]
            print(f"Created IAM role: {role_arn}")

            # Define least privilege S3 access policy
            s3_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{self.bucket_name}",
                            f"arn:aws:s3:::{self.bucket_name}/*"
                        ]
                    }
                ]
            }

            # Define least privilege Athena access policy
            athena_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "athena:StartQueryExecution",
                            "athena:GetQueryExecution",
                            "athena:GetQueryResults",
                            "athena:ListDatabases",
                            "athena:ListTableMetadata"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            # log_policy
            logs_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": [
                            "arn:aws:logs:us-east-1:<accountId>:log-group:/aws-glue/crawlers*",
                            "arn:aws:logs:us-east-1:<accountId>:log-group:/aws-glue/jobs*"
                        ]
                    }
                ]
            }
            
            glue_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "glue:GetDatabase",
                            "glue:GetDatabases",
                            "glue:GetTable",
                            "glue:GetTables",
                            "glue:CreateTable",
                            "glue:UpdateTable"
                        ],
                        "Resource": [
                            "arn:aws:glue:us-east-1:<accountId>:catalog",
                            "arn:aws:glue:us-east-1:<accountId>:database/glue_nba_data_lake",
                            "arn:aws:glue:us-east-1:<accountId>:table/glue_nba_data_lake/*"
                        ]
                    }
                ]
            }
            self.iam.put_role_policy(
                RoleName="glue_service_role",
                PolicyName="GlueCatalogAccessPolicy",
                PolicyDocument=json.dumps(glue_policy)
            )
            
            
            self.iam.put_role_policy(
                RoleName="glue_service_role",
                PolicyName="GlueCloudWatchLogsPolicy",
                PolicyDocument=json.dumps(logs_policy)
            )
            # Attach the custom inline policies to the role
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName="GlueS3AccessPolicy",
                PolicyDocument=json.dumps(s3_policy),
            )
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName="GlueAthenaAccessPolicy",
                PolicyDocument=json.dumps(athena_policy),
            )
            print("Attached least privilege policies to IAM role.")

        except Exception as e:
            print(f"Error creating IAM role: {e}")
            raise

    # def create_glue_table(self):
    #     """Create a Glue table for the NBA player data."""
    #     try:
    #         response = self.glue.create_table(
    #             DatabaseName=self.glue_database_name,
    #             TableInput={
    #                 "Name": "nba_player_data",
    #                 "Description": "NBA player data table",
    #                 "StorageDescriptor": {
    #                     "Columns": [
    #                         {"Name": "player_id", "Type": "string"},
    #                         {"Name": "first_name", "Type": "string"},
    #                         {"Name": "last_name", "Type": "string"},
    #                         {"Name": "team", "Type": "string"},
    #                         {"Name": "position", "Type": "string"},
    #                         {"Name": "points_per_game", "Type": "double"},
    #                         {"Name": "assists_per_game", "Type": "double"},
    #                         {"Name": "rebounds_per_game", "Type": "double"},
    #                     ],
    #                     "Location": f"s3://{self.bucket_name}/raw-data/",
    #                     "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
    #                     "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",

    #                     "SerdeInfo": {
    #                         "SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe",
    #                     },
    #                 },
    #                 "TableType": "EXTERNAL_TABLE",
    #             },
    #         )
    #         print("Glue table 'nba_player_data' created successfully.")
    #     except Exception as e:
    #         print(f"Error creating Glue table: {e}")
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
    data_lake.create_glue_role()
    data_lake.create_glue_crawler()
    data_lake.run_glue_crawler()

    # data_lake.create_glue_table()
    # data_lake.configure_athena()
    # print("Data lake setup completed successfully.")

if __name__ == "__main__":
    main()