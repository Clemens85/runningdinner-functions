# GitHub Actions Deployment Setup

This guide explains how to set up automated deployments for the RunningDinner Functions project using GitHub Actions.

## Prerequisites

1. **GitHub OIDC Provider deployed** - (see Step 2)
2. **AWS Accounts** - Separate accounts for dev and prod (or same account with different stages)

## GitHub Configuration

### Step 1: Create GitHub Environments

Create two environments in your GitHub repository settings:

1. Go to **Settings** → **Environments** → **New environment**
2. Create `dev` environment:
   - No protection rules needed (auto-deploys on push to main)
   - Add environment variable: `AWS_ACCOUNT_ID` = your dev AWS account ID
3. Create `prod` environment:
   - **Enable** "Required reviewers" and add yourself
   - Add environment variable: `AWS_ACCOUNT_ID` = your prod AWS account ID

### Step 2: Update GitHub OIDC provider (One-time)

The GitHub role needs CDK deployment permissions. Those permissions are managed
by the `runningdinner-infrastructure` terraform repository in the `network` module.

## How Deployments Work

### Manual Deployments

- **Trigger**: Manual workflow dispatch
- **How to deploy**:
  1. Go to **Actions** → **Deploy Geocoding Stack** → **Run workflow**
  2. Select environment
  3. Click "Run workflow"

## CDK Bootstrap

Ensure CDK is bootstrapped in your AWS accounts:

```bash
# Dev account
cd infrastructure
export RUNNINGDINNER_FUNCTIONS_STAGE=dev
./bootstrap.sh dev

# Prod account (if different)
export RUNNINGDINNER_FUNCTIONS_STAGE=prod
./bootstrap.sh prod
```

## Permissions

The GitHub OIDC role has:

- **PowerUserAccess** - Full access to most AWS services
- **Limited IAM permissions** - Can create/manage Lambda execution roles with specific name patterns
- **SSM access** - Read Google Maps, OpenAI, and Pinecone API keys
- **DynamoDB access** - For geocoding cache operations
