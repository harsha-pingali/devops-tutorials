# Multi-Stage Docker Builds

## Overview

Multi-stage Docker builds are an advanced Docker feature that allows you to use multiple FROM statements in a single Dockerfile. Each stage can be based on a different base image and only the final stage is used to create the production image. This technique significantly reduces final image size by excluding build dependencies from the production image.

```
    We can have 'N' number of stages
```

## Setup

### Prerequisites
- Docker installed and running
- Go 1.21 or later (for this tutorial)
- Basic understanding of Dockerfile syntax
- Familiarity with Docker image building basics

### Project Structure
```
multi-stage-builds/
├── Dockerfile          # Multi-stage build configuration
├── timer.go           # Go application source code
└── go.mod             # Go module definition
```

### Building the Image

To build the multi-stage Docker image:

```bash
docker build -t timer:latest .
```

To run the container:

```bash
docker run timer:latest
```

## Concepts

### What is a Multi-Stage Build?

A multi-stage build uses multiple FROM statements to create separate build stages. Each stage can:
- Use a different base image
- Build artifacts independently
- Be named for reference
- Copy artifacts from previous stages

### What are Distroless Images?

Distroless images are minimal container images that contain only the application and its runtime dependencies. They exclude:
- Package managers (apt, yum, apk)
- Shell interpreters (bash, sh)
- System utilities and tools
- Development headers and libraries

Google maintains a set of distroless images at `gcr.io/distroless/` for common languages and frameworks.

### Why Use Multi-Stage Builds?

1. **Reduced Image Size**: Build tools and dependencies are not included in the final image
2. **Security**: Removes unnecessary binaries and source code from production images
3. **Maintainability**: Separates build concerns from runtime concerns
4. **Performance**: Smaller images pull faster and require less storage

### Why Use Distroless Images?

Distroless images provide additional security and size benefits:

1. **Minimal Attack Surface**: No shell means attackers cannot execute commands in the container
2. **Extremely Small Size**: Distroless images are only a few MB vs 5-100+ MB for other base images
3. **Faster Deployment**: Smaller images pull and start faster
4. **Non-Interactive**: Perfect for containerized applications that don't need user interaction
5. **Compliance**: Helps meet security and compliance requirements
6. **Supply Chain Security**: Fewer dependencies mean fewer potential vulnerabilities

### How It Works

**Stage 1 (Builder Stage):**
- Uses a full development environment image
- Installs build tools (Go compiler, dependencies)
- Compiles the application source code
- Creates the executable binary

**Stage 2 (Final Stage - Distroless):**
- Uses a minimal distroless base image
- Copies only the compiled binary from Stage 1
- Runs the application without shell or utilities

### Benefits Compared to Single-Stage Builds

| Aspect | Single-Stage | Multi-Stage | Multi-Stage + Distroless |
|--------|-------------|------------|--------------------------|
| Image Size | Large (includes build tools) | Small (only runtime deps) | Minimal (only app binary) |
| Security | Large attack surface | Reduced attack surface | Minimal attack surface |
| Shell Access | Yes (bash/sh) | Yes (alpine) | No (non-interactive) |
| Build Time | Faster initial build | Slightly longer | Slightly longer |
| Maintenance | Simpler structure | More organized | Most secure/efficient |
| Security Scanning | More CVEs | Fewer CVEs | Minimal CVEs |
| Package Manager | Yes | Yes (apk) | No |

### Distroless vs Scratch vs Alpine

| Criteria | Alpine | Distroless | Scratch |
|----------|--------|-----------|---------|
| **Base Size** | ~5 MB | ~2-20 MB | 0 KB |
| **Package Manager** | Yes (apk) | No | No |
| **Shell** | Yes (sh) | No | No |
| **libc** | musl | glibc/other | No |
| **Debug Tools** | Basic | None | None |
| **Use Case** | Development | Production | Static binaries only |
| **Runtime Support** | Full Linux | Core only | Very limited |
| **Debuggability** | Moderate | Low | Very low |
| **Dynamic Linking** | Yes | Yes | No (static only) |

