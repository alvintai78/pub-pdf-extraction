# Cross-Architecture Deployment Guide
## From Apple Silicon (M1/M2/M3/M4) to Azure x86-64

This guide explains how to handle cross-architecture deployment from an ARM-based Mac to an x86-64 Azure environment.

## Understanding the Architecture Differences

- **Development Environment**: Apple Silicon M4 (ARM64 architecture)
- **Deployment Environment**: Azure (x86-64 architecture)

These architectures are different at the instruction set level, which can cause compatibility issues, particularly with:
- Binary dependencies and packages with native code
- System-specific optimizations
- Docker images built for a specific architecture

## Our Solution

We've implemented several measures to ensure smooth cross-architecture deployment:

1. **Platform-Specific Docker Builds**: Using `--platform=linux/amd64` flag
2. **Docker Buildx**: Leveraging multi-architecture build capabilities
3. **Dependency Management**: Ensuring all Python packages work across architectures

## Key Files Modified

1. **Dockerfile**: Added platform specification and necessary build tools
2. **deploy_to_azure.sh**: Updated to use Docker Buildx for cross-platform builds
3. **build_test_amd64.sh**: Added for local testing of AMD64 containers

## Prerequisites

Before deployment, ensure:

1. **Docker Desktop is Updated**: Latest version with buildx support
2. **Rosetta 2 is Installed**: For running x86-64 binaries on Apple Silicon
   ```
   softwareupdate --install-rosetta
   ```

## Testing Locally Before Deployment

Before deploying to Azure, test your container locally:

```bash
./build_test_amd64.sh
```

This will:
1. Build your container for AMD64 architecture
2. Run it locally using QEMU emulation
3. Make it available at http://localhost:8501

## Potential Issues and Solutions

### 1. Slow Builds

**Issue**: Building for AMD64 on ARM is slower due to emulation.  
**Solution**: Be patient during builds; they will take longer than native builds.

### 2. Package Compatibility

**Issue**: Some Python packages might have ARM-specific optimizations.  
**Solution**: Our Dockerfile installs build tools to compile packages as needed.

### 3. Performance Differences

**Issue**: Some operations might perform differently between architectures.  
**Solution**: Test thoroughly on both platforms; what works well on your Mac might perform differently on Azure.

## Monitoring After Deployment

After deploying to Azure Container Apps, monitor:

1. **Cold Start Times**: May be longer for cross-architecture builds
2. **Memory Usage**: May differ between architectures
3. **CPU Usage**: Efficiency patterns may vary

## Additional Resources

- [Docker Multi-Platform Guide](https://docs.docker.com/build/building/multi-platform/)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
