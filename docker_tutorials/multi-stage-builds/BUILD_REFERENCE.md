# Quick Reference: Building and Comparing Multi-Stage Builds

## Build All Three Versions

```bash
# Bad Example: Single-Stage Build (ubuntu:latest)
docker build -f Dockerfile.bad -t timer:bad .

# Good Example: Multi-Stage with Alpine
docker build -f Dockerfile.distroless -t timer:alpine . 

# Best Example: Multi-Stage with Distroless
docker build -f Dockerfile -t timer:distroless .
```

## Compare Image Sizes

```bash
# View all timer images
docker images timer:*

# Output should show:
# timer:bad          < 638 MB (large - includes Go compiler)
# timer:alpine       < 10 MB  (small - only alpine base)
# timer:distroless   < 3.81 MB (minimal - only essential libs)
```

## Run and Test All Versions

```bash
# Test bad version
docker run timer:bad

# Test alpine version
docker run timer:alpine

# Test distroless version  
docker run timer:distroless
```

## Inspect Image Contents

```bash
# See what's in the bad image (large OS)
docker run -it timer:bad ls -lh /usr/bin | head -20

# See what's in distroless (minimal)
docker run -it timer:distroless ls -lh /

# Try to run shell in distroless (will fail)
docker run -it timer:distroless /bin/sh  # Error: /bin/sh not found

# Shell works in alpine
docker run -it timer:alpine /bin/sh  # Works
```

## Scan for Vulnerabilities

```bash
# Scan all three images
docker scan timer:bad
docker scan timer:alpine
docker scan timer:distroless

# distroless will have significantly fewer vulnerabilities
```

## Push to Registry

```bash
# Tag for registry
docker tag timer:distroless myregistry.azurecr.io/timer:v1.0
docker tag timer:alpine myregistry.azurecr.io/timer:v1.0-debug

# Push distroless (small, fast, secure)
docker push myregistry.azurecr.io/timer:v1.0

# Push alpine for debugging only
docker push myregistry.azurecr.io/timer:v1.0-debug
```

## File Structure Reference

```
multi-stage-builds/
├── Dockerfile              # Best: Multi-stage with distroless
├── Dockerfile.bad          # Bad: Single-stage with ubuntu
├── Dockerfile.distroless   # Alternative: Multi-stage with alpine  
├── timer.go               # Go application source
├── go.mod                 # Go module file
└── notes.md               # Complete documentation
```

## Key Takeaways

| Image | Size | Security | Shell | Package Manager | Use Case |
|-------|------|----------|-------|-----------------|----------|
| Dockerfile.bad | 638 MB | ❌ Weak | ✅ Yes | ✅ Yes | Educational only |
| Dockerfile.distroless | ~10 MB | ⚠️ Good | ✅ Yes | ✅ Yes | Debugging/development |
| Dockerfile | 3.81 MB | ✅ Excellent | ❌ No | ❌ No | Production ⭐ |

## Recommended Workflow

1. **Develop locally**: Use alpine or full image with tools
2. **Build CI/CD**: Use distroless for production
3. **Deploy production**: Use distroless image (smallest, most secure)
4. **Debug production issues**: Push separate debug image based on alpine
5. **Scan all images**: Check for CVEs before pushing to registry

## Performance Metrics

```bash
# Measure image build time
time docker build -f Dockerfile -t timer:distroless .

# Measure image pull time (simulated)
docker pull gcr.io/distroless/base-debian11

# Measure container startup time
time docker run --rm timer:distroless
```
