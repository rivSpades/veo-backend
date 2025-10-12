"""
Support app admin
"""
from django.contrib import admin
from .models import SupportTicket, TicketMessage, TicketAttachment


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'title', 'user', 'instance', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['ticket_number', 'title', 'user__email', 'instance__name']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'created_at']
    search_fields = ['ticket__ticket_number', 'author__email', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'message', 'file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['filename', 'message__ticket__ticket_number']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