### Why Use Distroless Over Alpine?

Alpine is commonly used but has limitations:
- Still contains a shell (potential attack vector)
- Contains package manager (increased CVEs)
- Uses musl libc (different from standard glibc)
- May require building for different libc version
- Some applications expect glibc

Distroless addresses these with:
- No shell executable
- No package manager
- Uses standard glibc (when needed)
- Smaller size than Alpine for production
- Better compliance alignment

## Commands and Detailed Explanation

### Bad Example: Single-Stage Build (Dockerfile.bad)

This is the traditional approach without multi-stage optimization:

```dockerfile
FROM ubuntu:latest

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends golang

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o timer .

ENTRYPOINT [ "/app/timer" ]
```

**Problems with this approach:**
- **Large Image Size**: Contains the entire Go compiler, build tools, and Ubuntu base (~800+ MB)
- **Security Risk**: Unnecessary binaries and tools exposed in production
- **Wasted Resources**: Build dependencies shipped with production image
- **Slow Deployment**: Large images take longer to pull and deploy

**Building and checking size:**
```bash
docker build -f Dockerfile.bad -t timer:bad .
docker images timer:v1.0
# Result: ~638.67 MB 
```
![alt text](image.png)

### Good Example: Multi-Stage Build (Dockerfile)

This is the optimized approach using multi-stage builds:

```dockerfile
FROM golang:1.21-alpine as builder

WORKDIR /app

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o timer .

FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/timer .

ENTRYPOINT [ "/app/timer" ]
```

**Advantages of this approach:**
- **Minimal Image Size**: Only runtime dependencies (~5-10 MB with Alpine)
- **Security**: Only the compiled binary in production image
- **Fast Deployment**: Small images pull and deploy quickly
- **Clean Separation**: Build concerns separated from runtime concerns

**Building and checking size:**
```bash
docker build -f Dockerfile -t timer:good .
docker images timer:good
# Result: ~5-10 MB (dramatically smaller)
```

### Comparison Table

| Aspect | Single-Stage (Bad) | Multi-Stage (Good) | Multi-Stage + Distroless |
|--------|-------------------|-------------------|--------------------------|
| Image Size | 638.67 MB | ~5-10 MB | ~3.81 MB |
| Base Image | ubuntu:latest | alpine:latest | gcr.io/distroless/base-debian11 |
| Build Tools | Included in final image | Only in builder stage | Only in builder stage |
| Security | Large attack surface | Reduced attack surface | Minimal attack surface |
| Deployment Time | Slow (large download) | Fast (small download) | Fastest (smallest download) |
| Storage Space | High | Low | Minimal |
| Shell Access | Yes | Yes | No |
| Package Manager | Yes | Yes | No |
| Runtime Speed | Same | Same | Same |
| Build Time | ~1-2 min | ~1-2 min | ~1-2 min |

### Best Example: Multi-Stage Build with Distroless (Dockerfile)

This is the production-ready approach using multi-stage builds with distroless:

```dockerfile
########################################
### Building a multi-stage image with distroless base image
#############################################
# STAGE 1: Builder
FROM golang:1.21-alpine as builder

WORKDIR /app

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o timer .

# STAGE 2: Runtime with Distroless
FROM gcr.io/distroless/base-debian11

WORKDIR /app

# Copy the compiled binary from the builder stage
COPY --from=builder /app/timer /app

ENTRYPOINT [ "/app" ]
```

**Advantages of distroless approach:**
- **Extremely Small Size**: Only ~3.81 MB (as shown in your build)
- **Zero Shell**: No shell interpreter means non-interactive and more secure
- **No Package Manager**: Eliminates package manager attack vector
- **Production-Ready**: Optimized specifically for production workloads
- **Compliance Ready**: Helps meet SOC2, PCI-DSS, and other security standards
- **Faster Deployment**: Quickest image pull and startup times
- **Fewer CVEs**: Minimal dependencies mean minimal vulnerabilities

