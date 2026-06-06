# Dockerized FastAPI Application

## Overview

This tutorial demonstrates how to containerize a FastAPI web application using Docker. The application serves a simple "Hello World" HTML page with styled CSS through a FastAPI server running inside a Docker container with Ubuntu as the base image. This project teaches you the fundamentals of containerization, dependency management, and web server configuration.

---

## SETUP

### System Dependencies Required

Before starting, you need to have these tools installed on your computer:

1. **Python 3** (version 3.8 or higher)
   - Provides the runtime environment for FastAPI applications
   - Download from: https://www.python.org/downloads/

2. **Docker** (latest stable version)
   - Container engine that allows you to package and run applications in isolated environments
   - Download from: https://www.docker.com/products/docker-desktop

3. **Git** (optional, for cloning repositories)
   - Version control system

**Installation Verification:**
```bash
python3 --version      # Should show Python 3.x.x
docker --version       # Should show Docker version
```

### Application Libraries Required

These Python packages are listed in `requirements.txt` and must be installed:

1. **FastAPI** - Web framework for building modern APIs with Python
   - Provides decorators and utilities to create web endpoints
   - Automatically generates API documentation

2. **Uvicorn** - ASGI application server
   - Runs the FastAPI application and serves HTTP requests
   - ASGI = Asynchronous Server Gateway Interface (handles concurrent requests efficiently)

3. **Jinja2** - Template engine for rendering dynamic content
   - While not directly used in this basic example, it's included for template rendering capabilities

### Installation Steps

#### Step 1: Create and Activate Virtual Environment
```bash
# Navigate to project directory
cd docker_tutorials/fast_app

# Create a virtual environment (isolated Python environment)
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Your terminal prompt should now show (venv) prefix
```

**Why virtual environment?** - It isolates project dependencies from your system Python, preventing conflicts between projects.

#### Step 2: Install Application Libraries
```bash
# Install packages from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list  # Should show fastapi, uvicorn, jinja2
```

**What happens:** pip reads `requirements.txt` and downloads/installs each package from PyPI (Python Package Index).

### Project Structure and Control Flow

```
fast_app/
├── Dockerfile                 # [BUILD INSTRUCTIONS] Container blueprint
├── main.py                    # [ENTRY POINT] FastAPI application code
├── requirements.txt           # [DEPENDENCY LIST] Python packages needed
├── templates/
│   └── index.html            # [VIEW] HTML template served by FastAPI
└── static/
    └── styles.css            # [STYLING] CSS for styling the HTML page
```

#### Control Flow Explanation:

1. **Start**: Run `uvicorn main:app --host 0.0.0.0 --port 8000`
   - This command tells Uvicorn to start the FastAPI application

2. **main.py loads**:
   ```python
   from fastapi import FastAPI
   app = FastAPI()  # Create application instance
   ```
   - FastAPI creates the main application object

3. **Routes defined**:
   ```python
   @app.get("/")
   def read_root():
       return FileResponse(...)  # Return HTML file
   ```
   - When user visits `/`, this function executes

4. **Static files mounted**:
   ```python
   app.mount("/static", StaticFiles(directory="static"))
   ```
   - Enables serving CSS files from `/static/` directory

5. **Request arrives**: Browser sends GET request to `http://localhost:8000/`

6. **Response generated**: 
   - FastAPI reads `templates/index.html`
   - Browser loads `static/styles.css`
   - HTML + CSS rendered in browser

#### File-by-File Breakdown:

**main.py** (Application Logic):
- Imports FastAPI framework
- Mounts static files directory
- Defines root route that returns index.html
- This is where all business logic lives

**Dockerfile** (Container Configuration):
- Specifies base image (ubuntu:latest)
- Installs Python and pip
- Creates virtual environment
- Copies requirements and code
- Configures startup command
- Think of this as a recipe for creating a container

**requirements.txt** (Dependencies):
- Lists all Python packages needed
- pip uses this file to know what to install

**templates/index.html** (Frontend):
- Static HTML content
- Contains the "Hello World" message
- References CSS from /static/styles.css

**static/styles.css** (Styling):
- CSS rules for styling the HTML
- Uses CSS variables for theming
- Creates the card-based layout

---

## CONCEPTS

### 1. Docker Containerization

**What is Docker?**
Docker packages your entire application (code + dependencies + runtime) into a container. A container is like a lightweight virtual machine that includes everything needed to run your application, ensuring it works the same way everywhere.

**Why use Docker?**
- **Consistency**: Works on your laptop, staging server, and production identically
- **Isolation**: Application dependencies don't conflict with system packages
- **Reproducibility**: Others can run exact same environment using your Dockerfile
- **Scalability**: Easy to run multiple instances of the same application

**Container vs Image:**
- **Image**: A blueprint/template (like a recipe)
- **Container**: A running instance created from an image (like a cooked meal)

