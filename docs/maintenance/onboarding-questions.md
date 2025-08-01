# 📝 Onboarding Questions Management

This document explains how to modify and manage the onboarding questionnaire that new students complete when they first use the application.

## 📋 Overview

The onboarding questionnaire collects essential information about students to personalize their AI mentor experience. This data is stored in the user profile and used to enhance AI responses.

## 🎯 Current Questions

### **Question 1: Challenges and Goals**
```
What are your biggest challenges or goals right now across health, career, and finances? 
Be as specific as possible about what you're trying to achieve or overcome.
```

**Purpose**: Understand the student's primary concerns and objectives
**Data Field**: `challenges_goals` in user profile
**Usage**: Helps AI provide relevant and targeted advice

### **Question 2: Living Situation**
```
What's your current living situation and support system? 
(e.g., studying abroad, living independently, family support available, etc.)
```

**Purpose**: Understand the student's current circumstances and available resources
**Data Field**: `living_situation` in user profile
**Usage**: Helps AI provide contextually appropriate guidance

### **Question 3: Guidance Preference**
```
How do you prefer to receive guidance?
```

**Options**:
- `supportive` - Encouraging and gentle approach
- `action-oriented` - Direct and practical advice
- `analytical` - Detailed explanations and analysis
- `empathetic` - Understanding and emotional support
- `challenge-focused` - Motivational and pushing boundaries

**Purpose**: Personalize the AI's communication style
**Data Field**: `guidance_preference` in user profile
**Usage**: Adjusts AI tone and approach

## 🔧 Modifying Questions

### **1. Update Question Text**

Edit `app/api/v1/onboarding/routes.py`:

```python
@router.get("/questions")
async def get_onboarding_questions():
    """Get the onboarding questions for new users."""
    return {
        "questions": [
            {
                "id": "challenges_goals",
                "question": "What are your biggest challenges or goals right now across health, career, and finances? Be as specific as possible about what you're trying to achieve or overcome.",
                "type": "text",
                "required": True
            },
            {
                "id": "living_situation", 
                "question": "What's your current living situation and support system? (e.g., studying abroad, living independently, family support available, etc.)",
                "type": "text",
                "required": True
            },
            {
                "id": "guidance_preference",
                "question": "How do you prefer to receive guidance?",
                "type": "select",
                "options": [
                    "supportive",
                    "action-oriented", 
                    "analytical",
                    "empathetic",
                    "challenge-focused"
                ],
                "required": True
            }
        ]
    }
```

### **2. Add New Questions**

To add a new question:

1. **Update the questions endpoint**:
```python
{
    "id": "academic_level",
    "question": "What's your current academic level?",
    "type": "select", 
    "options": ["undergraduate", "graduate", "postgraduate"],
    "required": True
}
```

2. **Update the Pydantic model** in `app/shared/models.py`:
```python
class OnboardingRequest(BaseModel):
    challenges_goals: str
    living_situation: str
    guidance_preference: str
    academic_level: str  # New field
```

3. **Update the database schema**:
```sql
ALTER TABLE user_profiles 
ADD COLUMN academic_level TEXT;
```

4. **Update the profile service** in `app/features/profiles/services.py`:
```python
async def update_user_profile(user_id: str, onboarding_data: OnboardingRequest) -> UserProfile:
    update_data = {
        "challenges_goals": onboarding_data.challenges_goals,
        "living_situation": onboarding_data.living_situation,
        "guidance_preference": onboarding_data.guidance_preference,
        "academic_level": onboarding_data.academic_level,  # New field
        "onboarding_completed": True,
        "updated_at": datetime.utcnow().isoformat()
    }
    # ... rest of the function
```

### **3. Modify Question Types**

#### **Text Questions**
```python
{
    "id": "personal_goals",
    "question": "What are your personal goals for this semester?",
    "type": "text",
    "required": True,
    "max_length": 500
}
```

#### **Select Questions**
```python
{
    "id": "study_style",
    "question": "What's your preferred study style?",
    "type": "select",
    "options": ["visual", "auditory", "kinesthetic", "reading/writing"],
    "required": True
}
```

#### **Multi-select Questions**
```python
{
    "id": "interests",
    "question": "What areas interest you most? (Select all that apply)",
    "type": "multiselect",
    "options": ["technology", "health", "finance", "arts", "sports"],
    "required": False
}
```

#### **Scale Questions**
```python
{
    "id": "stress_level",
    "question": "How would you rate your current stress level?",
    "type": "scale",
    "min": 1,
    "max": 10,
    "labels": {
        "1": "Very Low",
        "5": "Moderate", 
        "10": "Very High"
    },
    "required": True
}
```

## 🎨 Question Design Best Practices

### **1. Clarity and Simplicity**
- Use clear, simple language
- Avoid jargon and complex terms
- Keep questions concise but specific

### **2. Logical Flow**
- Start with general questions
- Progress to more specific ones
- Group related questions together

### **3. User Experience**
- Don't ask too many questions (3-5 is ideal)
- Make optional questions clearly marked
- Provide helpful examples where appropriate

### **4. Data Quality**
- Ask specific, actionable questions
- Avoid leading or biased questions
- Ensure answers will be useful for AI personalization

## 🔄 Question Versioning

### **Handling Question Changes**

When modifying questions for existing users:

1. **Backward Compatibility**: Ensure existing profiles still work
2. **Migration Strategy**: Plan how to handle missing data
3. **User Communication**: Inform users about changes

### **Example Migration**
```python
async def migrate_user_profile(user_id: str):
    """Migrate existing profiles to new question format."""
    profile = await get_user_profile(user_id)
    
    if profile and not hasattr(profile, 'academic_level'):
        # Set default value for new field
        await update_profile_field(user_id, 'academic_level', 'undergraduate')
```

## 📊 Analytics and Insights

### **Question Response Analysis**
- Track completion rates for each question
- Analyze response patterns
- Identify common themes in challenges/goals

### **A/B Testing Questions**
Test different question formulations:
```python
# Version A
"What are your biggest challenges?"

# Version B  
"What specific goals are you working towards?"
```

### **Response Quality Metrics**
- Average response length
- Response completion rates
- User engagement with follow-up questions

## 🛠️ Implementation Examples

### **Adding a New Question Type**

1. **Define the question structure**:
```python
class QuestionConfig(BaseModel):
    id: str
    question: str
    type: Literal["text", "select", "multiselect", "scale"]
    required: bool = True
    options: Optional[List[str]] = None
    max_length: Optional[int] = None
```

2. **Update the questions endpoint**:
```python
@router.get("/questions")
async def get_onboarding_questions():
    questions = [
        QuestionConfig(
            id="challenges_goals",
            question="What are your biggest challenges or goals?",
            type="text",
            required=True,
            max_length=500
        ),
        # ... more questions
    ]
    return {"questions": [q.dict() for q in questions]}
```

### **Conditional Questions**
```python
def get_conditional_questions(user_context):
    """Show different questions based on user context."""
    base_questions = get_base_questions()
    
    if user_context.get("is_international_student"):
        base_questions.append(get_international_student_questions())
    
    return base_questions
```

## 🚀 Future Enhancements

### **1. Dynamic Question Flow**
- Questions that adapt based on previous answers
- Skip irrelevant questions
- Progressive disclosure of complex topics

### **2. Question Validation**
- Real-time validation of responses
- Helpful error messages
- Suggestions for better answers

### **3. Question Analytics**
- Track which questions provide the most value
- Identify questions that users struggle with
- Optimize question order and wording

---

*Well-designed onboarding questions are crucial for providing personalized AI mentorship. Regular review and updates ensure the questions remain relevant and effective.* 