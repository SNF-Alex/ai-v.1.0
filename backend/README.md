# Backend README - Thespis AI Assistant

## Overview
Secure FastAPI backend for the Thespis AI Assistant with Google Cloud integration.

## Features
- ✅ FastAPI REST API
- ✅ Google Cloud Storage integration
- ✅ Content moderation & safety filtering
- ✅ Email verification for developer access
- ✅ Rate limiting
- ✅ Comprehensive logging
- ✅ Conversation storage & review system

## Project Structure
```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── ai_core/               # Core AI logic
│   ├── config.py          # Configuration settings
│   ├── logger.py          # Logging setup
│   ├── ai_handler.py      # AI chat handler
│   ├── moderator.py       # Content moderation
│   ├── cloud_storage.py   # Google Cloud Storage
│   ├── email_service.py   # Email verification
│   ├── middleware.py      # Request middleware
│   └── routes/            # API routes
│       ├── chat.py        # Chat endpoints
│       └── dev_moderation.py  # Developer moderation
├── conversations/         # Stored conversations
├── flagged_questions/     # Flagged content
├── good_responses/        # Approved responses
├── bad_responses/         # Rejected responses
└── logs/                  # Application logs
```

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

### 3. Set Up Google Cloud (Optional but Recommended)

#### Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the following APIs:
   - Cloud Storage API
   - Secret Manager API
   - Cloud Logging API

#### Create a Storage Bucket
```bash
gsutil mb -p your-project-id -l us-central1 gs://your-bucket-name
```

#### Set up Service Account
```bash
gcloud iam service-accounts create thespis-backend
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:thespis-backend@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=thespis-backend@your-project-id.iam.gserviceaccount.com
```

#### Set Environment Variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### 4. Configure Allowed Developer Emails
Create `allowed_emails.txt` and add authorized emails (one per line):
```
developer@example.com
admin@example.com
```

### 5. Run the Server
```bash
# Development mode
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Chat Endpoints
- `POST /api/chat` - Send message to AI
- `GET /api/health` - Health check

### Developer Moderation Endpoints
- `POST /api/dev/verify-email` - Request verification code
- `POST /api/dev/verify-code` - Verify code
- `GET /api/dev/conversations` - Get all conversations
- `POST /api/dev/review-conversation` - Review conversation

## Security Features

### Content Moderation
- Profanity filtering
- Dangerous content detection
- Pattern-based flagging
- Length limits

### Rate Limiting
- 10 requests per minute (configurable)
- IP-based tracking

### Developer Access
- Email verification required
- 8-digit code sent via SendGrid
- 10-minute expiration
- Authorized email list

## Deployment to Google Cloud

### Deploy with Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/your-project-id/thespis-backend

# Deploy
gcloud run deploy thespis-backend \
  --image gcr.io/your-project-id/thespis-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Environment Variables in Cloud Run
Set all required environment variables in Cloud Run:
```bash
gcloud run services update thespis-backend \
  --update-env-vars GCP_PROJECT_ID=your-project-id,GCP_BUCKET_NAME=your-bucket
```

## Testing

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, Thespis!", "session_id": "test-123"}'
```

### Test Developer Verification
```bash
# Request code
curl -X POST http://localhost:8000/api/dev/verify-email \
  -H "Content-Type: application/json" \
  -d '{"email": "developer@example.com"}'

# Verify code
curl -X POST http://localhost:8000/api/dev/verify-code \
  -H "Content-Type: application/json" \
  -d '{"email": "developer@example.com", "code": "12345678"}'
```

## Monitoring & Logs

Logs are saved to:
- Console (JSON format)
- `logs/` directory
- Google Cloud Logging (if enabled)

## Maintenance

### Backup Conversations
```bash
# Local backup
tar -czf conversations-backup-$(date +%Y%m%d).tar.gz conversations/

# Or use Google Cloud Storage
gsutil -m rsync -r conversations/ gs://your-bucket/backups/conversations/
```

### Review Flagged Content
Access the developer moderation panel at `/devresponse` in your frontend.

## Troubleshooting

### Issue: "Google Cloud credentials not found"
**Solution:** Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable or ensure service account key is properly configured.

### Issue: "SendGrid email not sending"
**Solution:** Verify `SENDGRID_API_KEY` is set and valid. Check SendGrid dashboard for API status.

### Issue: "Rate limit exceeded"
**Solution:** Adjust `RATE_LIMIT_PER_MINUTE` in `.env` or implement user-based rate limiting.

## Next Steps
1. Connect frontend to backend API
2. Configure OpenAI or your AI service
3. Set up Google Cloud project
4. Deploy to production
5. Monitor and improve based on feedback

## Support
For issues or questions, check the main README.md or workflow documentation.
