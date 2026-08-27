#!/bin/bash
set -e

NAMESPACE=$1
DEPLOYMENT=$2

if [ -z "$NAMESPACE" ] || [ -z "$DEPLOYMENT" ]; then
    echo "Usage: $0 <namespace> <deployment>"
    exit 1
fi

echo "=== Gathering diagnostics for deployment $DEPLOYMENT in namespace $NAMESPACE ==="

echo -e "\n--- 1. Pod Status ---"
kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT

echo -e "\n--- 2. Pod Details (with Node IP & Pod IP) ---"
kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT -o wide

echo -e "\n--- 3. Service and Endpoints ---"
kubectl get svc,endpoints -n $NAMESPACE | grep $DEPLOYMENT || echo "Service/Endpoint not found."

echo -e "\n--- 4. Rollout Status ---"
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE || echo "Rollout status unknown."

echo -e "\n--- 5. Events (sorted by time) ---"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10

echo -e "\n--- 6. Pod Descriptions ---"
for pod in $(kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT -o name); do
    echo -e "\n--- Details for $pod ---"
    kubectl describe $pod -n $NAMESPACE
done

echo -e "\n--- 7. Previous Container Logs (if any) ---"
for pod in $(kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT -o name); do
    echo -e "\n--- Previous logs for $pod ---"
    kubectl logs $pod -n $NAMESPACE --previous || echo "No previous logs found."
    echo -e "\n--- Current logs for $pod ---"
    kubectl logs $pod -n $NAMESPACE || echo "No current logs found."
done

echo -e "\n--- 8. Readiness/Liveness Probe Configuration ---"
kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}'
echo
kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].livenessProbe}'
echo

echo -e "\nDiagnostic gathering complete."