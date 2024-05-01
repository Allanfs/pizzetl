#!/bin/sh

SECRETS=PROJECT_ID=PROJECT_ID:1
SECRETS=$SECRETS,DESTINATION_TABLE_CONSOLIDADOR_PLATAFORMAS=DESTINATION_TABLE_CONSOLIDADOR_PLATAFORMAS:2

FUNCTION=DG-consolidar-pedidos
ENTRY_POINT=consolidar_plataformas
TRIGGER_BUCKET=dg-orders-southamerica-east1
REGION=southamerica-east1

gcloud functions deploy $FUNCTION \
  --gen2 \
  --runtime=python39 \
  --memory=512MB \
  --region=$REGION \
  --source=./ports \
  --entry-point=$ENTRY_POINT \
  --trigger-bucket=$TRIGGER_BUCKET \
  --allow-unauthenticated \
  --set-secrets=$SECRETS
