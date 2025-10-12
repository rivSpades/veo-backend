"""
Support app serializers
"""
from rest_framework import serializers
from .models import SupportTicket, TicketMessage, TicketAttachment


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for ticket attachments
    """
    class Meta:
        model = TicketAttachment
        fields = ['id', 'filename', 'file', 'file_size', 'created_at']
        read_only_fields = ['id', 'created_at']


class TicketMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ticket messages
    """
    author_name = serializers.CharField(source='author.name', read_only=True, allow_null=True)
    author_email = serializers.EmailField(source='author.email', read_only=True, allow_null=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = TicketMessage
        fields = [
            'id', 'ticket', 'author', 'author_name', 'author_email',
            'content', 'message_type', 'is_staff', 'attachments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'is_staff', 'created_at', 'updated_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    """
    Full ticket serializer with messages
    """
    messages = TicketMessageSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'instance', 'user', 'user_name', 'user_email',
            'title', 'description', 'category', 'priority', 'status', 'screenshot',
            'created_at', 'updated_at', 'resolved_at',
            'messages'
        ]
        read_only_fields = ['id', 'ticket_number', 'user', 'priority', 'created_at', 'updated_at']


class SupportTicketListSerializer(serializers.ModelSerializer):
    """
    Lightweight ticket serializer for list views
    """
    user_name = serializers.CharField(source='user.name', read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'user_name',
            'title', 'category', 'priority', 'status',
            'created_at', 'message_count'
        ]
        read_only_fields = ['id', 'ticket_number', 'priority', 'created_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new tickets
    """
    class Meta:
        model = SupportTicket
        fields = ['title', 'description', 'category', 'instance', 'screenshot']
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Priority will be auto-set based on category in model.save()
        ticket = SupportTicket.objects.create(user=user, **validated_data)
        
        # Create initial message with the description
        TicketMessage.objects.create(
            ticket=ticket,
            author=user,
            content=validated_data['description'],
            is_staff=False
        )
        
        return ticket

