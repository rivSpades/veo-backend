"""
Support Tickets Models
"""
from django.db import models
from apps.authentication.models import User
from apps.instances.models import Instance
import uuid


class SupportTicket(models.Model):
    """
    Support ticket for customer help requests
    """
    CATEGORY_CHOICES = [
        ('cannot_use_app', 'I cannot use the app'),
        ('payment_issue', 'Payment or billing issue'),
        ('menu_not_loading', 'Menu not loading properly'),
        ('qr_code_issue', 'QR code problem'),
        ('translation_error', 'Translation or language issue'),
        ('feature_request', 'Feature request or suggestion'),
        ('other', 'Other issue'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Mapping of category to priority
    CATEGORY_PRIORITY_MAP = {
        'cannot_use_app': 'critical',
        'payment_issue': 'high',
        'menu_not_loading': 'high',
        'qr_code_issue': 'medium',
        'translation_error': 'medium',
        'feature_request': 'low',
        'other': 'medium',
    }
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, related_name='support_tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Image attachment for ticket creation
    screenshot = models.ImageField(upload_to='ticket_screenshots/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'support_tickets'
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.ticket_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate ticket number: TICK-XXXX
            last_ticket = SupportTicket.objects.all().order_by('-created_at').first()
            if last_ticket and last_ticket.ticket_number:
                last_num = int(last_ticket.ticket_number.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.ticket_number = f"TICK-{new_num:04d}"
        
        # Auto-set priority based on category if not manually set
        if self.category and self.category in self.CATEGORY_PRIORITY_MAP:
            self.priority = self.CATEGORY_PRIORITY_MAP[self.category]
        
        super().save(*args, **kwargs)


class TicketMessage(models.Model):
    """
    Messages/replies in a support ticket
    """
    MESSAGE_TYPE_CHOICES = [
        ('message', 'Message'),
        ('status_change', 'Status Change'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_messages', null=True, blank=True)
    
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='message')
    is_staff = models.BooleanField(default=False)  # True if message is from support staff
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ticket_messages'
        verbose_name = 'Ticket Message'
        verbose_name_plural = 'Ticket Messages'
        ordering = ['created_at']
        
    def __str__(self):
        return f"Message on {self.ticket.ticket_number} by {self.author.email}"


class TicketAttachment(models.Model):
    """
    File attachments for support tickets
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(TicketMessage, on_delete=models.CASCADE, related_name='attachments')
    
    file = models.FileField(upload_to='ticket_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()  # Size in bytes
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ticket_attachments'
        verbose_name = 'Ticket Attachment'
        verbose_name_plural = 'Ticket Attachments'
        
    def __str__(self):
        return f"{self.filename} ({self.file_size} bytes)"

