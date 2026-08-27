# Mindflix AI - DevOps Engineer Written Test Answers

**Name:** Shreyas M  
**Date:** August 27, 2026

---

## Q1.kubectl get pods
```bash 
shows:
api-7b9dfd8c5d-x1 1/1 Running
api-7b9dfd8c5d-x2 1/1 Running

But:
kubectl get endpoints api

shows:
 <none>

The Service is:
spec:
    selector:
        app: api

The pod labels are:
    labels:
        app: backend
```

### Questions

### 1. Why does Running not mean the service is reachable?

Ans: Running state in Kubernetes will indicate that the container process is running and hasn't crashed which shows the container status to confirm that it is alive. Service reachability however, require proper configuration of network.
    - A service msut have matching selectors
    - It must target a correct container port binding and address
    - The controller must be able to populate the endpoints
    - policies should be allowed for the traffic

When the pod is in Running state but of still unreachable it can be because:
    - The listening port not matching with the service requirement.
    - The labels does not match with the selector
    - The namespaces is in different namespace

### 2. What is the immediate root cause?

Ans: To identify the root cause would check with the label mismatch of the service which it is looking for (ex, app: application), but the pods have the label as (ex, app: delivery-app) as there are no pods match the selector.
    - service endpoints connot find the pods
    - endpoints object would remain empty 
    - no traffic would be routing to the necessary pod

### 3. Which commands would you run to verify Service → Endpoint → Pod connectivity?

Ans. 
```bash
# get the service details of the selector
kubectl describe svc api

# check the endpoint object
kubectl get ep api -o yaml

# check pod labels if any mismatch
kubectl get pods --show-labels

# verify service selector specifically
kubectl get svc api -o jsonpath='{spec.selector}'

# test the domain resolution
kubectl exec -it (pod-name) --nslookup api.(namespace).svc.cluster.local

# check if service get any endpoints if any
kubectl get endpoints api -o yaml | grep -A "subsets"

# check & verify the deployment labels 
kubectl get deployment -o yaml | grep -A "labels"
```

### 4. Would restarting the pods fix this?

Ans. No, restarting will not fix the pod issue because.
-  A new pod will be created with the same label
- The service selector remains unchanged
- Underlying configuration mismatches persists

### Necessary fix for the service update 
```bash 
spec: 
    selector:
        app:delivery-lab
```
### Apply the necessary changes
```bash 
kubectl edit svc api
# or
kubectl apply -f updated-service.yaml
```


## Q2.A service depends on PostgreSQL.
```bash 
Liveness:
    livenessProbe:
        httpGet:
            path: /health
            port: 8080
```
/health fails whenever PostgreSQL is temporarily unavailable. <br>
During a DB incident, every application pod restarts repeatedly.

## Questions
### 1. Explain the failure amplification.
Ans. This creates a failure cycle as 
```bash 
DB failure -> endpoints will fail -> liveness probe fails -> pod keeps restarting -> new pods will start & DB stays unavailable ->  endpoint fails again -> pod would be killed -> this cycle points to (CrashLoopBackOff)
```
This effects which follow are as below:
- Increased load: All restart adds stress to the cluster scheduler
- Longer downtime: instead of app staying in running state it become completely unavailable.
- Waste of resource: restarting consumes CPU & memory
- Cascading failure: All replicas restart in rolling wave
- Delayed recovery: When a DB recovers, all pods are in CrashLoopBackOff which would need manual intervention

### 2. What should liveness check? 
Ans. The Liveness should only check a process health:
The liveness endpoint should 
- check if web server is running.
- respond with a 200 OK status code 
- will not check DB connection
- will not check external API's
- will not check any message queues
- will not check any cache connections

Will restart a stuck/dead application process, not validate any environments

### 3. What should readiness check?
Ans. Readiness should check full application functionality:
the readiness endpoint should control traffic flow to the pod not restart it.
- check the database connectivity
- verify message queue availability
- validate cache connections
- confirm external API connectivity
- Return 503 if dependencies are unavailable

### 4. When can dependency checks inside readiness also become dangerous?
Ans. Dangerous scenario to complete dependency outage
If all the replicas check the same unhealth dependency: 
Database outage -> Pods fail readiness check -> Pods remove service endpoint -> service has no healthy endpoint -> 503 application failure -> service outage  

- The application logic might still work only in (cached data, read-only mode)
- The partial functionality, you get complete unavailibility.
- Can create a self-inflicted denial of service
- Recovery would require the dependency to fully recover before any traffic flow

1. Fail-open approach: Consider the pod if it can connect to a majority of dependencies.
2. Grace period: Dont remove pod immediately on the first failure. 
3. check break pattern: Implement breakers in the application to hanfle dependency failure gracefully

## Q3.
```bash 
FROM node:22
ARG NPM_TOKEN
ENV NPM_TOKEN=$NPM_TOKEN
RUN npm install
COPY . .
RUN npm run build
```
## Questions
### 1. Where can this token accidentally remain visible?