**Building and checking size:**
```bash
docker build -f Dockerfile -t timer:distroless .
docker images timer
# Result: ~3.81 MB (3x smaller than Alpine!)
```
![alt text](image-1.png)

### Scratch Image - The Absolute Minimum (Dockerfile.scratch)

For static binaries, you can use `scratch` (empty image):

```dockerfile
########################################
### Building with scratch - the minimal distroless image
#############################################
# STAGE 1: Builder
FROM ubuntu:latest as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y golang

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o timer .

# STAGE 2: Scratch (empty image)
FROM scratch

COPY --from=builder /app/timer /app

ENTRYPOINT [ "/app" ]
```

**Characteristics of scratch:**
- **0 MB Base Size**: No filesystem, just the binary
- **Static Binary Only**: Application must be compiled statically
- **No Runtime Support**: No libc, no system libraries
- **Extreme Minimalism**: Only what your binary needs
- **Best for**: Static Go binaries, static C binaries, other statically compiled programs

**Limitations of scratch:**
- Cannot execute shell commands or utilities
- No debugging capabilities
- Static linking required
- Limited to applications that don't need system libraries

## Distroless Images: Comprehensive Advantages

### Security Advantages

**1. Reduced Attack Surface**
- No shell interpreter (bash, sh) - prevents shell-based attacks
- No package manager - eliminates package manager exploits
- Fewer binaries - fewer potential vulnerabilities
- Non-interactive nature prevents user-facing exploits

**2. Supply Chain Security**
- Minimal dependencies reduce dependency vulnerabilities
- Fewer components to audit and approve
- Easier to verify image integrity
- Reduced risk of transitive dependency attacks

**3. Runtime Security**
- Process cannot fork new shells
- Limited system calls available
- Cannot install additional tools at runtime
- Reduces lateral movement risks in compromised containers

### Performance Advantages

**1. Image Size**
```
Single-Stage (Ubuntu):     638.67 MB
Multi-Stage (Alpine):      ~5-10 MB
Distroless:                ~3.81 MB
Scratch:                   <1 MB (binary only)
```

**2. Deployment Speed**
- Faster image pulls from registry
- Faster container startup time
- Lower bandwidth usage across clusters
- Faster auto-scaling and rollouts

**3. Storage Efficiency**
- Reduced storage costs in registries
- Smaller node disk space requirements
- More images per node for Kubernetes clusters
- Cost savings in large deployments

### Operational Advantages

**1. Compliance**
- Meets SOC2 requirements (minimal OS components)
- Aligns with PCI-DSS standards
- Supports NIST cybersecurity frameworks
- Easier security certifications

**2. Maintenance**
- No OS patches to apply to base image
- No package manager updates needed
- Simpler dependency management
- Focus on application vulnerabilities only

**3. Container Management**
- Consistent behavior across environments
- No shell differences between systems
- Predictable resource consumption
- Better suited for serverless/Knative

### Cost Advantages

**1. Infrastructure Costs**
- Reduced storage in container registries ($500-5000/year savings at scale)
- Lower bandwidth costs
- Reduced node storage requirements
- Better bin packing on Kubernetes

**2. Operational Costs**
- Less time spent on security scanning
- Fewer vulnerabilities to patch
- Reduced incident response time
- Lower compliance audit costs

### Disadvantages and Trade-offs

**When NOT to use Distroless:**

1. **Development/Debugging**
   - Cannot exec into container
   - Cannot install debugging tools
   - Limited troubleshooting capabilities
   - Use Alpine or Ubuntu for dev images instead

2. **Complex Applications**
   - Applications requiring system utilities
   - Scripts that need interpreters
   - Applications expecting system tools
   - Dynamic linking to unusual libraries

