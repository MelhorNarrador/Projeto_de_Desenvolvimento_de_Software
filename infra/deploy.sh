#!/bin/sh
set -e
kubectl create configmap kairos-db-init \
  --from-file=api/db/schema.sql --from-file=api/db/seed.sql --from-file=infra/grants.sql \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n cnpg-system scale deployment cnpg-controller-manager --replicas=3
kubectl -n kube-system scale deployment coredns --replicas=3
kubectl apply -f infra/
