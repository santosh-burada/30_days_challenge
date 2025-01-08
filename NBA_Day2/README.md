# 30 Days of Cozy Cloud Crew DevOps Challenge: Automating NBA Game Notifications with AWS

## Day 2: NBA Game Notifications System

This project involves automating NBA game notifications using AWS services like Lambda, SNS, and EventBridge Scheduler. The system fetches game data from SportsData.io and sends notifications to subscribed users.

### Overview

- **Goal**: Build a serverless system to fetch and notify NBA game updates.
- **Key AWS Services**:
  - AWS Lambda: Fetch and process game data.
  - Amazon SNS: Distribute notifications.
  - Amazon EventBridge Scheduler: Automate Lambda execution.

### Architecture

1. **AWS Lambda Function**
   - **Purpose**: Fetch NBA game data and send it to an SNS topic.
   - **Implementation**:
     - Written in Python using the `requests` library.
     - Retrieves API key and SNS topic ARN from environment variables.
     - Adjusts for Central Time (UTC-6) to fetch the correct game data.
     - Formats and publishes game data to the SNS topic.

2. **Amazon SNS**
   - **Purpose**: Send notifications about NBA games.
   - **Setup**:
     - Create an SNS topic (e.g., `NBA_topic`).
     - Add subscriptions (e.g., email, SMS) to deliver notifications.

3. **Amazon EventBridge Scheduler**
   - **Purpose**: Schedule Lambda function execution.
   - **Setup**:
     - Create a rule with a cron expression to trigger the Lambda function at specific intervals.

### Data Flow
1. EventBridge Scheduler triggers the Lambda function.
2. Lambda fetches NBA game data from SportsData.io.
3. Processed data is sent to the SNS topic.
4. SNS delivers notifications to subscribed endpoints.

### Security and Permissions
- **IAM Roles**:
  - Lambda requires permissions to access the API and publish to SNS.
  - Attach `AWSLambdaBasicExecutionRole` and a custom SNS publish policy.
- **Environment Variables**:
  - Store API key and SNS topic ARN securely.

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/santosh-burada/30_days_challenge
   cd NBA_Day2
   ```

2. **Create an SNS Topic**:
   - Go to the SNS service in AWS.
   - Create a topic named `NBA_topic`.
   - Note the ARN.

3. **Add Subscriptions**:
   - Add email or SMS subscriptions to the topic.
   - Confirm the subscription via the provided email or phone.

4. **Create an IAM Role**:
   - Create a role for Lambda with the following policies:
     - SNS Publish Policy.
     - AWSLambdaBasicExecutionRole.

5. **Deploy the Lambda Function**:
   - Create a new Lambda function with Python runtime.
   - Assign the IAM role.
   - Upload the code and configure environment variables for the API key and SNS topic ARN.

6. **Set Up EventBridge Scheduler**:
   - Create a rule to trigger the Lambda function at desired intervals.

7. **Test the System**:
   - Run a test event in the Lambda console.
   - Verify notifications are received.

### Problems Faced
- **Missing Dependencies**: AWS Lambda runtime lacked the `requests` module.
  - **Solution**: Use Lambda layers or package dependencies in a `.zip` file. [AWS Documentation](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)

### Lessons Learned
- Automating workflows with EventBridge.
- Designing secure, least-privilege IAM policies.
- Integrating external APIs into AWS workflows.
### For more info: [Medium Blog](https://medium.com/@santu.burada99/30-days-of-cozy-cloud-crew-devops-challenge-automating-nba-game-notifications-with-aws-01bc49a5d42f)

### Conclusion
This project highlights how to automate NBA game notifications using AWS services, creating a scalable and cost-effective system. The setup can be further enhanced with features like team-based filtering or alternative notification channels.

###
---
Thanks to Cozy Cloud Crew!