3. **Legacy Applications**
   - Applications compiled against specific libc versions
   - Java applications with specific requirements
   - Applications with complex runtime dependencies

**Solutions for Complex Cases:**

```dockerfile
# Use distroless base with custom tooling
FROM golang:1.21-alpine as builder

WORKDIR /app
COPY . .
RUN go build -o myapp .

FROM distroless/base-debian11 as runtime

# Add debugging tools if needed
COPY --from=builder /bin/sh /bin/sh
COPY --from=builder /app/myapp /app/myapp

ENTRYPOINT ["/app/myapp"]
```

### Distroless Image Variants

Google provides different distroless base images:

```
gcr.io/distroless/base              # Debian-based with glibc
gcr.io/distroless/base-debian11     # Specific Debian version
gcr.io/distroless/python3           # For Python applications
gcr.io/distroless/nodejs            # For Node.js applications
gcr.io/distroless/java              # For Java applications
gcr.io/distroless/cc                # For C/C++ applications
gcr.io/distroless/static            # Static binaries only
```

### Real-World Savings Example

**Scenario**: Enterprise with 100 microservices deployed across 10 Kubernetes clusters

**Single-Stage (Ubuntu) Approach:**
- Average image size: 500 MB per service
- Total images: 500 MB × 100 × 3 versions = 150 GB
- Registry storage cost: $150/month
- Bandwidth for 1000 deployments/day: ~50 GB = $500/day
- Annual cost: ~$180K

**Distroless Approach:**
- Average image size: 5 MB per service
- Total images: 5 MB × 100 × 3 versions = 1.5 GB
- Registry storage cost: $1.50/month
- Bandwidth for 1000 deployments/day: ~500 MB = $5/day
- Annual cost: ~$2K

**Savings: ~$178K/year + Security improvements**

## Best Practices

### General Multi-Stage Build Practices

1. **Name Your Stages**: Use descriptive names with `as` keyword for clarity
   ```dockerfile
   FROM golang:1.21 as builder
   FROM distroless/base as runtime
   ```

2. **Use Lightweight Base Images**: For final stage, follow this hierarchy:
   ```dockerfile
   # Best (smallest, most secure)
   FROM scratch                              # 0 MB - static binaries only
   
   # Very Good (3-20 MB, production-ready)
   FROM gcr.io/distroless/base              # ~2-5 MB
   
   # Good (5-10 MB, has shell)
   FROM alpine:latest                        # ~5 MB
   
   # Acceptable (larger)
   FROM ubuntu:22.04                         # ~70 MB
   
   # Avoid (bloated)
   FROM ubuntu:latest                        # ~77+ MB
   ```

3. **Minimize Layer Count**: Combine RUN commands where logical
   ```dockerfile
   RUN apt-get update && \
       apt-get install -y package1 package2 && \
       apt-get clean
   ```

4. **Order Dockerfile Commands**: Place frequently changing commands later to leverage caching

5. **Use Specific Versions**: Avoid `latest` tags for reproducibility
   ```dockerfile
   FROM golang:1.21-alpine
   FROM gcr.io/distroless/base-debian11
   FROM ubuntu:22.04
   ```

6. **Build Only Needed Artifacts**: In build stage, exclude unnecessary files
   ```dockerfile
   COPY . .
   RUN rm -rf tests docs vendor
   ```

7. **Keep Builder Separate**: When possible, use dedicated builder images with all tools pre-installed

8. **Documentation**: Add comments explaining each stage's purpose

### Distroless-Specific Best Practices

1. **Use Distroless for Production**: Always prefer distroless for production images
   ```dockerfile
   # Production image
   FROM gcr.io/distroless/base-debian11
   
   # Development/debugging image
   FROM alpine:latest
   ```

