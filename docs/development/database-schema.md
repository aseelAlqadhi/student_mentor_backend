# Database Schema

This document contains the complete SQL schema for the AI Mentor Backend application.

## Tables

### user_profiles

Stores user profile information and onboarding questionnaire responses.

```sql
-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    challenges_goals TEXT,
    living_situation TEXT,
    guidance_preference TEXT CHECK (guidance_preference IN ('supportive', 'action-oriented', 'analytical', 'empathetic', 'challenge-focused')),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on user_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- Create index on onboarding_completed for faster queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_onboarding_completed ON user_profiles(onboarding_completed);

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

### chat_history

Stores chat messages for different areas (health, career, finance, general).

```sql
-- Create chat_history table
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    area TEXT NOT NULL CHECK (area IN ('health', 'career', 'finance', 'general')),
    message_type TEXT NOT NULL CHECK (message_type IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_area ON chat_history(area);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_area ON chat_history(user_id, area);

-- Enable Row Level Security (RLS)
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own chat history
CREATE POLICY "Users can view own chat history" ON chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat messages" ON chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat messages" ON chat_history
    FOR DELETE USING (auth.uid() = user_id);
```

## Setup Instructions

1. **Access your Supabase Dashboard**
2. **Go to SQL Editor**
3. **Copy and paste the entire schema above**
4. **Run the SQL commands**

## Schema Features

### Security
- **Row Level Security (RLS)** enabled on all tables
- Users can only access their own data
- Automatic user authentication checks

### Performance
- **Indexes** on frequently queried columns
- **Composite indexes** for area-specific queries
- **Unique constraints** to prevent duplicate profiles

### Data Integrity
- **Foreign key constraints** linking to Supabase auth.users
- **Check constraints** ensuring valid enum values
- **Automatic timestamps** for created_at and updated_at

### Automatic Updates
- **Triggers** automatically update the `updated_at` timestamp
- **Default values** for required fields
- **UUID primary keys** for security and scalability

## Usage Examples

### Query user profile
```sql
SELECT * FROM user_profiles WHERE user_id = auth.uid();
```

### Get chat history for specific area
```sql
SELECT * FROM chat_history 
WHERE user_id = auth.uid() 
AND area = 'career' 
ORDER BY created_at DESC 
LIMIT 50;
```

### Check onboarding status
```sql
SELECT onboarding_completed FROM user_profiles WHERE user_id = auth.uid();
``` 