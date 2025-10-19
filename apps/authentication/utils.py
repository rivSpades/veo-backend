"""
Utility functions for authentication
Handles OTP sending via SMS (Twilio) and Email (SendGrid)
"""
from django.conf import settings
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging

logger = logging.getLogger(__name__)


class TwilioService:
    """Service for sending SMS via Twilio"""

    @staticmethod
    def send_otp(phone_number, otp_code):
        """
        Send OTP code via SMS

        Args:
            phone_number (str): Recipient phone number in E.164 format
            otp_code (str): 6-digit OTP code

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Initialize Twilio client
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )

            # Compose message
            message_body = f"Your VEOmenu verification code is: {otp_code}\n\nThis code expires in 10 minutes."

            # Send SMS
            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )

            logger.info(f"OTP sent successfully to {phone_number}. SID: {message.sid}")
            return True, "OTP sent successfully"

        except Exception as e:
            logger.error(f"Failed to send OTP to {phone_number}: {str(e)}")
            return False, f"Failed to send OTP: {str(e)}"


class SendGridService:
    """Service for sending emails via SendGrid"""

    @staticmethod
    def send_welcome_email(user_email, user_name):
        """
        Send welcome email after successful registration

        Args:
            user_email (str): Recipient email address
            user_name (str): User's name

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Initialize SendGrid client
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

            # Create email content
            from_email = Email(settings.DEFAULT_FROM_EMAIL, "VEOmenu Team")
            to_email = To(user_email)
            subject = "Welcome to VEOmenu!"

            # HTML content with VEOmenu branding
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to VEOmenu</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 40px 0;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                <!-- Header -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                                        <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">VEOmenu</h1>
                                        <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; opacity: 0.9;">Digital Menu Platform</p>
                                    </td>
                                </tr>

                                <!-- Content -->
                                <tr>
                                    <td style="padding: 40px 30px;">
                                        <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Welcome, {user_name}!</h2>
                                        <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                            Thank you for joining VEOmenu, the modern digital menu platform for restaurants and businesses.
                                        </p>
                                        <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                            Your account has been successfully created and verified. You can now start creating beautiful, interactive menus for your customers.
                                        </p>

                                        <!-- CTA Button -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                            <tr>
                                                <td align="center">
                                                    <a href="{settings.FRONTEND_URL}/dashboard"
                                                       style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                                              color: #ffffff; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: 600;">
                                                        Get Started
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- Features -->
                                        <div style="margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
                                            <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">What's next?</h3>
                                            <ul style="margin: 0; padding-left: 20px; color: #666666; font-size: 14px; line-height: 1.8;">
                                                <li>Create your first digital menu</li>
                                                <li>Customize your menu design</li>
                                                <li>Add items with images and descriptions</li>
                                                <li>Share your menu with QR codes</li>
                                                <li>Track analytics and insights</li>
                                            </ul>
                                        </div>

                                        <p style="margin: 20px 0 0 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                            If you have any questions or need assistance, feel free to reach out to our support team.
                                        </p>
                                    </td>
                                </tr>

                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e0e0e0;">
                                        <p style="margin: 0 0 10px 0; color: #999999; font-size: 12px;">
                                            © 2025 VEOmenu. All rights reserved.
                                        </p>
                                        <p style="margin: 0; color: #999999; font-size: 12px;">
                                            This email was sent to {user_email}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            # Plain text fallback
            plain_content = f"""
            Welcome to VEOmenu, {user_name}!

            Thank you for joining VEOmenu, the modern digital menu platform for restaurants and businesses.

            Your account has been successfully created and verified. You can now start creating beautiful, interactive menus for your customers.

            Get started: {settings.FRONTEND_URL}/dashboard

            What's next?
            - Create your first digital menu
            - Customize your menu design
            - Add items with images and descriptions
            - Share your menu with QR codes
            - Track analytics and insights

            If you have any questions or need assistance, feel free to reach out to our support team.

            © 2025 VEOmenu. All rights reserved.
            """

            # Create and send email
            mail = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=plain_content,
                html_content=html_content
            )

            response = sg.send(mail)
            logger.info(f"Welcome email sent successfully to {user_email}. Status: {response.status_code}")
            return True, "Welcome email sent successfully"

        except Exception as e:
            logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
            return False, f"Failed to send email: {str(e)}"

    @staticmethod
    def send_otp_email(user_email, user_name, otp_code):
        """
        Send OTP code via email as backup

        Args:
            user_email (str): Recipient email address
            user_name (str): User's name
            otp_code (str): 6-digit OTP code

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Initialize SendGrid client
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

            # Create email content
            from_email = Email(settings.DEFAULT_FROM_EMAIL, "VEOmenu Team")
            to_email = To(user_email)
            subject = "Your VEOmenu Verification Code"

            # HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>VEOmenu Verification Code</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 40px 0;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                <!-- Header -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                                        <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">VEOmenu</h1>
                                        <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; opacity: 0.9;">Verification Code</p>
                                    </td>
                                </tr>

                                <!-- Content -->
                                <tr>
                                    <td style="padding: 40px 30px; text-align: center;">
                                        <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Hello, {user_name}!</h2>
                                        <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                            Your verification code is:
                                        </p>

                                        <!-- OTP Code -->
                                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                                    padding: 20px; border-radius: 10px; margin: 0 0 30px 0;">
                                            <p style="margin: 0; color: #ffffff; font-size: 48px; font-weight: 700; letter-spacing: 8px;">
                                                {otp_code}
                                            </p>
                                        </div>

                                        <p style="margin: 0 0 15px 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                            This code will expire in <strong>10 minutes</strong>.
                                        </p>
                                        <p style="margin: 0; color: #999999; font-size: 12px; line-height: 1.6;">
                                            If you didn't request this code, please ignore this email.
                                        </p>
                                    </td>
                                </tr>

                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e0e0e0;">
                                        <p style="margin: 0 0 10px 0; color: #999999; font-size: 12px;">
                                            © 2025 VEOmenu. All rights reserved.
                                        </p>
                                        <p style="margin: 0; color: #999999; font-size: 12px;">
                                            This email was sent to {user_email}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            # Plain text fallback
            plain_content = f"""
            Hello {user_name}!

            Your VEOmenu verification code is: {otp_code}

            This code will expire in 10 minutes.

            If you didn't request this code, please ignore this email.

            © 2025 VEOmenu. All rights reserved.
            """

            # Create and send email
            mail = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=plain_content,
                html_content=html_content
            )

            response = sg.send(mail)
            logger.info(f"OTP email sent successfully to {user_email}. Status: {response.status_code}")
            return True, "OTP email sent successfully"

        except Exception as e:
            logger.error(f"Failed to send OTP email to {user_email}: {str(e)}")
            return False, f"Failed to send email: {str(e)}"
