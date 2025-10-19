# Phone OTP Verification Integration

## Overview

This document describes the phone OTP verification system integrated into the VEOmenu registration flow. The system uses Twilio for SMS delivery and SendGrid for email delivery, providing a dual-channel verification approach.

## Features

- **Two-Factor Phone Verification**: Users must verify their phone number during registration
- **Dual-Channel Delivery**: OTP codes sent via both SMS (Twilio) and Email (SendGrid)
- **Branded Email Templates**: Professional, responsive email templates with VEOmenu branding
- **Rate Limiting**: Maximum 3 verification attempts per OTP code
- **Expiration**: OTP codes expire after 10 minutes
- **Resend Functionality**: Users can request a new OTP if needed
- **Welcome Email**: Automatic welcome email sent after successful registration

## API Endpoints

### 1. Register (Step 1: Request OTP)

**Endpoint**: `POST /api/auth/register/`

**Description**: Initiates user registration by creating an OTP and sending it to the user's phone and email.

**Request Body**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "password": "securePassword123",
  "language": "en"
}
```

**Response** (200 OK):
```json
{
  "message": "OTP sent successfully. Please verify your phone number.",
  "email": "user@example.com",
  "phone": "+1234567890",
  "otp_sent_via": {
    "sms": true,
    "email": true
  },
  "expires_in_minutes": 10
}
```

**Notes**:
- Phone number must be in international format (starting with `+`)
- Email must be unique (not already registered)
- Registration data is stored in session temporarily
- OTP is sent via both SMS and email

---

### 2. Verify OTP (Step 2: Complete Registration)

**Endpoint**: `POST /api/auth/verify-otp/`

**Description**: Verifies the OTP code and completes user registration.

**Request Body**:
```json
{
  "email": "user@example.com",
  "phone": "+1234567890",
  "otp_code": "123456"
}
```

**Response** (201 Created):
```json
{
  "message": "Registration successful! Welcome to VEOmenu.",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+1234567890",
    "language": "en",
    "has_instances": false,
    "instances": []
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "otp_code": ["Invalid OTP code. 2 attempts remaining."]
}
```

**Notes**:
- OTP must be exactly 6 digits
- Maximum 3 verification attempts
- User account is created only after successful verification
- JWT tokens are returned for immediate login
- Welcome email is sent automatically

---

### 3. Resend OTP

**Endpoint**: `POST /api/auth/resend-otp/`

**Description**: Generates and sends a new OTP code to the user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "phone": "+1234567890"
}
```

**Response** (200 OK):
```json
{
  "message": "OTP resent successfully.",
  "otp_sent_via": {
    "sms": true,
    "email": true
  },
  "expires_in_minutes": 10
}
```

**Notes**:
- Must have a pending registration session
- Generates a new OTP code (previous code becomes invalid)
- Resets the attempt counter

---

## Database Models

### PhoneOTP Model

```python
class PhoneOTP(models.Model):
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(db_index=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
```

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```env
# Twilio Settings (for SMS OTP)
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'  # Your Twilio phone number

# SendGrid Settings (for transactional emails)
SENDGRID_API_KEY = 'your_sendgrid_api_key'

# Email Settings
DEFAULT_FROM_EMAIL = 'noreply@veomenu.com'
```

### Twilio Setup

1. Create a Twilio account at https://www.twilio.com/
2. Get a phone number capable of sending SMS
3. Find your Account SID and Auth Token in the Twilio Console
4. Add credentials to `.env` file

### SendGrid Setup

1. Create a SendGrid account at https://sendgrid.com/
2. Create an API key with "Mail Send" permissions
3. Add API key to `.env` file
4. Optionally set up domain authentication for better deliverability

## Email Templates

### OTP Verification Email

- **Subject**: "Your VEOmenu Verification Code"
- **Features**:
  - Large, centered OTP code display
  - VEOmenu branding with gradient colors
  - Expiration notice (10 minutes)
  - Security reminder
  - Responsive design for mobile devices

### Welcome Email

