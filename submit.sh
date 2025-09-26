#!/bin/bash

# ==============================================================================
# BASH SCRIPT TO BUILD AND DEPLOY A DOCKER CONTAINER TO GOOGLE CLOUD RUN
# ==============================================================================
#
# This script automates the following steps:
#   1. Builds a Docker image from the local Dockerfile.
#   2. Pushes the image to Google Artifact Registry.
#   3. Deploys the image to Google Cloud Run, assigning a secure service
#      account identity for authentication with other Google Cloud services.
#
# USAGE:
#   1. Make sure you have the following installed:
#      - Google Cloud SDK (gcloud): `gcloud auth login`
#      - Docker
#   2. Ensure your user account (the one running this script) has the
#      required IAM roles on the project:
#      - Artifact Registry Writer (`roles/artifactregistry.writer`)
#      - Cloud Run Admin (`roles/run.admin`)
#      - Service Account User (`roles/iam.serviceAccountUser`)
#   3. Ensure the resources below have been created (one-time setup):
#      - An Artifact Registry repository.
#      - A runtime service account for the Cloud Run service.
#      - A secret in Secret Manager for the Flask secret key.
#   4. Ensure the runtime service account has the necessary IAM roles to
#      access other services (e.g., `roles/storage.objectAdmin` for GCS).
#   5. Fill in the variables in the "USER-CONFIGURABLE VARIABLES" section below.
#   6. Make the script executable: `chmod +x deploy.sh`
#   7. Run the script from your project root: `./deploy.sh`
#
# ==============================================================================

# --- SCRIPT CONFIGURATION ---

# Exit immediately if a command exits with a non-zero status.
set -e

# --- USER-CONFIGURABLE VARIABLES ---

# GCP Project ID.
PROJECT_ID="prj-hackathon-team2"

# The GCP region for your resources.
REGION="europe-west3"

# The name of your Artifact Registry repository.
REPOSITORY_NAME="hr-chatbot-repo"

# The name of the container image.
IMAGE_NAME="hr-chatbot-app"

# The name of your Cloud Run service.
SERVICE_NAME="hr-chatbot-service"

# The email of the service account your Cloud Run service will run as.
# This service account MUST already exist and have the required permissions
# (e.g., to access Cloud Storage and Vertex AI).
RUNTIME_SERVICE_ACCOUNT_EMAIL="vertex-search@prj-hackathon-team2.iam.gserviceaccount.com"

# The location for Vertex AI/GenAI services.
# NOTE: The Cloud Run service is in `europe-west3`, but Vertex may need a different one.
VERTEX_AI_LOCATION="europe-west4"

# --- SCRIPT LOGIC (NO NEED TO EDIT BELOW THIS LINE) ---

# Step 0: Ensure Artifact Registry repository exists.
echo "--> Step 0/5: Checking for Artifact Registry repository..."
if ! gcloud artifacts repositories describe "${REPOSITORY_NAME}" --location="${REGION}" --project="${PROJECT_ID}" &> /dev/null; then
  echo "--> Repository '${REPOSITORY_NAME}' not found. Creating it now..."
  gcloud artifacts repositories create "${REPOSITORY_NAME}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Docker repository for ${SERVICE_NAME}" \
    --project="${PROJECT_ID}"
  echo "--> Repository created."
else
  echo "--> Repository '${REPOSITORY_NAME}' already exists."
fi
echo

# Construct the full image URL in Artifact Registry.
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest"

echo "===================================================="
echo "          CLOUD RUN DEPLOYMENT SCRIPT"
echo "===================================================="
echo "Project ID:               ${PROJECT_ID}"
echo "Region:                   ${REGION}"
echo "Cloud Run Service Name:   ${SERVICE_NAME}"
echo "Image URL:                ${IMAGE_URL}"
echo "Runtime Service Account:  ${RUNTIME_SERVICE_ACCOUNT_EMAIL}"
echo "===================================================="
echo

# Step 1: Build the Docker image locally.
echo "--> Step 1/5: Building Docker image..."
# The --no-cache flag is good for ensuring a fresh build, but removing it
# will leverage Docker's layer caching and can significantly speed up subsequent builds.
docker build -t "${IMAGE_URL}" .
echo "--> Build complete."
echo

# Step 2: Configure Docker to authenticate with Google Cloud.
echo "--> Step 2/5: Configuring Docker authentication..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
echo "--> Authentication configured."
echo

# Step 3: Push the image to Artifact Registry.
echo "--> Step 3/5: Pushing image to Artifact Registry..."
docker push "${IMAGE_URL}"
echo "--> Push complete."
echo

# Step 4: Deploy the image to Cloud Run using the recommended best practices.
# - The '--service-account' flag assigns an identity to the service, which is
#   the secure way for it to authenticate with other Google Cloud APIs.
# - The '--allow-unauthenticated' flag makes the service public. Remove it
#   if you want an authenticated (private) service.
echo "--> Step 4/5: Deploying image to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_URL}" \
  --project "$PROJECT_ID" \
  --region "${REGION}" \
  --platform "managed" \
  --service-account "${RUNTIME_SERVICE_ACCOUNT_EMAIL}" \
  --timeout=600s \
  --memory=1Gi \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${VERTEX_AI_LOCATION},ENV=dev" \
  --allow-unauthenticated

echo
echo "===================================================="
echo "✅ Deployment successful!"
echo "Your service is available at the URL provided above."
echo "===================================================="