# 🚀 Getting Started

This guide will help you set up and run the Student Mentor Backend application.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed on your system
- **Supabase account** with a project created
- **Google Gemini API key** for AI functionality
- **Git** for version control

## 🛠️ Installation

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd student_mentor_backend
```

### **2. Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### **1. Environment Variables**
```bash
# Copy the example environment file
cp env.example .env
```

Edit `.env` with your credentials:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key
```

### **2. Supabase Setup**

1. **Create a Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Note your project URL and anon key

2. **Set Up Database Schema**:
   - Go to your Supabase project dashboard
   - Navigate to SQL Editor
   - Run the schema from [Database Schema](development/database-schema.md)

### **3. Google Gemini API**

1. **Get API Key**:
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Add it to your `.env` file

## 🗄️ Database Setup

Run the following SQL in your Supabase SQL Editor:

```sql
-- Create user_profiles table
CREATE TABLE user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    challenges_goals TEXT,
    living_situation TEXT,
    guidance_preference TEXT,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_history table
CREATE TABLE chat_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    area TEXT NOT NULL,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own chat history" ON chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat messages" ON chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat history" ON chat_history
    FOR DELETE USING (auth.uid() = user_id);

-- Create indexes
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_area ON chat_history(area);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);
```

## 🚀 Running the Application

### **Development Mode**
```bash
uvicorn app.main:app --reload
```

### **Production Mode**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Using Docker**
```bash
# Build the image
docker build -t student-mentor-backend .

# Run the container
docker run -p 8000:8000 student-mentor-backend
```

## ✅ Verification

### **1. Health Check**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### **2. API Documentation**
Visit `http://localhost:8000/docs` in your browser to see the interactive API documentation.

### **3. Test User Registration**
```bash
curl -X POST "http://localhost:8000/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpassword123"
     }'
```

## 🔧 Troubleshooting

### **Common Issues**

1. **Import Errors**:
   ```bash
   # Ensure you're in the virtual environment
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Database Connection Issues**:
   - Verify your Supabase URL and key in `.env`
   - Check that the database schema is properly set up

3. **AI Integration Issues**:
   - Verify your Gemini API key is correct
   - Check API key permissions and quotas

4. **Port Already in Use**:
   ```bash
   # Use a different port
   uvicorn app.main:app --reload --port 8001
   ```

### **Environment Variables**

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_ANON_KEY` | Your Supabase anon key | Yes |
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |

## 📚 Next Steps

- **API Reference**: See [API Overview](api/overview.md) for all available endpoints
- **Project Structure**: Understand the codebase in [Project Structure](development/project-structure.md)
- **Maintenance**: Learn about [Rate Limiting](maintenance/rate-limiting.md) and [AI Persona Management](maintenance/ai-persona.md)

## 🆘 Support

If you encounter issues:

1. Check the [Troubleshooting](maintenance/troubleshooting.md) guide
2. Review the [API Documentation](api/overview.md)
3. Create an issue in the repository

---

*You're now ready to start developing with the Student Mentor Backend!* 