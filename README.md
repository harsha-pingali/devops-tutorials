# DevOps Tutorials

A comprehensive repository of hands-on DevOps tutorials covering containerization, orchestration, infrastructure automation, and modern deployment practices.

## 📚 Overview

This repository is a learning resource for DevOps engineers, cloud architects, developers, and operations teams who want to master industry-standard tools and practices. Each tutorial includes complete documentation, working examples, best practices, and real-world scenarios.

---

## 📑 Quick Navigation

- [Repository Index](#repository-index)
- [Getting Started](#getting-started)
- [Tutorials Overview](#tutorials-overview)
- [Documentation](#documentation)

---

## 📂 Repository Index

```
devops-tutorials/
│
└── /docker_tutorials
    ├── /fast_app
    └── /multi-stage-builds
```

---

## 🎓 Getting Started

### Prerequisites

- **Docker** (latest version) - [Install](https://docs.docker.com/get-docker/)
- **Git** - [Install](https://git-scm.com/downloads)
- **Basic DevOps/Linux knowledge**

Additional requirements for specific tutorials are listed in their directories.

### Clone Repository

```bash
git clone https://github.com/harsha-pingali/devops-tutorials.git
cd devops-tutorials
```

---

## 📋 Tutorials Overview

### 1. FastAPI Application (`docker_tutorials/fast_app/`)

**Containerizing a FastAPI Web Application**

- **Difficulty:** Beginner
- **Duration:** 1-2 hours
- **Topics:** Docker basics, Python containerization, web applications

**Quick Start:**
```bash
cd docker_tutorials/fast_app
cat notes.md              # Read the complete guide
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

---

### 2. Multi-Stage Builds (`docker_tutorials/multi-stage-builds/`)

**Advanced Docker Image Optimization**

- **Difficulty:** Intermediate/Advanced
- **Duration:** 2-4 hours
- **Topics:** Multi-stage builds, image optimization, security, distroless images, cost reduction

**Quick Start:**
```bash
cd docker_tutorials/multi-stage-builds
cat notes.md              # Read the complete guide
docker build -f Dockerfile.bad -t timer:bad .
docker build -f Dockerfile -t timer:distroless .
docker images timer:*     # Compare sizes
```

**Size Comparison:**
- Single-Stage: 638 MB ❌
- Multi-Stage (Alpine): ~10 MB ✓
- Multi-Stage (Distroless): 3.81 MB ✅

---

## 📚 Documentation

Each tutorial directory contains:

- **notes.md** - Comprehensive tutorial guide with theory, setup, and best practices
- **BUILD_REFERENCE.md** - Quick copy-paste commands (where applicable)
- **VISUAL_GUIDE.md** - Visual comparisons and ASCII diagrams (where applicable)
- **Working code examples** - Production-ready code and configurations

---

## 📊 Repository Statistics

- **Total Documentation:** 1,743+ lines
- **Code Examples:** 20+
- **Tutorials:** 2 comprehensive tutorials
- **Dockerfiles:** 4 versions for comparison
- **Best Practices:** 15+ documented
- **Visual Diagrams:** 10+ ASCII visualizations

---

## 🎯 Learning Paths

### Beginner Path
1. Read `docker_tutorials/fast_app/notes.md`
2. Build and run the FastAPI application
3. Understand basic Docker concepts

### Intermediate Path
1. Complete the beginner path
2. Read `docker_tutorials/multi-stage-builds/notes.md`
3. Compare the three Dockerfile approaches
4. Study best practices and optimization

### Advanced Path
1. Complete intermediate path
2. Review distroless image architecture
3. Implement in your own projects
4. Optimize for production deployment

---

## 🔗 External Resources

- [Docker Documentation](https://docs.docker.com/)
- [Google Distroless Project](https://github.com/GoogleContainerTools/distroless)
- [NIST Container Security](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

For additional references, see the "References" section in each tutorial's `notes.md`.

---

## 📝 Repository Info

- **Repository:** devops-tutorials
- **Owner:** harsha-pingali
- **Branch:** main
- **Status:** ✅ Production Ready
- **Last Updated:** June 7, 2026

---

**Start learning today! 🚀**

Begin with `docker_tutorials/fast_app/notes.md` for a comprehensive introduction to DevOps containerization practices.
