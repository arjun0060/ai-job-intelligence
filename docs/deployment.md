# Deployment Guide

## Production architecture

Production uses:

- AWS EC2
- AWS RDS PostgreSQL
- AWS S3
- AWS VPC
- AWS IAM
- AWS Systems Manager
- Elastic IP
- Docker
- Docker Compose
- Terraform
- GitHub Actions

The architecture is intentionally cost-conscious and does not require an ALB or NAT Gateway for the current deployment.

## Containers

Production runs two containers:

```text
frontend
  └── Nginx + React static build

backend
  └── FastAPI + Python
```

The frontend publishes port 80.

The backend exposes port 8000 only to the Docker network:

```text
Browser
  ↓
Nginx :80
  ↓
backend:8000
```

## Docker build

The backend image uses Python 3.11 and installs the required dependencies.

The frontend uses a multi-stage build:

```text
Node build stage
      ↓
React production build
      ↓
Nginx runtime image
```

## Production Compose

The production Compose file starts:

```bash
docker compose -f docker-compose.prod.yml up -d
```

The backend uses the production environment file and is not directly published to the host.

## Terraform

Infrastructure is maintained under:

```text
terraform/
```

Terraform manages the AWS resources required by the application, including networking, EC2, RDS, security groups, IAM, S3, and the Elastic IP.

Typical workflow:

```bash
terraform init
terraform plan
terraform apply
```

Infrastructure changes should be reviewed with `terraform plan` before applying them.

## EC2 deployment script

The server deployment script is:

```text
scripts/deploy.sh
```

The script:

1. changes to the application directory
2. fetches the latest `main`
3. resets to `origin/main`
4. builds the backend image
5. builds the frontend image
6. starts Docker Compose
7. removes unused Docker images
8. checks container status

The script uses Git's explicit safe-directory configuration because the deployment command is executed through AWS Systems Manager.

## GitHub Actions

The deployment flow is:

```text
Push to main
    ↓
GitHub Actions
    ↓
AWS OIDC authentication
    ↓
IAM role
    ↓
SSM SendCommand
    ↓
EC2
    ↓
deploy.sh
```

The GitHub Actions workflow does not require storing a long-lived AWS access key in GitHub secrets.

OIDC allows GitHub Actions to assume the dedicated AWS IAM role.

## AWS Systems Manager

EC2 is managed through AWS Systems Manager.

This allows GitHub Actions to send the deployment command without requiring the CI runner to open an SSH connection to the server.

The EC2 instance uses the required Systems Manager IAM permissions.

## Database

PostgreSQL runs on AWS RDS.

The database is in a private subnet and its security group allows PostgreSQL traffic from the application security group.

The application uses the RDS endpoint through the VPC network.

The pgvector extension is installed for vector similarity search.

## Security model

Important security boundaries include:

- RDS is not publicly exposed.
- Backend port 8000 is not published to the internet.
- Database access is restricted by security group rules.
- AWS deployment uses IAM and OIDC.
- Application secrets are provided through environment configuration.
- Real secrets must never be committed to Git.

## Environment configuration

Create a local environment file based on:

```text
.env.example
```

Required values depend on the application configuration and include database credentials and AI/API configuration.

Never commit:

```text
.env
```

or real API keys/passwords.

## Operational checks

After deployment:

```bash
docker compose -f docker-compose.prod.yml ps
```

Check backend logs:

```bash
docker logs ai-job-intelligence-backend
```

Check frontend logs:

```bash
docker logs ai-job-intelligence-frontend
```

The application should then be tested through the public HTTP endpoint.

## Rollback

Because deployment resets the EC2 working tree to the latest `origin/main`, rollback should be performed by deploying a known-good Git commit or reverting the problematic commit and triggering the normal deployment workflow.

For production incidents:

1. identify the failing deployment/commit
2. inspect container logs
3. revert or deploy a known-good revision
4. trigger the GitHub Actions workflow
5. verify containers and API health
6. confirm frontend functionality

## Cost-conscious design

The current deployment deliberately avoids unnecessary infrastructure components.

The application runs on a single EC2 host with Docker Compose while PostgreSQL is provided by RDS.

This keeps the architecture understandable for a portfolio/interview project while still demonstrating:

- cloud infrastructure
- infrastructure as code
- containerization
- CI/CD
- IAM
- secure database networking
- automated deployment
