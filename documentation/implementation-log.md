# DevSecOps Implementation Journal

## Milestone 1: Environment and Repository Setup

Date: 31 October 2026

- Installed and verified Git, VS Code, AWS CLI and Terraform.
- Installed Docker Desktop and verified using hello-world.
- Verified WSL 2 and kubectl.
- Created the devsecops-platform directory structure.
- Initialized the Git repository.
- Created README.md and .gitignore.
- Created GitHub repository and pushed the initial commit.

## Milestone 2: Sample Application

Status: Completed

Objective:
Develop a lightweight Python Flask application with
home, health-check and version endpoints.

Implementation results:
Success.

Verification:
Success.

## Milestone 3: Docker Containerization

**Status:** Container started successfully; HTTP verification pending.

### Implementation
- Created a Dockerfile for the Flask application.
- Built the Docker image `devsecops-app:v1`.
- Started a container named `devsecops-app`.
- Published container port 5000 to host port 5000.

### Observed Container Details
- Image: devsecops-app:v1
- Container name: devsecops-app
- Container status: Up
- Port mapping: 5000:5000

### Verification
- Docker container startup: Successful.
- HTTP endpoint verification: Pending.
- Container log inspection: Pending.


### Final Verification — Docker Containerization

**Status: COMPLETED**

The Flask application was successfully containerized using Docker.

Verification performed:
1. Docker image built successfully.
2. Container started successfully.
3. Container status verified using `docker ps`.
4. Home endpoint tested successfully.
5. Health endpoint tested successfully.
6. Version endpoint tested successfully.

**Container configuration:**
- Image: devsecops-app:v1
- Container: devsecops-app
- Host port: 5000
- Container port: 5000

**Conclusion:**

The application operates successfully inside a Docker container and its HTTP endpoints are accessible through the published host port.