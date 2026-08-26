# Delivery Lab Service

A minimal HTTP service demonstrating production-ready DevOps practices including containerization, Kubernetes deployment, and CI/CD pipelines.

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Or using uvicorn locally
uvicorn app:app --host 0.0.0.0 --port 8080
```

### Using Docker
```bash
# Build the image
docker build -t delivery-lab:latest .

# Run the container
docker run -p 8080:8080 -e APP_VERSION=1.0.0 delivery-lab:latest
```

### Using Docker Compose
```bash
# will bring up the container with port and network
docker-compose up -d
```

### Deploy to Kubernetes
```bash 
kubectl apply -f k8s/
```

# Service Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | GET | Service information |
| `/health/live` | GET | Liveness probe—process health only |
| `/health/ready` | GET | Readiness probe—full functionality check |
| `/work` | GET | Simulated work with configurable delay |
| `/config` | GET | Show current configuration |