### 2. Dockerfile Deep Dive

**`FROM ubuntu:latest`**
- Specifies the base layer (starting point)
- ubuntu:latest contains a minimal Ubuntu Linux operating system
- All subsequent layers build on top of this
- Alternative: `FROM python:3-slim` would be more efficient (smaller, includes Python)

**`ENV DEBIAN_FRONTEND=noninteractive`**
- Sets environment variable to prevent interactive prompts
- Without this, installation would pause waiting for user input
- Necessary for automated container builds

**`WORKDIR /app`**
- Sets the working directory inside container to `/app`
- All subsequent commands execute in this directory
- Creates the directory if it doesn't exist

**`RUN apt-get update && apt-get install -y ...`**
- `apt-get` = Advanced Package Tool (package manager for Debian/Ubuntu)
- `update` = refresh package lists
- `-y` = automatically answer "yes" to prompts
- Installs Python 3, pip, and venv support

**Layer Caching - Order Matters:**
```dockerfile
# ✅ GOOD - Caches dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# ❌ BAD - Reinstalls dependencies every time code changes
COPY . .
RUN pip install -r requirements.txt
```

If code changes, Docker rebuilds layers from the change point. By copying requirements first, dependencies cache and rebuilds are faster.

**`RUN python3 -m venv /app/venv`**
- Creates an isolated Python environment
- `venv` = virtual environment module
- Isolates project packages from system Python

**`ENV PATH="/app/venv/bin:$PATH"`**
- Modifies PATH (list of directories where system looks for executables)
- Prepends virtual environment's bin directory
- Ensures all subsequent Python commands use venv's Python
- Without this, `pip install` would install to system Python (bad practice)

**`RUN pip install --no-cache-dir -r requirements.txt`**
- `--no-cache-dir` = don't store downloaded packages
- Reduces image size significantly (important for production)
- You don't need cached wheels inside a container (they're not reused)

**`COPY requirements.txt .` then `COPY . .`**
- First copy = only requirements (allows caching)
- Second copy = remaining application files
- Leverages Docker's layer caching for faster rebuilds

**`EXPOSE 8000`**
- Documents that application listens on port 8000
- **Important**: This doesn't actually open the port!
- Must use `docker run -p 8000:8000` to map ports

**`ENTRYPOINT ["uvicorn"]` and `CMD ["main:app", "--host", "0.0.0.0", "--port", "8000"]`**

These work together:
- `ENTRYPOINT` = the immutable main command (not overridable in normal use)
- `CMD` = arguments to ENTRYPOINT (can be overridden)
- Together: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Allows flexibility: `docker run fast-app main:app --port 8080` (changes port)

### 3. FastAPI Application Structure

**`from fastapi import FastAPI`**
- Imports the FastAPI class
- FastAPI is a modern Python web framework

**`app = FastAPI()`**
- Creates an instance of FastAPI application
- This is the core of your web application
- All routes and middleware attach to this object

**Route Decorator: `@app.get("/")`**
- Decorator = Python function wrapper
- `@app.get("/")` = create a GET HTTP endpoint at root path `/`
- When user visits `http://localhost:8000/`, this function executes
- **HTTP Methods**: GET (retrieve), POST (create), PUT (update), DELETE (delete)

**`FileResponse`**
- Returns a file from disk as HTTP response
- Browser receives file contents and renders it
- Sets appropriate content-type headers (text/html for .html files)

**Static File Mounting: `app.mount("/static", StaticFiles(directory="static"))`**
- Mounts entire directory as static file server
- Files in `static/` accessible at `/static/` URLs
- Example: `static/styles.css` → accessible at `/static/styles.css`
- Use for CSS, JavaScript, images, etc.

### 4. Web Request Flow

```
1. User opens browser and navigates to http://localhost:8000/
2. Browser sends HTTP GET request to server
3. FastAPI receives request on route "/" 
4. Function read_root() executes
5. Returns FileResponse with templates/index.html
6. Browser receives HTML content
7. Browser parses HTML and finds <link rel="stylesheet" href="/static/styles.css">
8. Browser sends second HTTP request for /static/styles.css
9. FastAPI serves CSS from static directory
10. Browser applies CSS styling and renders complete page
```

### 5. Port and Host Configuration

**`--host 0.0.0.0`**
- Makes application accessible from any network interface
- 0.0.0.0 = "all IPv4 addresses on local machine"
- Allows access from same computer, other computers on network, and containers

**`--port 8000`**
- Application listens on port 8000
- Ports are numbered endpoints (0-65535)
- Common convention: port 8000 for development, 80/443 for production

**Port Mapping: `-p 8000:8000`**
- Format: `-p <host-port>:<container-port>`
- Connects container's internal port to your computer's port
- `-p 8001:8000` = access container's 8000 via your computer's 8001

---

## Best Practices