2. **Choose the Right Distroless Variant**:
   ```dockerfile
   # For Go applications
   FROM gcr.io/distroless/base-debian11
   
   # For Python applications
   FROM gcr.io/distroless/python3
   
   # For Node.js applications
   FROM gcr.io/distroless/nodejs
   
   # For static binaries only
   FROM gcr.io/distroless/static
   ```

3. **Static Compilation for Minimal Images**:
   ```dockerfile
   # Build with static linking
   RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o app .
   
   # Use with distroless or scratch
   FROM scratch
   COPY --from=builder /app/app /app
   ```

4. **Copy Only Essential Files**:
   ```dockerfile
   # Copy only the binary, nothing else
   COPY --from=builder /app/binary /app
   
   # Avoid copying source code or build artifacts
   # COPY --from=builder /app . # ❌ Don't do this
   ```

5. **Set Non-Root User for Security**:
   ```dockerfile
   FROM gcr.io/distroless/base-debian11
   
   # Distroless provides nonroot user by default
   USER nonroot
   
   COPY --from=builder /app/binary /app
   ENTRYPOINT ["/app"]
   ```

6. **Use Multi-Stage with Distroless Security Scanning**:
   ```bash
   # Build with distroless
   docker build -t myapp:latest .
   
   # Scan for vulnerabilities
   docker scan myapp:latest
   
   # Push to registry with confidence
   docker push myapp:latest
   ```

7. **Create Separate Dev and Prod Dockerfiles**:
   ```dockerfile
   # Dockerfile (production - distroless)
   FROM golang:1.21-alpine as builder
   COPY . .
   RUN go build -o app .
   
   FROM gcr.io/distroless/base-debian11
   COPY --from=builder /app /app
   
   # Dockerfile.dev (development - Alpine with tools)
   FROM golang:1.21-alpine
   WORKDIR /app
   COPY . .
   RUN go build -o app .
   ENTRYPOINT ["./app"]
   ```

8. **Document Base Image Choice**:
   ```dockerfile
   # Use gcr.io/distroless/base-debian11 instead of Alpine because:
   # - No shell interpreter (security)
   # - No package manager (reduced CVEs)
   # - Standard glibc (better compatibility)
   # - Smaller than Alpine (3.81 MB vs 5-10 MB)
   FROM gcr.io/distroless/base-debian11
   ```

## Common Errors

### General Multi-Stage Build Errors

**Error: "COPY --from: Stage Not Found"**
- **Cause**: Referencing a stage that doesn't exist or misspelled name
- **Solution**: Verify stage name in `as` keyword matches the `--from` reference

**Error: "File Not Found After COPY --from"**
- **Cause**: Copying from incorrect path in builder stage
- **Solution**: Verify the file path exists in builder stage; use absolute paths

**Error: "Dynamic Variable Not Substituted"**
- **Cause**: Using variables in `--from` flag without build args
- **Solution**: Use `--build-arg` for dynamic stage names:
```bash
docker build --build-arg BUILDER_STAGE=mybuild .
```

**Error: "Large Final Image Size"**
- **Cause**: Copying unnecessary files or using heavy base image
- **Solution**: Use Alpine, Distroless, or Scratch; verify COPY --from targets

**Error: "Binary Not Executable"**
- **Cause**: Cross-compilation flags missing
- **Solution**: Set proper build environment variables:
```dockerfile
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o timer .
```

### Distroless-Specific Errors

**Error: "exec /app: no such file or directory"**
- **Cause**: Binary path incorrect in distroless image
- **Solution**: Verify ENTRYPOINT path matches COPY target
```dockerfile
COPY --from=builder /app/binary /app    # Destination is /app
ENTRYPOINT [ "/app" ]                    # Must match
```

**Error: "standard_init_linux.go:228: exec user process caused: no such file or directory"**
- **Cause**: Binary was compiled for wrong architecture or dynamic dependencies missing
- **Solution**: Build with proper flags for distroless
```dockerfile
# For distroless (needs glibc)
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o app .

# Verify ldd shows required libraries
RUN ldd ./app
```

