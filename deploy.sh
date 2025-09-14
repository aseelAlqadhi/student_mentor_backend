#!/bin/bash

echo "🚀 Deploying with Google Cloud Secret Manager"
echo "============================================="

# Step 1: Build and push Docker image with fixed Dockerfile
echo "🔨 Building Docker image (this may take a few minutes)..."
gcloud builds submit --tag us-central1-docker.pkg.dev/buzn-472100/student-mentor-backend/student-mentor-backend:latest

# Step 2: Deploy to Cloud Run using your existing secrets
echo "🚀 Deploying to Cloud Run with Secret Manager..."
gcloud run deploy student-mentor-backend \
  --image us-central1-docker.pkg.dev/buzn-472100/student-mentor-backend/student-mentor-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_ANON_KEY=supabase-anon-key:latest,SUPABASE_JWT_SECRET=supabase-jwt-secret:latest,SUPABASE_SERVICE_KEY=supabase-service-key:latest" \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300

# Step 3: Show results
echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "Your API should now be accessible. Getting the URL..."

# Get and display the service URL
SERVICE_URL=$(gcloud run services describe student-mentor-backend --region=us-central1 --format='value(status.url)')
echo "🌐 Your API URL: $SERVICE_URL"
echo ""
echo "Test endpoints:"
echo "• Health check: $SERVICE_URL/health"
echo "• API docs: $SERVICE_URL/docs"
echo "• Root: $SERVICE_URL/"
echo ""
echo "✅ Deployment using Secret Manager completed successfully!"