**1. Use Specific Base Images**
```dockerfile
# ❌ Avoid - 900MB image
FROM ubuntu:latest

# ✅ Better - 150MB image
FROM python:3-slim

# ✅ Best - 50MB image (if you need lightweight)
FROM python:3-alpine
```

**Why:** Smaller images = faster downloads, faster deployments, less storage needed.

**2. Multi-layer Ordering**
- Install system dependencies first (less frequently changed)
- Copy requirements and install packages (moderate frequency)
- Copy application code last (changes frequently)
- **Benefit:** Maximizes layer cache hits, speeds up development cycle

**3. Minimize Image Size**
- Clean up after installations: `rm -rf /var/lib/apt/lists/*`
- Use `--no-cache-dir` with pip
- Use slim/alpine base images
- Remove unnecessary packages
- **Benefit:** Faster image pulls, less storage, faster container startup

**4. Security Best Practices**
- Don't run as root (create non-root user)
- Use specific versions for base images instead of `latest`
- Scan images for vulnerabilities
- Don't include secrets in Dockerfile
- **Benefit:** Prevents unauthorized access and data breaches

**5. Development vs Production**
- **Development**: Use `--reload` flag with uvicorn (auto-restart on code changes)
- **Production**: Remove `--reload`, configure proper error handling, use production ASGI server

---

## Common Errors & Prevention

### ❌ Error: "Port 8000 is already allocated"
**What went wrong:** Another process is using port 8000
**Prevention:** 
- Check what's using the port: `lsof -i :8000`
- Use different port: `docker run -p 8001:8000 fast-app`
- Stop conflicting container: `docker stop <container-id>`

**What NOT to do:** Don't use ports below 1024 without sudo (they're reserved)

### ❌ Error: "No such file or directory: requirements.txt"
**What went wrong:** `COPY requirements.txt .` executed in wrong working directory
**Prevention:** 
- Ensure `WORKDIR /app` is set BEFORE any COPY commands
- Double-check file path in COPY command
- Verify requirements.txt exists locally

**What NOT to do:** Don't use relative paths without WORKDIR set first

### ❌ Error: "ModuleNotFoundError: No module named 'fastapi'"
**What went wrong:** Dependencies not installed or wrong Python interpreter used
**Prevention:** 
- Ensure `pip install -r requirements.txt` runs in Dockerfile AFTER venv setup
- Verify `ENV PATH="/app/venv/bin:$PATH"` is set correctly
- Run `pip list` to verify all packages are installed

**What NOT to do:** Don't forget to update PATH to use venv Python

### ❌ Error: "Cannot GET /"
**What went wrong:** Route not found or file doesn't exist in container
**Prevention:** 
- Verify `@app.get("/")` route is defined in main.py
- Ensure `templates/index.html` exists and is copied (COPY . .)
- Check function returns valid response
- Verify application imports (FileResponse, StaticFiles)

**What NOT to do:** Don't forget to copy template and static directories

### ❌ Error: "uvicorn: command not found"
**What went wrong:** uvicorn not installed in Docker or venv not activated locally
**Prevention:**
- Ensure uvicorn is in requirements.txt
- Local development: Activate venv with `source venv/bin/activate`
- Docker: Verify pip install runs AFTER venv is created
- Verify `ENV PATH` modification includes venv bin directory

**What NOT to do:** Don't forget to activate venv when developing locally

### ❌ Error: "Address already in use"
**What went wrong:** Another service using same host:port combination
**Prevention:** 
- Change port number with `-p 8001:8000`
- Stop conflicting services
- Use `docker ps` to see running containers

**What NOT to do:** Don't force-kill processes without understanding consequences

---

## Commands Reference

### Docker Commands
```bash
# Build image from Dockerfile
docker build -t fast-app .
# -t = tag/name the image

# Run container from image
docker run -p 8000:8000 fast-app
# -p = publish/map ports

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Stop running container
docker stop <container-id>

# Remove stopped container
docker rm <container-id>

# View container logs
docker logs <container-id>

# View real-time logs (follow mode)
docker logs -f <container-id>

# Execute command inside running container
docker exec -it <container-id> bash
```

### Local Development Commands
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI with auto-reload (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run without reload (production-like)
uvicorn main:app --host 0.0.0.0 --port 8000

# View installed packages
pip list

# Show what package provides a module
pip show fastapi

# Deactivate virtual environment
deactivate
```

---

## References

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/) - Complete API reference and tutorials
- [Uvicorn Documentation](https://www.uvicorn.org/) - ASGI server configuration details
- [Docker Documentation](https://docs.docker.com/) - Comprehensive Docker guide and reference
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/) - Production guidelines
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html) - Official venv tutorial
- [Docker ENTRYPOINT vs CMD](https://docs.docker.com/engine/reference/builder/#entrypoint) - Understanding entry points
