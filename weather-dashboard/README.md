# Weather Data Collection System

## Overview
The Weather Data Collection System demonstrates core DevOps concepts by integrating the following technologies and practices:

- **External API**: OpenWeather API
- **Cloud Storage**: AWS S3
- **Infrastructure as Code**
- **Version Control**: Git
- **Python Development**
- **Error Handling**
- **Environment Management**

## Key Features
1. **Real-time weather data fetching** for multiple cities
2. Display of **temperature (°F)**, **humidity**, and **weather conditions**
3. **Automatic storage** of weather data in AWS S3
4. Support for **tracking multiple cities**
5. **Timestamped data** for historical tracking

## Technical Architecture
- **Language**: Python 3.x
- **Cloud Provider**: AWS (S3)
- **External API**: OpenWeather API
- **Dependencies**:
  - `boto3` (AWS SDK)
  - `python-dotenv`
  - `requests`

---

## Project Structure
```
weather-dashboard/
|-- src/
|   |-- weather_dashboard.py
|-- .env
|-- requirements.txt
|-- README.md
```

---

## Setup Instructions

### 1. Clone Repository:
```
git clone https://github.com/santosh-burada/30_days_challenge/tree/main/weather-dashboard
```

### 2. Install Dependencies:
```
pip install -r requirements.txt
```

### 3. Configure Environment Variables:
Create a `.env` file in the root directory and add the following:
```
WEATHER_APIKEY = your_weather-api
WEATHER_BUCKET_NAME = AWS_bucket_name
AWS_ACCESS_KEY_ID = AWS_IAM_USER_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = AWS_IAM_USER_SECRET_KEY
AWS_REGION = region (e.g., us-east-1)
```

### 4. Run the Script:
```
python src/weather_dashboard.py
```

---

## Problems Faced

**Error:**
```
An error occurred (AccessDenied) when calling the CreateBucket operation: User: <USER ARN> is not authorized to perform: s3:CreateBucket on resource: “arn:aws:s3:::weather-dashboard1” with an explicit deny in an identity-based policy
```

### Root Cause:
This error occurs when an IAM user’s `access_key` and `secret_key` are publicly exposed on the internet. AWS automatically assigns `CompromisedKeyQuarantine` and `CompromisedKeyQuarantineV2` managed policies to the compromised user, effectively blocking access, even for users with full administrative privileges.

### Solution:
- Delete the compromised IAM user.
- Create a new IAM user and generate fresh access keys.

---

## What I Learned
This project provided valuable hands-on experience in:

1. Creating and managing **AWS S3 buckets**
2. Implementing secure **API key management** using environment variables
3. Applying **Python best practices** for API integration
4. Utilizing **Git workflow** for project development
5. Implementing **error handling** in distributed systems
6. Gaining practical knowledge in **cloud resource management**

---

## Future Enhancements

- **Data visualization**: Generate charts and graphs for weather trends.
- **Expand tracked cities**: Support for a larger list of cities.
- **Automated testing suite**: Implement unit and integration tests.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Author
Santosh Burada