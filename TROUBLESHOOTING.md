# Troubleshooting Azure Container Apps Deployment

This guide addresses common issues when deploying the PDF Extraction app to Azure Container Apps.

## Prerequisites Check

Before running the deployment script, ensure:

1. **Docker Desktop is running**
   - Open Docker Desktop application
   - Verify status in menu bar (macOS) or system tray (Windows)
   - Run `docker info` to confirm connection

2. **Azure CLI is installed and updated**
   - Run `az --version` to check
   - Update if needed: `brew upgrade azure-cli` (macOS) or `az upgrade` (Windows)

3. **You're logged into Azure**
   - Run `az login` and follow the browser authentication
   - Verify with `az account show`

4. **You have required permissions**
   - Contributor or Owner role on the subscription
   - Ability to create resource groups and services

## Common Issues and Solutions

### 1. Docker Login Issues

**Error**: `flag needs an argument: 'p' in -p` or other login issues

**Solutions**:
- Use stdin for password: `echo $PASSWORD | docker login --username $USERNAME --password-stdin`
- Try manual login: `docker login yourregistry.azurecr.io` and enter credentials when prompted
- Check ACR credentials: `az acr credential show --name yourregistry`

### 2. Docker Daemon Connection Issues

**Error**: `Cannot connect to the Docker daemon`

**Solutions**:
- Start Docker Desktop
- Check Docker service: `systemctl status docker` (Linux)
- Verify Docker socket: `ls -la /var/run/docker.sock`
- Restart Docker: `sudo service docker restart` (Linux) or restart Docker Desktop

### 3. ACR Authorization Issues

**Error**: `UNAUTHORIZED: authentication required` or similar

**Solutions**:
- Ensure admin account is enabled: `az acr update --name yourregistry --admin-enabled true`
- Verify credentials: `az acr credential show --name yourregistry`
- Check if you can manually push: `docker push yourregistry.azurecr.io/yourimage:tag`
- Check network connectivity to ACR
- Assign appropriate roles: `az role assignment create --assignee <principal-id> --scope <acr-resource-id> --role AcrPush`

### 4. Container App Creation Issues

**Error**: `Failed to provision revision for container app`

**Solutions**:
- Verify image exists in ACR: `az acr repository show --name yourregistry --repository yourimage`
- Ensure image is properly tagged and pushed
- Check if Container Apps can access ACR
- Create a managed identity and grant it access to ACR
- Try deploying from Azure Portal as a test

### 5. Multi-Architecture Build Issues

**Error**: Issues with buildx or platform-specific builds

**Solutions**:
- Install QEMU: `docker run --privileged --rm tonistiigi/binfmt --install all`
- Use standard Docker build as fallback: `docker build -t yourimage .`
- Ensure Docker Desktop experimental features are enabled

## Checking Deployment Status

If the script fails, check the status manually:

```bash
# List container apps
az containerapp list --resource-group your-resource-group --output table

# Check specific container app logs
az containerapp logs show --name your-app-name --resource-group your-resource-group

# Check container app revision status
az containerapp revision list --name your-app-name --resource-group your-resource-group
```

## Manual Deployment Steps

If the script fails completely, you can deploy manually:

1. Build and push your Docker image:
   ```bash
   docker build -t yourregistry.azurecr.io/yourimage:tag .
   docker push yourregistry.azurecr.io/yourimage:tag
   ```

2. Create a Container App Environment:
   ```bash
   az containerapp env create --name your-env --resource-group your-rg --location your-location
   ```

3. Create the Container App:
   ```bash
   az containerapp create \
     --name your-app \
     --resource-group your-rg \
     --environment your-env \
     --image yourregistry.azurecr.io/yourimage:tag \
     --registry-server yourregistry.azurecr.io \
     --registry-username username \
     --registry-password password \
     --target-port 8501 \
     --ingress external
   ```

## Still Having Issues?

1. Check the Azure Container Apps service status
2. Review your Azure subscription quotas and limits
3. Look at Azure Container Apps documentation for updates or known issues
4. Try deploying a simple test container to isolate the issue
