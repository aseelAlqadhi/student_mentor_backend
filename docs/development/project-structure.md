# 🏗️ Project Structure

This document explains the organization and architecture of the Student Mentor Backend codebase.

## 📁 Directory Structure

```
student_mentor_backend/
├── app/                          # Main application package
│   ├── api/v1/                   # API Layer (Version 1)
│   │   ├── auth/                 # Authentication endpoints
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py   # Auth dependencies
│   │   │   ├── routes.py         # Auth routes
│   │   │   └── throttling.py     # Rate limiting
│   │   ├── chat/                 # Chat endpoints
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # Chat routes
│   │   ├── onboarding/           # Onboarding endpoints
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # Onboarding routes
│   │   ├── profiles/             # Profile endpoints
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # Profile routes
│   │   └── __init__.py           # API v1 router
│   ├── features/                 # Business Logic Layer
│   │   ├── authentication/       # Auth feature
│   │   │   └── __init__.py
│   │   ├── chat/                 # Chat feature
│   │   │   ├── ai/               # AI integration
│   │   │   │   ├── __init__.py
│   │   │   │   ├── gemini.py     # Gemini AI client
│   │   │   │   ├── prompts.py    # System prompts
│   │   │   │   └── system_prompt.md
│   │   │   ├── __init__.py
│   │   │   └── services.py       # Chat services
│   │   ├── onboarding/           # Onboarding feature
│   │   │   └── __init__.py
│   │   ├── profiles/             # Profiles feature
│   │   │   ├── __init__.py
│   │   │   └── services.py       # Profile services
│   │   └── __init__.py
│   ├── infrastructure/           # Infrastructure Layer
│   │   └── external/             # External services
│   │       ├── __init__.py
│   │       └── supabase.py       # Supabase client
│   ├── shared/                   # Shared utilities
│   │   ├── __init__.py
│   │   ├── base.py               # Base classes
│   │   └── models.py             # Pydantic models
│   └── main.py                   # Application entry point
├── docs/                         # Documentation
├── prompts/                      # Legacy prompts (moved to features/chat/ai/)
├── public/                       # Static files
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
└── README.md                     # Project overview
```

## 🏛️ Architecture Overview

### **1. API Layer (`app/api/v1/`)**
- **Purpose**: HTTP endpoints and request/response handling
- **Responsibilities**: 
  - Route definitions
  - Request validation
  - Response formatting
  - Authentication middleware
- **Pattern**: RESTful API design

### **2. Features Layer (`app/features/`)**
- **Purpose**: Business logic and domain services
- **Responsibilities**:
  - Core business operations
  - Data processing
  - Feature-specific services
- **Pattern**: Feature-based organization

### **3. Infrastructure Layer (`app/infrastructure/`)**
- **Purpose**: External services and infrastructure concerns
- **Responsibilities**:
  - Database connections
  - External API clients
  - Configuration management
- **Pattern**: Dependency injection

### **4. Shared Layer (`app/shared/`)**
- **Purpose**: Common utilities and models
- **Responsibilities**:
  - Data models (Pydantic)
  - Base classes
  - Utility functions
- **Pattern**: Shared components

## 🔄 Data Flow

```
Client Request → API Layer → Features Layer → Infrastructure Layer → Database
                ↓              ↓                ↓
            Validation    Business Logic    External Services
                ↓              ↓                ↓
            Response ← Formatted Data ← Processed Data
```

## 🎯 Key Design Principles

### **1. Separation of Concerns**
- API layer handles HTTP concerns
- Features layer handles business logic
- Infrastructure layer handles external dependencies

### **2. Feature-Based Organization**
- Related functionality is grouped together
- Easy to find and modify specific features
- Reduces coupling between features

### **3. Dependency Inversion**
- High-level modules don't depend on low-level modules
- Both depend on abstractions
- Easy to test and mock

### **4. API Versioning**
- Version 1 structure ready for future updates
- Backward compatibility support
- Clear migration path

## 🚀 Benefits

### **Maintainability**
- Clear file organization
- Easy to locate code
- Reduced cognitive load

### **Scalability**
- Easy to add new features
- Independent development possible
- Clear boundaries between modules

### **Testability**
- Isolated components
- Easy to mock dependencies
- Clear interfaces

### **Team Development**
- Multiple developers can work independently
- Clear ownership of code areas
- Reduced merge conflicts

## 📝 Naming Conventions

- **Files**: snake_case (e.g., `user_profile.py`)
- **Classes**: PascalCase (e.g., `UserProfile`)
- **Functions**: snake_case (e.g., `get_user_profile`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- **Directories**: snake_case (e.g., `user_management`)

## 🔧 Adding New Features

1. **Create API endpoints** in `app/api/v1/[feature]/`
2. **Add business logic** in `app/features/[feature]/`
3. **Update models** in `app/shared/models.py` if needed
4. **Add tests** in `tests/[feature]/`
5. **Update documentation** in `docs/`

---

*This structure follows industry best practices and makes the codebase easy to understand, maintain, and scale.* 