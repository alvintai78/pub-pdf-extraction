# Troubleshooting ACR Authentication Issues

This guide helps you resolve authentication issues when pushing Docker images to Azure Container Registry (ACR).

## Common ACR Authentication Errors

### Error 1: Failed to authorize / 401 Unauthorized

```
failed to authorize: failed to fetch anonymous token: unexpected status from GET request to https://yourregistry.azurecr.io/oauth2/token: 401 Unauthorized
```

This error occurs when:
- Docker is not logged into ACR
- Login credentials have expired
- Admin account is not enabled on ACR
- User doesn't have proper permissions to the ACR

### Error 2: Unknown or invalid registry

```
Error response from daemon: pull access denied for yourregistry.azurecr.io/yourimage, repository does not exist or may require 'docker login'
```

This error occurs when:
- ACR URL is incorrect
- Repository doesn't exist
- Not authenticated to the registry

## Solution Steps

### Step 1: Verify Azure CLI is logged in

```bash
az login
```

### Step 2: Enable ACR Admin Account

```bash
az acr update --name yourregistry --admin-enabled true
```

### Step 3: Get Fresh ACR Credentials

```bash
ACR_USERNAME=$(az acr credential show --name yourregistry --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name yourregistry --query passwords[0].value -o tsv)
```

### Step 4: Force Re-login to ACR

```bash
# Log out first (if already logged in)
docker logout yourregistry.azurecr.io

# Log in with fresh credentials
echo $ACR_PASSWORD | docker login yourregistry.azurecr.io --username $ACR_USERNAME --password-stdin
```

### Step 5: Alternative Authentication Method

If the above doesn't work, try authenticating with az acr login:

```bash
az acr login --name yourregistry
```

### Step 6: Check IAM Permissions

Ensure your user has the AcrPush role:

```bash
# Get ACR resource ID
ACR_ID=$(az acr show --name yourregistry --query id -o tsv)

# Get your user ID
USER_ID=$(az ad signed-in-user show --query id -o tsv)

# Assign AcrPush role
az role assignment create --assignee $USER_ID --scope $ACR_ID --role AcrPush
```

## Using the fix_acr_auth.sh Script

We've provided a script that automates these steps:

```bash
./fix_acr_auth.sh
```

This script will:
1. Check if Docker is running
2. Verify Azure login
3. Enable admin on the ACR
4. Get fresh credentials
5. Force a re-login
6. Try alternative authentication if needed
7. Build and push your image

## After Successful Push

Once you've successfully pushed your image to ACR, run:

```bash
./continue_deployment.sh
```

This script will create the Container App Environment and deploy your application.

## Additional Troubleshooting

If you're still having issues:

1. **Check Network Connectivity**: Ensure your network allows connections to Azure
2. **Docker Daemon Status**: Restart Docker if necessary
3. **Check ACR Status**: Verify the ACR service is running in Azure
4. **Clear Docker Cache**: Try `docker system prune` to clear cached credentials
5. **Check Image Name**: Ensure the image name and tag are correct
