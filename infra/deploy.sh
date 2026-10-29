#!/bin/sh
set -e
kubectl create configmap kairos-db-init \
  --from-file=api/db/schema.sql --from-file=api/db/seed.sql --from-file=infra/grants.sql \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f infra/