Ans. The token can persist in a multiple places: 
- Docker image layers
- Build Cache
- Build Logs
- Intermediate containers
- Layer Metadata
- Registry 

### 2. Why is deleting the environment variable in a later layer not necessarily enough?

Ans. Docker layers are immutable. Deleting in a later layer doesn't remove it from earlier layer

```bash
ENV NPM_TOKEN=secret-token

RUN npm install

ENV NPM_TOKEN= 
```
The only safe approach: Never write the token to the image in the first place. 

### 3 . What safer build mechanism would you use?

## Method 1: BuildKit Secrets
```bash
#For Base Image
FROM node:22 AS builder

WORKDIR /app
COPY package*.json ./

RUN --mount=secret, id=npm-token \
    export NPM_TOKEN=$(cat /run/secrets/npm_token) && \
    npm install 

COPY . .
RUN npm run build
# Production stage 
FROM node:22-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json . 

USER node
EXPOSE 8080
CMD [ "node", "dist/index.js"]
 
```

## Build command:
```bash 
DOCKER_BUILDKIT=1 docker build \
    --secret id=npm_token, src=./.npmrc \
    -t delivery-lab:latest .
```

### 4. What should happen to the tocken after a suspected leak?

1. Immediate Action :
- Revoke the token immediately in the registy.
- Check for any unauthorized access in the registry.
- Block the token in any CDN layers

2. Investigation:
- Audit build logs for token exposure
- Check CI/CD pipelines scret storage
- Review Docker image layers in registry
- Identify all build environements that's used in token

3. Remedy 
- Generate new token with same permission
- Update secrets in CI/CD pipeline
- Remove comparision image from registry 
- Update all file 

4. Preventing 
- Implement secret scannign in CI/CD
- Use BuildKit secretes 
- Rotate token regularly
- Use npm's fine grain access tokens
- Add token usage for monitorig/ alerts

## Q4 Workflow:
```bash
on:
    pull_request_target:
jobs:
    test:
        steps:
            - uses: actions/checkout@v4
            with:
                ref: ${{ github.event.pull_request.head.sha }}
            - run: npm install
            - run: npm test
            env:
                PROD_TOKEN: ${{ secrets.PROD_TOKEN }}
```
### Questions

1. What security risk do you see?

Ans. High Risk: Script Injection attack
This is extremely dangerous because: 
- pull_request_target | Runs with base repo permission | Access to ALL secrets|
- token exposed | Token available in environment | Used for any kind of attackers
- npm install | Executes code from apckage.json | can run arbitrary code
- npm test | executes untrusted test code | can compromise CI environment

### potential consequences:

- Secret exfiltration
- CI environment compromise
- Production infrastructure access
- Data Breach

2. Why is executing untrusted PR code with secrets dangerous?

The danger comes from the combination of two factors:
a. Untracted code: PRs from forks can contain any code you cant trust:
- The Repository
- The package.json scripts
- The npm package installed
- The test code itself

b. High Value Secrets: The PROD_TOKEN likely has: 
- Production deployment access
- Infrastructure modification permission
- Sensitivity data access
- Registry write permission

3. How would you separate untrusted testing from trusted deployment?
Ans. Two-workflow Architecture

Workflow 1: Untrusted Testing 
```bash 
# .github/workflows/pr-test.yml
name: PR Test

on:
  pull_request:  
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read 
      pull-requests: write 
    
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install
      
      - name: Run tests
        run: npm test
      
      - name: Security scan
        run: |
          npm audit --audit-level=high
          ! grep -r "curl.*\\$" *.js || exit 1
      
      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Tests passed! Ready for review.'
            })
```

workflow 2 : Trusted Deployment 
```bash 
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:  # Manual trigger

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # For OIDC
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate via OIDC
        uses: aws-actions/configure-aws-credentials@v3
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-deploy
          aws-region: us-east-1
      
      - name: Build and deploy
        run: |
          docker build -t my-app:latest .
          # Only runs on trusted, merged code
          ./deploy.sh
```

4. What permissions would you minimize?

Ans. Principel of least privilege - Minimum Required permission

For PR Testing workflow
```bash 
permissions:
  contents: read
  pull-requests: write 
```

For deployment workflows
```bash
permissions:
  contents: read
  id-token: write
  packages: write 
```

Repository level settings:

```bash 
# .github/settings.yml
rulesets:
  - name: Protection Rules
    conditions:
      ref_name:
        include: ["refs/heads/main"]
    rules:
      - require_code_owner_review
      - require_last_push_author
      - require_signed_commits
      - require_conversation_resolution
      - required_status_checks:
          contexts:
            - "PR Test"
            - "Security Scan"
      - restrict_pushes:
          bypass_mode: "admins_only"
```
- PR tests run with contents: read only
- Security scans happen on every PR
- Deployments require
    - Manual Approval
    - Two-person review
    - Successful PR tests
    - No high-severity vulnaribilities