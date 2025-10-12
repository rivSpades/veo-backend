"""
Support app views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import SupportTicket, TicketMessage
from .serializers import (
    SupportTicketSerializer,
    SupportTicketListSerializer,
    SupportTicketCreateSerializer,
    TicketMessageSerializer
)


class SupportTicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for support tickets
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return tickets for the authenticated user's instances
        """
        user = self.request.user
        return SupportTicket.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SupportTicketListSerializer
        elif self.action == 'create':
            return SupportTicketCreateSerializer
        return SupportTicketSerializer
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """
        Add a message/reply to a ticket
        POST /api/support-tickets/{id}/add_message/
        Body: { "content": "message text" }
        """
        ticket = self.get_object()
        
        content = request.data.get('content')
        if not content:
            return Response(
                {'error': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = TicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            content=content,
            is_staff=False
        )
        
        # Update ticket timestamp
        ticket.updated_at = timezone.now()
        ticket.save()
        
        serializer = TicketMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """
        Change ticket status
        POST /api/support-tickets/{id}/change_status/
        Body: { "status": "resolved" }
        """
        ticket = self.get_object()
        
        new_status = request.data.get('status')
        if new_status not in dict(SupportTicket.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = ticket.status
        ticket.status = new_status
        if new_status == 'resolved' and not ticket.resolved_at:
            ticket.resolved_at = timezone.now()
        ticket.save()
        
        # Create a status change message
        status_labels = dict(SupportTicket.STATUS_CHOICES)
        TicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            content=f"Status changed from '{status_labels.get(old_status, old_status)}' to '{status_labels.get(new_status, new_status)}'",
            message_type='status_change',
            is_staff=request.user.is_staff or request.user.is_superuser
        )
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get ticket statistics for the user
        GET /api/support-tickets/stats/
        """
        user = request.user
        tickets = SupportTicket.objects.filter(user=user)
        
        stats = {
            'total': tickets.count(),
            'open': tickets.filter(status='open').count(),
            'in_progress': tickets.filter(status='in_progress').count(),
            'resolved': tickets.filter(status='resolved').count(),
            'closed': tickets.filter(status='closed').count(),
        }
        
        return Response(stats)

