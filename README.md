# AI Mentor Backend

A FastAPI backend for an AI mentorship web application with Supabase authentication and Gemini AI integration.

## 🚀 Features

- 🔐 **Supabase Authentication**: Complete user registration, login, and session management
- 🤖 **AI Mentorship**: Integration with Google's Gemini AI for educational conversations
- ⚡ **FastAPI**: High-performance async API framework
- 🚀 **Rate Limiting**: Built-in request throttling for API protection
- 📚 **Auto-generated Docs**: Interactive API documentation with Swagger UI
- 🎯 **Email Confirmation**: Secure email verification flow
- 🛡️ **JWT Token Validation**: Secure token-based authentication

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI
- **Authentication**: Supabase Auth
- **Database**: Supabase (PostgreSQL)
- **AI Integration**: Google Gemini API
- **Deployment**: Docker + Google Cloud Run
- **Token Validation**: JWT with PyJWT

## 📋 Prerequisites

- Python 3.8+
- Supabase project with URL and anon key
- Google Gemini API key

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/student_mentor_backend.git
cd student_mentor_backend
```

### 2. Set Up Environment Variables
Copy the example environment file and fill in your credentials:
```bash
cp env.example .env
```

Edit `.env` with your actual values:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Development Server
```bash
uvicorn app.main:app --reload
```

### 5. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Auth Callback**: http://localhost:8000/auth-callback

## 📚 API Endpoints

### Authentication
- `POST /auth/signup` - Register a new user
- `POST /auth/signin` - Sign in existing user
- `POST /auth/signout` - Sign out current user
- `GET /auth/me` - Get current user information
- `GET /auth/callback` - Handle email confirmation redirects

### Chat
- `POST /chat` - Send a message to the AI mentor (supports both authenticated and unauthenticated users)
- `GET /` - API health check
- `GET /health` - Detailed health status

## 🔧 Usage Examples

### User Registration
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "securepassword123"}'
```

### User Login
```bash
curl -X POST "http://localhost:8000/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "securepassword123"}'
```

### Chat with AI Mentor (Authenticated)
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I need help with my math homework"}'
```

### Chat with AI Mentor (Unauthenticated)
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, can you help me study?"}'
```

## 📁 Project Structure

```
student_mentor_backend/
├── app/
│   ├── auth/
│   │   ├── dependencies.py    # Authentication dependencies
│   │   ├── routes.py          # Auth API endpoints
│   │   └── throttling.py      # Rate limiting
│   ├── main.py               # FastAPI application
│   ├── models.py             # Pydantic models
│   ├── supabase.py           # Supabase client & utilities
│   └── gemini.py             # AI integration
├── public/
│   └── auth-callback.html    # Email confirmation page
├── prompts/
│   └── system_prompt.md      # AI mentor instructions
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── env.example              # Environment variables template
└── README.md               # This file
```

## 🔐 Authentication Flow

1. **User Registration**: User signs up with email/password
2. **Email Confirmation**: User receives confirmation email
3. **Email Verification**: User clicks link, gets redirected to callback page
4. **Token Generation**: Access token is generated for API access
5. **API Access**: User can now access protected endpoints

## 🚀 Deployment

### Docker
```bash
docker build -t ai-mentor-backend .
docker run -p 8000:8000 ai-mentor-backend
```

### Environment Variables for Production
Make sure to set all required environment variables in your deployment environment:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `GEMINI_API_KEY`

## 👥 Authors

👤 **Aseel**

- GitHub: [@cluab](https://github.com/Cluab)
- LinkedIn: [Ebrahim Al-Yousefi](https://www.linkedin.com/in/ebrahim-alyousefi/)

👤 **Ebrahim Suhail Al-Yousefi**

- GitHub: [@cluab](https://github.com/Cluab)
- LinkedIn: [Ebrahim Al-Yousefi](https://www.linkedin.com/in/ebrahim-alyousefi/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

Copyright (c) 2024 AI Mentor Backend. This software and associated documentation 
files are the proprietary and confidential information of AI Mentor Backend. 
The Software is protected by copyright laws and international copyright treaties.

For licensing inquiries, please contact: [ebra.alyousefi@gmail.com]

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [Supabase](https://supabase.com/) for authentication and database
- [Google Gemini](https://ai.google.dev/) for AI capabilities