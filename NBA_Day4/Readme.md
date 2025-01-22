# Sports Data API Management System

## Project Overview
In this project, a containerized API management system was configured for querying sports data. The system leverages the following AWS services:

- **Amazon ECS (Fargate)** for running containerized applications.
- **Amazon ECR** for storing Docker images.
- **Application Load Balancer (ALB)** for distributing traffic.
- **IAM Users with Custom Policies** for secure access management.
- **Amazon API Gateway** for securing and managing API endpoints.

A Python API was developed using **FastAPI**, utilizing object-oriented programming (OOP) principles to ensure secure and standardized code. FastAPI’s rapid development capabilities and its auto-generated Swagger documentation at the `/docs` endpoint made it easier to test and validate the application.

---

## Features

1. **Containerized Deployment:**
   - Utilized ECS Fargate to deploy and run the API in a serverless environment.
   - Images stored and managed with ECR.

2. **Secure Access:**
   - API Gateway was employed to secure access to the endpoint.
   - Custom IAM policies ensured the least privilege principle for managing resources.

3. **Development Framework:**
   - Built the API with FastAPI for efficient development.
   - Leveraged OOP principles for robust and maintainable code.
   - Swagger documentation for quick testing and debugging.

---

## Challenges Faced

### 1. Configuring IAM User with Granular Permissions
Creating an IAM user with just the necessary permissions required detailed troubleshooting to identify the required actions. Below is the custom policy used to achieve this:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ecr:BatchGetImage",
                "ecr:CompleteLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:InitiateLayerUpload",
                "ecr:BatchCheckLayerAvailability",
                "ecr:PutImage"
            ],
            "Resource": "arn:aws:ecr:<region>:<ID>:repository/sports-api"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "ecr:GetAuthorizationToken",
            "Resource": "*"
        }
    ]
}
```

Additionally, while creating the custom policy, I initially attempted to add `ecr:GetAuthorizationToken` permission to a single resource. This was a mistake because the `ecr:GetAuthorizationToken` action only works with `"*"` (i.e., all ECR resources) and not on individual resources. Identifying and correcting this oversight was an important learning experience.

### 2. Execution Errors During Service Start
The initial attempts to run the service resulted in the following error:

```
exec /usr/local/bin/uvicorn: exec format error
```

#### Cause:
This error occurred because of a mismatch between the architecture type used to build the Docker image and the architecture type selected for running the image.

#### Solution:
While creating the ECS task definition, the architecture type was changed from the default `Linux x86` to `arm64`, resolving the issue.

---

## FastAPI Features
- **Rapid Development:** FastAPI allowed for quick development and deployment of the API.
- **Auto-Generated Documentation:** Swagger documentation available at `/docs` helped streamline API testing and validation.

---

## Conclusion
This project demonstrates the integration of AWS services with a modern Python framework to create a scalable, secure, and efficient API system. The challenges faced during implementation provided valuable insights into configuring custom IAM policies and resolving architecture-related issues in containerized environments.

---

## Acknowledgments
- **FastAPI Documentation:** For quick references and tutorials.
- **AWS Documentation:** For detailed explanations of ECS, ECR, and IAM.
- **Community Forums:** For debugging assistance with architecture-related issues.
- **For Deatiled steps:** [REXTECH friends youtube channel ](https://www.youtube.com/watch?v=sF9_YzOrmTs&ab_channel=REXTECHfriends)