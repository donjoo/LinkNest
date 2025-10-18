# OTP-Based Email Verification Implementation Guide

## Overview
This implementation adds OTP-based email verification to the existing Django + React authentication system. Users must verify their email address with a 6-digit code before their account is activated.

## Backend Implementation

### 1. OTP Model (`apps/users/otp_models.py`)
- **Purpose**: Stores OTP codes with expiration, usage tracking, and attempt limits
- **Key Features**:
  - 6-digit secure random codes
  - 10-minute expiration
  - Maximum 3 verification attempts
  - Automatic invalidation of old OTPs
  - Single-use verification

### 2. OTP Serializers (`apps/users/otp_serializers.py`)
- **SendOTPSerializer**: Validates email and generates new OTP
- **VerifyOTPSerializer**: Validates OTP code and user email
- **ResendOTPSerializer**: Handles OTP resend requests
- **OTPStatusSerializer**: Provides OTP status information

### 3. OTP Views (`apps/users/otp_views.py`)
- **SendOTPView**: Generates and sends OTP via email
- **VerifyOTPView**: Verifies OTP and activates user account
- **ResendOTPView**: Resends OTP to user's email
- **otp_status_view**: Returns OTP status (time remaining, attempts)

### 4. Updated Registration Flow (`apps/users/auth_views.py`)
- Modified `RegisterView` to create inactive users
- Automatically generates and sends OTP after registration
- Users must verify email before account activation

### 5. Email Configuration (`config/settings/local.py`)
- Gmail SMTP configuration with app password
- Email: `jodon3262@gmail.com`
- App Password: `vwag twrw qeow ihxl`

## Frontend Implementation

### 1. API Service Updates (`src/services/api.js`)
Added OTP-related API functions:
- `sendOTP(email)`: Send OTP to email
- `verifyOTP(email, code)`: Verify OTP code
- `resendOTP(email)`: Resend OTP
- `getOTPStatus(email)`: Get OTP status

### 2. OTP Verification Component (`src/pages/OTPVerification.jsx`)
- **Features**:
  - 6-digit input fields with auto-focus
  - Real-time countdown timer (10 minutes)
  - Auto-submit when all digits entered
  - Resend functionality with cooldown
  - Error handling and success messages
  - Responsive design matching app theme

### 3. Updated Authentication Flow
- **AuthContext**: Modified registration to handle OTP verification
- **Register Component**: Redirects to OTP verification after successful registration
- **App.jsx**: Added OTP verification route

## API Endpoints

### Registration Flow
1. **POST** `/api/auth/register/`
   - Creates inactive user account
   - Generates and sends OTP
   - Returns user data and OTP info

2. **POST** `/api/auth/verify-otp/`
   - Verifies OTP code
   - Activates user account
   - Returns JWT tokens

3. **POST** `/api/auth/resend-otp/`
   - Resends OTP to user's email
   - Invalidates previous OTP

4. **GET** `/api/auth/otp-status/?email=user@example.com`
   - Returns OTP status information

## Testing Instructions

### 1. Backend Testing
```bash
# Start Django server
cd backend
DATABASE_URL=sqlite:///db.sqlite3 CELERY_BROKER_URL=redis://localhost:6379/0 USE_DOCKER=no python3 manage.py runserver 8001
```

### 2. Frontend Testing
```bash
# Start React development server
cd frontend
npm run dev
```

### 3. Test Registration Flow
1. Navigate to `http://localhost:3000/register`
2. Fill out registration form
3. Submit form - should redirect to OTP verification page
4. Check email for 6-digit verification code
5. Enter code in verification form
6. Should redirect to dashboard upon successful verification

### 4. Test OTP Features
- **Resend OTP**: Click "Didn't receive the code? Resend" after timer expires
- **Invalid Code**: Enter wrong code to test error handling
- **Expired OTP**: Wait 10 minutes and try to verify (should show expired message)
- **Multiple Attempts**: Try wrong code 3 times (should show max attempts exceeded)

## Email Setup

### Gmail App Password Configuration
1. Enable 2-Factor Authentication on Gmail account
2. Generate App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use generated password in Django settings

### Email Template
The system sends a simple text email with:
- User's name (if provided)
- 6-digit verification code
- 10-minute expiration notice
- LinkNest branding

## Security Features

### 1. OTP Security
- Cryptographically secure random number generation
- 6-digit codes (1,000,000 possible combinations)
- 10-minute expiration
- Single-use verification
- Maximum 3 attempts per OTP

### 2. Rate Limiting
- Automatic OTP invalidation on new requests
- Cooldown period for resend functionality
- Attempt tracking and limits

### 3. User Account Security
- Accounts remain inactive until email verification
- JWT tokens only issued after verification
- Secure email delivery via Gmail SMTP

## Database Schema

### OTP Table
```sql
CREATE TABLE users_otp (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users_user(id),
    code VARCHAR(6) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3
);
```

## Error Handling

### Backend Errors
- Invalid email format
- User not found
- OTP expired
- Maximum attempts exceeded
- Invalid OTP code
- Email sending failures

### Frontend Errors
- Network connectivity issues
- Invalid OTP format
- Expired OTP
- Server error responses
- Form validation errors

## Future Enhancements

### Potential Improvements
1. **Email Templates**: HTML email templates with better styling
2. **SMS OTP**: Add SMS as alternative verification method
3. **Rate Limiting**: Implement Redis-based rate limiting
4. **Audit Logging**: Track OTP generation and verification attempts
5. **Custom Expiration**: Configurable OTP expiration times
6. **Multiple OTP Types**: Different OTP types for different actions

### Monitoring
- Track OTP generation rates
- Monitor verification success rates
- Alert on high failure rates
- Log suspicious activity patterns

## Troubleshooting

### Common Issues
1. **Email not received**: Check spam folder, verify SMTP settings
2. **OTP expired**: Use resend functionality
3. **Database errors**: Ensure migrations are applied
4. **Frontend routing**: Verify route configuration in App.jsx

### Debug Mode
- Set `DEBUG=True` in Django settings for detailed error messages
- Check browser console for frontend errors
- Monitor Django server logs for backend issues

## Conclusion

This implementation provides a secure, user-friendly OTP-based email verification system that integrates seamlessly with the existing authentication flow. The system is production-ready with proper error handling, security measures, and a polished user interface.
