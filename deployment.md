# Deployment

  - create new RDS mysql db "cratr"
    - use aws secrets manager for credentials
    - create new vpc (or reuse safe one) 
    - password auth
    - initial database name: "cratr"

  - create new lambda function named "cratr"
    - set handler to "runner.lambda_handler", arch as needed
    - use server/deploy.sh to deploy
    - connect to rds db (or manually set to same vpc)
    - increase execution timeout, memory (can be temporary, max needed for cold start was 161s, 165mb)

  - edit vpc settings
    - add nat gateway for public internet access

  - create/validate a cert in acm for the domain

  - create api gateway endpoint
    - add integration for GET /meteorites -> cratr lambda 
    - add vpc link 
    - add custom domain api.cratr.rocks
      - add api mapping to api.cratr.rocks -> api with path "meteorites"
      - add CNAME to domain to point to new api gateway domain 

  - add s3 bucket for static hosting
    - enable static website hosting
    - use frontend/deploy.sh to deploy

  - add cloudfront distributions 
    - cratr.rocks -> s3 bucket
    - add CNAME to domain to point to distribution domain name
    - add s3:GetObject policy for cf to s3 bucket 

  - add eventbridge cron to trigger cratr lambda
    - payload event object {"action": "fetch"}