**Error: "cannot execute binary file: Exec format error"**
- **Cause**: Attempting to run architecture-incompatible binary in distroless
- **Solution**: Ensure builder and distroless architecture match
```dockerfile
FROM golang:1.21-alpine as builder
# Default is amd64, matches distroless/base-debian11

FROM gcr.io/distroless/base-debian11 
# Also amd64 by default - architectures match ✓
```

**Error: "Segmentation fault" or runtime errors in distroless**
- **Cause**: Distroless may have different glibc version or missing libraries
- **Solution**: Compile with Alpine or use dynamic linking test
```bash
# Test in Alpine first
docker run -it --rm -v $(pwd):/app alpine:latest
apk add libc6-compat
/app/binary

# Then test in distroless
docker run -it --rm myapp:distroless
```

**Error: "Cannot debug - no shell in distroless"**
- **Cause**: distroless has no shell for debugging
- **Solution**: Create debug image with same binary
```dockerfile
# production image (distroless)
FROM gcr.io/distroless/base-debian11 as prod
COPY --from=builder /app/binary /app
ENTRYPOINT ["/app"]

# debug image (alpine)
FROM alpine as debug
COPY --from=builder /app/binary /app
RUN apk add --no-cache bash curl strace
ENTRYPOINT ["/app"]
```

**Error: "Distroless image not found or authentication failed"**
- **Cause**: Registry credentials not configured or network issues
- **Solution**: Pull explicitly and check credentials
```bash
# Login to gcr.io
docker login gcr.io

# Try pulling
docker pull gcr.io/distroless/base-debian11

# Check authentication
docker logout && docker login gcr.io
```

**Error: "Application works in Alpine but fails in distroless"**
- **Cause**: Distroless has different glibc, timezone data, or SSL certificates
- **Solution**: Copy missing dependencies from builder
```dockerfile
FROM golang:1.21-alpine as builder
RUN go build -o app .

FROM gcr.io/distroless/base-debian11

# Copy system dependencies if needed
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo

COPY --from=builder /app/app /app
ENTRYPOINT ["/app"]
```

## References

### Official Documentation
- [Docker Multi-Stage Builds Official Documentation](https://docs.docker.com/build/building/multi-stage/)
- [Google Distroless Project](https://github.com/GoogleContainerTools/distroless)
- [Distroless Images Documentation](https://github.com/GoogleContainerTools/distroless/tree/main/base)

### Build Optimization
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Image Size Optimization](https://docs.docker.com/build/building/multi-stage/#use-multi-stage-builds)
- [Go Cross-Compilation](https://golang.org/doc/install/source#environment)

### Base Images
- [Alpine Linux Official Images](https://hub.docker.com/_/alpine)
- [Distroless Base Images](https://github.com/GoogleContainerTools/distroless/tree/main/base)
- [Scratch Image Documentation](https://docs.docker.com/build/building/multi-stage/#use-multi-stage-builds-to-reduce-image-size)

### Security and Compliance
- [NIST Container Security Recommendations](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Container Security](https://owasp.org/www-community/vulnerabilities/Insecure_Container)

### Practical Examples
- [Distroless Getting Started](https://github.com/GoogleContainerTools/distroless#getting-started)
- [Multi-Stage Builds Examples](https://docs.docker.com/build/building/multi-stage/#name-your-build-stages)
- [Go Binary in Distroless](https://github.com/GoogleContainerTools/distroless/blob/main/base/README.md)

### Tools and Resources
- [Docker Scout - Image Scanning](https://www.docker.com/products/docker-scout/)
- [Trivy - Vulnerability Scanner](https://aquasecurity.github.io/trivy/)
- [Syft - SBOM Generator](https://github.com/anchore/syft)
- [Cosign - Container Signing](https://github.com/sigstore/cosign)
