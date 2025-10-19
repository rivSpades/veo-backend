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
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER
    
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
            # Delete the verification record if SMS failed
            verification.delete()
            return {
                'success': False,
                'error': f'Failed to send SMS: {sms_result["error"]}'
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
        self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    
    def send_verification_email(self, to_email, verification_code):
        """Send email with verification code."""
        try:
            message = Mail(
                from_email='noreply@veomenu.com',
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
        """Send welcome email to new users."""
        try:
            message = Mail(
                from_email='welcome@veomenu.com',
                to_emails=to_email,
                subject='Welcome to VEOmenu!',
                html_content=f"""
                <h2>Welcome to VEOmenu, {user_name}!</h2>
                <p>Thank you for joining VEOmenu. You can now start creating your digital menu.</p>
                <p>If you have any questions, feel free to contact our support team.</p>
                <p>Best regards,<br>The VEOmenu Team</p>
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
