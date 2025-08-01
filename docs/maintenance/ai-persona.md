# 🤖 AI Persona Management

This document explains how to manage and customize the AI mentor's persona and behavior.

## 📋 Overview

The AI mentor uses a combination of system prompts and user context to provide personalized guidance. The persona can be customized for different areas (health, career, finance) and user preferences.

## 🎭 Current Persona System

### **Base System Prompt**
Located in: `app/features/chat/ai/system_prompt.md`

The base prompt defines the AI's core personality and role:
- **Role**: Student mentor and life coach
- **Tone**: Supportive, encouraging, and professional
- **Approach**: Evidence-based guidance with practical advice

### **Area-Specific Prompts**
Located in: `app/features/chat/ai/prompts.py`

Different personas for different life areas:

#### **Health Mentor**
- Focus on physical and mental well-being
- Encourages healthy habits and self-care
- Provides stress management techniques

#### **Career Mentor**
- Professional development guidance
- Skill-building recommendations
- Networking and job search strategies

#### **Finance Mentor**
- Budgeting and financial planning
- Investment education for beginners
- Debt management strategies

## 🔧 Customizing the AI Persona

### **1. Modify Base System Prompt**

Edit `app/features/chat/ai/system_prompt.md`:

```markdown
# AI Mentor System Prompt

You are an experienced student mentor and life coach specializing in helping students navigate their academic and personal challenges.

## Your Role
- Provide personalized guidance based on student's unique situation
- Offer practical, actionable advice
- Maintain a supportive and encouraging tone
- Use evidence-based approaches

## Your Approach
- Ask clarifying questions when needed
- Provide step-by-step guidance
- Share relevant resources and tools
- Encourage self-reflection and growth

## Your Personality
- Warm and approachable
- Professional yet friendly
- Patient and understanding
- Solution-oriented
```

### **2. Update Area-Specific Prompts**

Edit `app/features/chat/ai/prompts.py`:

```python
# Health-specific prompt
HEALTH_SYSTEM_PROMPT = """
You are a health and wellness mentor for students.

Focus Areas:
- Physical health and fitness
- Mental health and stress management
- Sleep hygiene and energy management
- Nutrition and healthy eating habits

Guidance Style:
- Encourage sustainable lifestyle changes
- Provide evidence-based health tips
- Address common student health challenges
- Promote work-life balance
"""

# Career-specific prompt
CAREER_SYSTEM_PROMPT = """
You are a career development mentor for students.

Focus Areas:
- Academic and professional goal setting
- Skill development and learning strategies
- Internship and job search guidance
- Networking and professional relationships

Guidance Style:
- Help students identify their strengths
- Provide actionable career advice
- Share industry insights and trends
- Encourage continuous learning
"""
```

### **3. Add New Guidance Styles**

In `app/shared/models.py`, you can add new guidance preferences:

```python
class OnboardingRequest(BaseModel):
    challenges_goals: str
    living_situation: str
    guidance_preference: Literal[
        "supportive", 
        "action-oriented", 
        "analytical", 
        "empathetic", 
        "challenge-focused",
        "mentor-style",      # New style
        "coach-style"        # New style
    ]
```

Then update the prompts to handle these new styles.

## 🎯 User Context Integration

### **How User Context is Used**

The AI combines:
1. **Base system prompt** (core personality)
2. **Area-specific prompt** (domain expertise)
3. **User context** (personalized information)

### **User Context Sources**

From onboarding questionnaire:
- **Challenges/Goals**: What the student wants to achieve
- **Living Situation**: Current circumstances and support system
- **Guidance Preference**: How they prefer to receive advice

### **Context Format**

```python
# Example user context
user_context = "Student's main challenges/goals: Improve time management and work-life balance | Living situation and support system: Living in dorm with roommates, family support available | Preferred guidance style: action-oriented"
```

## 🔄 Updating Persona in Production

### **1. Development Process**
1. Modify prompts in development environment
2. Test with different user scenarios
3. Gather feedback on AI responses
4. Iterate and refine

### **2. Deployment**
1. Update prompt files
2. Restart the application
3. Monitor AI responses
4. Collect user feedback

### **3. A/B Testing**
Consider implementing A/B testing for different personas:
- Test different prompt variations
- Measure user satisfaction
- Track engagement metrics

## 📊 Monitoring AI Performance

### **Key Metrics to Track**
- **User satisfaction** with AI responses
- **Engagement rates** in different areas
- **Completion rates** for suggested actions
- **User feedback** and ratings

### **Feedback Collection**
- In-app feedback buttons
- User surveys
- Chat session reviews
- Support ticket analysis

## 🛠️ Advanced Customization

### **1. Dynamic Persona Selection**

Based on user behavior and preferences:

```python
def select_persona(user_profile, chat_history, current_area):
    """Dynamically select the most appropriate persona."""
    
    # Consider user's guidance preference
    if user_profile.guidance_preference == "analytical":
        return ANALYTICAL_PROMPT
    
    # Consider chat history patterns
    if is_struggling_user(chat_history):
        return SUPPORTIVE_PROMPT
    
    # Consider current area
    return get_area_prompt(current_area)
```

### **2. Seasonal or Contextual Prompts**

```python
# Holiday-specific prompts
HOLIDAY_PROMPTS = {
    "exam_season": "Focus on stress management and study strategies",
    "summer_break": "Emphasize personal development and planning",
    "new_semester": "Help with goal setting and organization"
}
```

### **3. Cultural Sensitivity**

```python
# Culture-aware prompts
CULTURAL_PROMPTS = {
    "collectivist": "Emphasize community and family support",
    "individualist": "Focus on personal achievement and independence"
}
```

## 🚀 Best Practices

### **1. Consistency**
- Maintain consistent personality across areas
- Use similar tone and approach
- Avoid conflicting advice

### **2. Personalization**
- Leverage user context effectively
- Adapt to user's communication style
- Provide relevant examples and resources

### **3. Safety**
- Include safety disclaimers for health advice
- Provide professional resources when needed
- Avoid giving medical or legal advice

### **4. Continuous Improvement**
- Regularly review and update prompts
- Gather user feedback
- Monitor AI response quality
- Stay updated with best practices

## 🔍 Troubleshooting

### **Common Issues**

1. **Inconsistent Responses**
   - Check prompt consistency
   - Review user context integration
   - Test with different scenarios

2. **Poor User Engagement**
   - Analyze user feedback
   - Review prompt tone and approach
   - Consider A/B testing different versions

3. **Inappropriate Responses**
   - Add safety filters
   - Review and update prompts
   - Implement response validation

---

*Regular updates and monitoring ensure the AI mentor provides the best possible guidance to students.* 