# 🎓 Student Mentor Backend

A FastAPI-based backend for an AI mentorship web application that provides personalized guidance to students across health, career, and finance areas.

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Environment Setup**
```bash
cp env.example .env
# Edit .env with your Supabase and Gemini API credentials
```

### **3. Database Setup**
Run the SQL schema in your Supabase database (see [Database Schema](docs/development/database-schema.md))

### **4. Start the Application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📡 Core Features

- **User Authentication** - Registration, login, and profile management
- **Multi-Area Chat** - Separate conversations for health, career, and finance
- **AI Personalization** - Context-aware responses based on user profile
- **Rate Limiting** - API protection and fair usage
- **Onboarding System** - Personalized questionnaire for new users

## 📖 Documentation

- **[Getting Started](docs/README.md)** - Complete setup and usage guide
- **[API Reference](docs/api/overview.md)** - All available endpoints
- **[Project Structure](docs/development/project-structure.md)** - Code organization
- **[Maintenance](docs/maintenance/)** - Rate limiting, AI persona, and onboarding management

## 🛠️ Development

- **API Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Project Structure**: See [Project Structure](docs/development/project-structure.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.