# 🚦 Rate Limiting System

This document explains the rate limiting system implemented in the Student Mentor Backend.

## 📋 Overview

The rate limiting system protects the API from abuse and ensures fair usage by limiting the number of requests a user can make within a specified time window.

## ⚙️ Configuration

### **Default Settings**
```python
# Default rate limit configuration
RATE_LIMIT = {
    "requests_per_minute": 60,      # 60 requests per minute
    "time_window_seconds": 60,      # 1 minute window
    "burst_limit": 10               # Allow 10 requests in burst
}
```

### **Environment Variables**
```bash
# Optional: Override default settings
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_TIME_WINDOW_SECONDS=60
RATE_LIMIT_BURST_LIMIT=10
```

## 🔧 How It Works

### **1. Request Tracking**
- Each request is tracked by user identifier (IP address or user ID)
- Timestamps are stored in memory for rate limit calculation
- Automatic cleanup of expired entries

### **2. Rate Limit Calculation**
- Counts requests within the time window
- Applies burst limit for rapid requests
- Returns appropriate HTTP status codes

### **3. Response Headers**
When rate limited, the response includes:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 30
```

## 📡 API Endpoints

### **Get Rate Limit Status**
```http
GET /auth/rate-limit/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": "user123",
  "requests_made": 45,
  "requests_allowed": 60,
  "time_window_seconds": 60,
  "reset_time": "2024-01-01T12:00:00Z"
}
```

### **Reset User Rate Limit**
```http
POST /auth/rate-limit/reset
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Rate limit reset successfully",
  "user_id": "user123"
}
```

### **Get All Rate Limit Status (Admin)**
```http
GET /auth/rate-limit/all
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "active_users": [
    {
      "user_id": "user123",
      "requests_made": 45,
      "requests_allowed": 60,
      "time_window_seconds": 60
    }
  ],
  "total_active_users": 1
}
```

### **Update Rate Limit Configuration**
```http
PUT /auth/rate-limit/config
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "requests_per_minute": 100,
  "time_window_seconds": 60,
  "burst_limit": 20
}
```

## 🚨 Error Responses

### **Rate Limit Exceeded**
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded",
  "rate_limit": 60,
  "time_window_seconds": 60,
  "retry_after": 30
}
```

### **Configuration Error**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "detail": "Invalid rate limit configuration",
  "errors": ["requests_per_minute must be positive"]
}
```

## 🧪 Testing Rate Limiting

### **1. Test Basic Rate Limiting**
```bash
# Make multiple requests quickly
for i in {1..70}; do
  curl -H "Authorization: Bearer YOUR_TOKEN" \
       http://localhost:8000/auth/me
done
```

### **2. Test Rate Limit Status**
```bash
# Check current rate limit status
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/auth/rate-limit/status
```

### **3. Test Rate Limit Reset**
```bash
# Reset rate limit for user
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/auth/rate-limit/reset
```

### **4. Test Configuration Update**
```bash
# Update rate limit settings
curl -X PUT \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"requests_per_minute": 100, "time_window_seconds": 60}' \
     http://localhost:8000/auth/rate-limit/config
```

## 🔍 Monitoring

### **Rate Limit Metrics**
- Track rate limit violations
- Monitor API usage patterns
- Identify potential abuse

### **Logging**
Rate limit events are logged with:
- User identifier
- Request count
- Timestamp
- Action taken (allowed/blocked)

## 🛡️ Security Considerations

### **1. IP-based vs User-based**
- **Unauthenticated requests**: Limited by IP address
- **Authenticated requests**: Limited by user ID
- **Admin endpoints**: Higher limits or bypass

### **2. Burst Protection**
- Prevents rapid-fire requests
- Configurable burst limits
- Smooths out traffic spikes

### **3. Memory Management**
- Automatic cleanup of expired entries
- Memory-efficient storage
- Configurable cleanup intervals

## 🔧 Customization

### **Per-Endpoint Limits**
```python
# Different limits for different endpoints
ENDPOINT_LIMITS = {
    "/auth/signin": {"requests_per_minute": 5},    # Stricter for login
    "/chat": {"requests_per_minute": 30},          # Moderate for chat
    "/profiles": {"requests_per_minute": 100}      # Higher for profiles
}
```

### **User Tier Limits**
```python
# Different limits for user tiers
USER_TIER_LIMITS = {
    "free": {"requests_per_minute": 30},
    "premium": {"requests_per_minute": 100},
    "enterprise": {"requests_per_minute": 500}
}
```

## 🚀 Best Practices

### **1. Gradual Rollout**
- Start with generous limits
- Monitor usage patterns
- Adjust based on actual usage

### **2. Clear Communication**
- Inform users about rate limits
- Provide clear error messages
- Include retry-after headers

### **3. Monitoring**
- Track rate limit violations
- Monitor for abuse patterns
- Adjust limits as needed

---

*This rate limiting system provides robust protection while maintaining good user experience.* 