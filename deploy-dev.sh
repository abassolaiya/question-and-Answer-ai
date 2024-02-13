#!/usr/bin/env sh
set -ue
REGISTRY="gcr.io"
PROJECT_NAME="codematic-playground"
IMAGE_NAME="qa_ai"
IMAGE_ENV=${ENV}
IMAGE_TAG=$(git rev-parse --short HEAD)
SERVICE_NAME=${IMAGE_NAME}-${ENV}
IMAGE=${REGISTRY}/${PROJECT_NAME}/${IMAGE_NAME}:${IMAGE_ENV}-${IMAGE_TAG}

echo "Cloud run deployment....................."
echo "Starting deployment of ${IMAGE_NAME} to the ${IMAGE_ENV} environment"

gcloud beta run deploy $SERVICE_NAME --image ${IMAGE} \
  --project $PROJECT_NAME \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