- **Subject**: "Welcome to VEOmenu!"
- **Features**:
  - Personalized greeting
  - "Get Started" call-to-action button
  - Feature overview
  - Next steps checklist
  - VEOmenu branding
  - Responsive design

## Frontend Integration

### Registration Flow

1. **User fills registration form** with email, name, phone, password
2. **Submit to `/api/auth/register/`**
   - Store email and phone in local state
   - Redirect to OTP verification page
3. **User enters OTP code**
4. **Submit to `/api/auth/verify-otp/`**
   - On success: Store JWT tokens and redirect to dashboard
   - On failure: Show error message with remaining attempts
5. **Resend OTP if needed**
   - Call `/api/auth/resend-otp/` endpoint

### Example Frontend Code (React)

```javascript
// Step 1: Registration
const handleRegister = async (formData) => {
  const response = await fetch('http://localhost:8000/api/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });

  const data = await response.json();

  if (response.ok) {
    // Store email and phone for next step
    setEmail(data.email);
    setPhone(data.phone);
    // Redirect to OTP verification page
    navigate('/auth/verify-otp');
  }
};

// Step 2: Verify OTP
const handleVerifyOTP = async (otpCode) => {
  const response = await fetch('http://localhost:8000/api/auth/verify-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: email,
      phone: phone,
      otp_code: otpCode
    })
  });

  const data = await response.json();

  if (response.ok) {
    // Store tokens
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    // Redirect to dashboard
    navigate('/dashboard');
  }
};

// Resend OTP
const handleResendOTP = async () => {
  const response = await fetch('http://localhost:8000/api/auth/resend-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: email,
      phone: phone
    })
  });

  if (response.ok) {
    showToast('OTP resent successfully');
  }
};
```

## Security Considerations

1. **Rate Limiting**: Implement rate limiting on registration endpoint to prevent abuse
2. **Phone Number Validation**: Phone numbers must be in international format
3. **Attempt Limits**: Maximum 3 verification attempts per OTP
4. **Expiration**: OTP codes expire after 10 minutes
5. **IP Tracking**: OTP requests are tracked by IP address
6. **Session Security**: Registration data stored in Django sessions
7. **HTTPS**: Always use HTTPS in production

## Testing

### Test OTP Flow Locally

For development/testing, you can:

1. **Check console output**: OTP codes are logged in console
2. **Use Django admin**: View OTP codes in admin panel at `/admin/authentication/phoneotp/`
3. **Mock Twilio/SendGrid**: For testing without sending real SMS/emails

### Admin Panel

Access the PhoneOTP admin at: `http://localhost:8000/admin/authentication/phoneotp/`

View:
- Phone numbers
- Email addresses
- OTP codes
- Verification status
- Attempt counts
- Creation/expiration times

## Troubleshooting

### OTP Not Received

1. **Check Twilio phone number**: Ensure `TWILIO_PHONE_NUMBER` is set correctly
2. **Verify Twilio credentials**: Check Account SID and Auth Token
3. **Check phone format**: Must start with `+` and country code
4. **Check email spam**: OTP emails might be in spam folder
5. **View logs**: Check Django console for error messages

### Registration Fails After OTP Verification

1. **Check session**: Ensure Django sessions are enabled
2. **Session expiry**: Registration data might have expired
3. **Check database**: Verify OTP was marked as verified

### Email Template Issues

1. **SendGrid API key**: Ensure API key has Mail Send permissions
2. **From email**: Verify `DEFAULT_FROM_EMAIL` is set
3. **Domain authentication**: Set up domain authentication in SendGrid

## Future Enhancements

- [ ] Add SMS rate limiting per phone number
- [ ] Implement phone number blacklist
- [ ] Add support for multiple countries/languages
- [ ] Implement 2FA for login (not just registration)
- [ ] Add phone number verification for profile updates
- [ ] Implement backup codes for account recovery

## Support

For issues or questions:
- Check Django logs for error messages
- Review Twilio and SendGrid dashboards
- Verify all environment variables are set correctly
- Ensure database migrations are applied
