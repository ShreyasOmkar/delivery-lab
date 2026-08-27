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


1. What should liveness test that readiness should not?

Ans. Lliveness should test the application is live and responsive, which should not test external dependencies. If a liveness probe fails, the container is restarted.
Readiness probes should test that the application is fully functional and ready for traffic. This test includes connection to database or external API's. If a readiness probe fails, pod is removed from the service but the pos isn't restarted. 

2. Why do Kubernetes requests affect scheduling?

Ans. The requests field tells the Kubernetes scheduler the minimum amount of CPU and memory a container needs to run. The scheduler uses this information to find a node that has sufficient available resources. If a node doesn't have free resources to stisfy the request, the pod won't be scheduled there, this will ensure the pods get the resources they need and prevents resource contention.

3. How can a rollout be Kubernetes-healthy but user-unhealthy?

Ans. A rollout is considered kubernetes healthy if all replicas are running and pass their readiness and liveness probe. However the application might be user-unhealthy
- A logical bug that returns wronf data.
- A performance issue causing high latency that will not cause the probe to fail. 
- Misconfigured data that causes slow queries but still returns 200 status for health endpoint. 
- Incorrect dependency logic where the app is ready cut which cant compelete the transactions

4. How would you authenticate CI to a cloud provider without static keys?
Ans. Use GitHub Actions OIDC/workload identity federation. Bind a narrowly scoped cloud role to repository, branch, workflow, and protected-environment claims; exchange the signed OIDC token for short-lived credentials only in the deployment job.


5. What is one dangerous Terraform/state mistake you would prevent in production?
Ans. Use GitHub Actions OIDC/workload identity federation. Bind a narrowly scoped cloud role to repository, branch, workflow, and protected-environment claims; exchange the signed OIDC token for short-lived credentials only in the deployment job.


6. What metrics/logs would you want before allowing automatic rollback?

Ans. Use a minimum sample window and compare the new revision against baseline for request rate, 5xx/error ratio, p95/p99 latency, saturation, restart/OOM rate, readiness, and critical business success signals. Correlate structured logs/traces by revision and distinguish application regressions from dependency-wide incidents to avoid a harmful rollback loop.



7. What changes would you make if this service handled 10x traffic?

Ans. Load-test first; tune worker/concurrency and connection limits; add an HPA using CPU plus request/concurrency signals; set topology spread and a PodDisruptionBudget; right-size requests/limits; add ingress rate limits/timeouts; cache where correct; protect downstreams with bounded queues, timeouts, backoff, and circuit breakers; and verify database capacity and observability cardinality.

8. What shortcut did you intentionally take?

Ans. 
The exercise uses an in-process application with no real dependency, ingress, TLS, registry publishing, autoscaling, or production cloud target. CI proves deployment in ephemeral kind. Production would use immutable image digests, signed artifacts/SBOM, pinned action SHAs, environment-specific overlays, external secret management, policy enforcement, and SLO-based progressive delivery.