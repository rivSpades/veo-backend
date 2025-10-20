"""
Services for authentication including phone verification and email sending.
"""

import re
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import PhoneVerification, User


class PhoneService:
    """Service for handling phone number verification via SMS."""
    
    def __init__(self):
        # Check if Twilio credentials are configured
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_ACCOUNT_SID != 'your_twilio_account_sid_here':
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.phone_number = settings.TWILIO_PHONE_NUMBER
            self.twilio_configured = True
        else:
            self.client = None
            self.phone_number = None
            self.twilio_configured = False
    
    def normalize_phone_number(self, phone_number):
        """Normalize phone number by removing spaces and ensuring proper format."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # If it doesn't start with +, add it
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        
        return cleaned
    
    def send_verification_sms(self, phone_number, verification_code):
        """Send SMS with verification code."""
        if not self.twilio_configured:
            return {
                'success': False,
                'error': 'SMS service not configured. Please contact support.'
            }
        
        try:
            normalized_phone = self.normalize_phone_number(phone_number)
            
            message = self.client.messages.create(
                body=f"Your VEOmenu verification code is: {verification_code}. This code expires in 10 minutes.",
                from_=self.phone_number,
                to=normalized_phone
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'phone_number': normalized_phone
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_verification(self, user, phone_number):
        """Create a new phone verification record."""
        # Check if phone number already exists for another user
        if User.objects.filter(phone=phone_number).exclude(id=user.id).exists():
            return {
                'success': False,
                'error': 'Phone number is already registered with another account.'
            }
        
        # Check cooldown period (10 minutes) - single entry per user
        cooldown_minutes = 10
        try:
            verification = PhoneVerification.objects.get(user=user)
            time_remaining = (verification.created_at + timedelta(minutes=cooldown_minutes) - timezone.now()).total_seconds()
            if time_remaining > 0:
                return {
                    'success': False,
                    'error': f'Please wait {int(time_remaining / 60)} minutes and {int(time_remaining % 60)} seconds before requesting another code.',
                    'cooldown_remaining': int(time_remaining)
                }
        except PhoneVerification.DoesNotExist:
            pass
        
        # Normalize phone number
        normalized_phone = self.normalize_phone_number(phone_number)
        
        # Create verification record
        verification_code = PhoneVerification.generate_verification_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Get or create a single verification entry for this user
        verification, created = PhoneVerification.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': normalized_phone,
                'verification_code': verification_code,
                'expires_at': expires_at
            }
        )
        
        # If entry already exists, update it with new code
        if not created:
            verification.phone_number = normalized_phone
            verification.verification_code = verification_code
            verification.expires_at = expires_at
            verification.is_verified = False
            verification.attempts = 0
            verification.created_at = timezone.now()  # Update the created_at timestamp
            verification.save()
        
        # Send SMS
        sms_result = self.send_verification_sms(normalized_phone, verification_code)
        
        if sms_result['success']:
            return {
                'success': True,
                'verification_id': verification.id,
                'phone_number': normalized_phone,
                'expires_at': expires_at
            }
        else:
            # In development mode, don't delete the verification record
            # Just log the error and return success
            print(f"SMS failed but continuing in development mode: {sms_result['error']}")
            return {
                'success': True,
                'verification_id': verification.id,
                'phone_number': normalized_phone,
                'expires_at': expires_at,
                'development_mode': True,
                'sms_error': sms_result['error']
            }
    
    def verify_code(self, verification_id, code):
        """Verify the provided code."""
        try:
            verification = PhoneVerification.objects.get(id=verification_id)
            
            if verification.verify_code(code):
                # Update user's phone number and verification status
                verification.user.phone = verification.phone_number
                verification.user.is_phone_verified = True
                verification.user.save()
                
                print(f"Phone verification successful for user {verification.user.id}: is_phone_verified = {verification.user.is_phone_verified}")
                
                return {
                    'success': True,
                    'message': 'Phone number verified successfully.'
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid verification code or code has expired.'
                }
        except PhoneVerification.DoesNotExist:
            return {
                'success': False,
                'error': 'Verification record not found.'
            }
    
    def verify_code_for_user(self, user, code):
        """Verify the provided code for a specific user (single entry per user)."""
        try:
            verification = PhoneVerification.objects.get(user=user)
            
            if verification.is_verified:
                return {
                    'success': False,
                    'error': 'This verification code has already been used.'
                }
            
            if verification.expires_at < timezone.now():
                return {
                    'success': False,
                    'error': 'Verification code has expired.'
                }
            
            if verification.verify_code(code):
                # Update user's phone number and verification status
                verification.user.phone = verification.phone_number
                verification.user.is_phone_verified = True
                verification.user.save()
                
                print(f"Phone verification successful for user {verification.user.id}: is_phone_verified = {verification.user.is_phone_verified}")
                
                return {
                    'success': True,
                    'message': 'Phone number verified successfully.'
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid verification code.'
                }
        except PhoneVerification.DoesNotExist:
            return {
                'success': False,
                'error': 'No verification code found for this user.'
            }


class EmailService:
    """Service for handling email sending via SendGrid."""
    
    def __init__(self):
        # Check if SendGrid is configured
        print(f"EmailService: Checking SendGrid configuration...")
        print(f"EmailService: SENDGRID_API_KEY exists: {hasattr(settings, 'SENDGRID_API_KEY')}")
        if hasattr(settings, 'SENDGRID_API_KEY'):
            print(f"EmailService: SENDGRID_API_KEY value: {settings.SENDGRID_API_KEY}")
            print(f"EmailService: SENDGRID_API_KEY length: {len(settings.SENDGRID_API_KEY) if settings.SENDGRID_API_KEY else 0}")
        
        if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
            print(f"EmailService: SendGrid configured, creating client...")
            self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            self.sendgrid_configured = True
            print(f"EmailService: SendGrid client created successfully")
        else:
            print(f"EmailService: SendGrid not configured, using development mode")
            self.sg = None
            self.sendgrid_configured = False
    
    def send_verification_email(self, to_email, verification_code):
        """Send email with verification code."""
        try:
            message = Mail(
                from_email='ricardomiguelrosaclemente@gmail.com',
                to_emails=to_email,
                subject='VEOmenu - Email Verification',
                html_content=f"""
                <h2>Verify Your Email Address</h2>
                <p>Your verification code is: <strong>{verification_code}</strong></p>
                <p>This code expires in 10 minutes.</p>
                <p>If you didn't request this verification, please ignore this email.</p>
                """
            )
            
            response = self.sg.send(message)
            
            return {
                'success': True,
                'status_code': response.status_code
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_welcome_email(self, to_email, user_name):
        """Send welcome email to new user."""
        # if not self.sendgrid_configured:
        #     print(f"SendGrid not configured. Welcome email for {to_email} would be sent here.")
        #     # Development mode fallback
        #     print(f"🎉 Welcome to VEOmenu, {user_name}!")
        #     print(f"📧 Email would be sent to: {to_email}")
        #     print(f"📱 Phone verification will be sent via SMS")
        #     print(f"🔗 Dashboard: https://veomenu.com/dashboard")
        #     return {
        #         'success': True,
        #         'development_mode': True,
        #         'message': 'Welcome email logged to console (SendGrid not fully configured)'
        #     }
        
        try:
            message = Mail(
                from_email='ricardomiguelrosaclemente@gmail.com', # This needs to be verified in SendGrid
                to_emails=to_email,
                subject='Welcome to VEOmenu! 🎉',
                html_content=self._get_welcome_email_template(user_name)
            )
            
            print(f"Attempting to send welcome email to {to_email}")
            response = self.sg.send(message)
            print(f"SendGrid response: {response.status_code}")
            print(f"SendGrid headers: {response.headers}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'headers': dict(response.headers)
            }
        except Exception as e:
            print(f"SendGrid error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_welcome_email_template(self, user_name):
        """Generate welcome email HTML template."""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to VEOmenu</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 12px;
                    padding: 40px;
                    color: white;
                    text-align: center;
                }}
                .logo {{
                    font-size: 32px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .welcome-title {{
                    font-size: 28px;
                    margin-bottom: 20px;
                    color: #fff;
                }}
                .welcome-message {{
                    font-size: 18px;
                    margin-bottom: 30px;
                    opacity: 0.9;
                }}
                .features {{
                    background: rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 30px;
                    margin: 30px 0;
                    backdrop-filter: blur(10px);
                }}
                .feature-item {{
                    display: flex;
                    align-items: center;
                    margin: 15px 0;
                    font-size: 16px;
                }}
                .feature-icon {{
                    font-size: 24px;
                    margin-right: 15px;
                    width: 30px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 18px;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
                    transition: transform 0.3s ease;
                }}
                .cta-button:hover {{
                    transform: translateY(-2px);
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(255,255,255,0.2);
                    font-size: 14px;
                    opacity: 0.8;
                }}
                .social-links {{
                    margin: 20px 0;
                }}
                .social-links a {{
                    color: white;
                    text-decoration: none;
                    margin: 0 10px;
                    font-size: 18px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🍽️ VEOmenu</div>
                
                <h1 class="welcome-title">Welcome to VEOmenu, {user_name}! 🎉</h1>
                
                <p class="welcome-message">
                    Thank you for joining our community of innovative restaurants and food businesses. 
                    We're excited to help you create amazing digital menu experiences for your customers.
                </p>
                
                <div class="features">
                    <h3 style="margin-top: 0; color: #fff;">What you can do with VEOmenu:</h3>
                    
                    <div class="feature-item">
                        <span class="feature-icon">📱</span>
                        <span>Create stunning digital menus with QR codes</span>
                    </div>
                    
                    <div class="feature-item">
                        <span class="feature-icon">🎨</span>
                        <span>Customize designs to match your brand</span>
                    </div>
                    
                    <div class="feature-item">
                        <span class="feature-icon">📊</span>
                        <span>Track menu performance and analytics</span>
                    </div>
                    
                    <div class="feature-item">
                        <span class="feature-icon">🌍</span>
                        <span>Multi-language support for global reach</span>
                    </div>
                    
                    <div class="feature-item">
                        <span class="feature-icon">⚡</span>
                        <span>Real-time menu updates and management</span>
                    </div>
                </div>
                
                <a href="https://veomenu.com/dashboard" class="cta-button">
                    Get Started Now →
                </a>
                
                <div class="social-links">
                    <a href="https://twitter.com/veomenu">🐦 Twitter</a>
                    <a href="https://facebook.com/veomenu">📘 Facebook</a>
                    <a href="https://instagram.com/veomenu">📷 Instagram</a>
                </div>
                
                <div class="footer">
                    <p>Need help? Contact us at <a href="mailto:support@veomenu.com" style="color: #fff;">support@veomenu.com</a></p>
                    <p>© 2024 VEOmenu. All rights reserved.</p>
                    <p>You're receiving this email because you signed up for VEOmenu.</p>
                </div>
            </div>
        </body>
        </html>
        """
