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

## 1. Why does Running not mean the service is reachable?

Ans: Running state in Kubernetes will indicate that the container process is running and hasn't crashed which shows the container status to confirm that it is alive. Service reachability however, require proper configuration of network.
    - A service msut have matching selectors
    - It must target a correct container port binding and address
    - The controller must be able to populate the endpoints
    - policies should be allowed for the traffic

When the pod is in Running state but of still unreachable it can be because:
    - The listening port not matching with the service requirement.
    - The labels does not match with the selector
    - The namespaces is in different namespace

## 2. What is the immediate root cause?

Ans: To identify the root cause would check with the label mismatch of the service which it is looking for (ex, app: application), but the pods have the label as (ex, app: delivery-app) as there are no pods match the selector.
    - service endpoints connot find the pods
    - endpoints object would remain empty 
    - no traffic would be routing to the necessary pod

## 3. Which commands would you run to verify Service → Endpoint → Pod connectivity?

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

## 4. Would restarting the pods fix this?

Ans. No, restarting will not fix the pod issue because
    1. A new pod will be created with the same label
    2. The service selector remains unchanged
    3. Underlying configuration mismatches persists

## Necessary fix for the service update 
```bash 
spec: 
    selector:
        app:delivery-lab
```
## Apply the necessary changes
```bash 
kubectl edit svc api
# or
kubectl apply -f updated-service.yaml
```
=====================================================================

### Q2.A service depends on PostgreSQL.
```bash 
Liveness:
    livenessProbe:
        httpGet:
            path: /health
            port: 8080
```
/health fails whenever PostgreSQL is temporarily unavailable.
During a DB incident, every application pod restarts repeatedly.

## Questions
# 1. Explain the failure amplification.
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

# 2. What should liveness check? 
Ans. The Liveness should only check a process health:
# The liveness endpoint should 
- check if web server is running.
- respond with a 200 OK status code 
- will not check DB connection
- will not check external API's
- will not check any message queues
- will not check any cache connections

# Will restart a stuck/dead application process, not validate any environments

3. What should readiness check?
Ans. Readiness should check full application functionality:
# the readiness endpoint should control traffic flow to the pod not restart it.
- check the database connectivity
- verify message queue availability
- validate cache connections
- confirm external API connectivity
- Return 503 if dependencies are unavailable

4. When can dependency checks inside readiness also become dangerous?
Ans. Dangerous scenario to complete dependency outage
If all the replicas check the same unhealth dependency: 
Database outage -> Pods fail readiness check -> Pods remove service endpoint -> service has no healthy endpoint -> 503 application failure -> service outage  

