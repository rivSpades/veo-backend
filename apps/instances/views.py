"""
Instances app views
Handles restaurant/bar instances, members, and business hours
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Instance, InstanceMember, BusinessHours
from .serializers import (
    InstanceSerializer,
    InstanceListSerializer,
    InstanceCreateSerializer,
    InstanceUpdateSerializer,
    InstanceMemberSerializer,
    InstanceMemberInviteSerializer,
    BusinessHoursSerializer
)

User = get_user_model()


class InstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing instances (restaurants/bars)
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get instances where the user is a member
        """
        return Instance.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        ).distinct()

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return InstanceListSerializer
        elif self.action == 'create':
            return InstanceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InstanceUpdateSerializer
        return InstanceSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new instance
        POST /api/instances/
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response({
            'message': 'Instance created successfully',
            'instance': InstanceSerializer(instance).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='members')
    def members(self, request, pk=None):
        """
        Get all members of an instance
        GET /api/instances/{id}/members/
        """
        instance = self.get_object()

        # Check if user has permission (owner, admin, or manager)
        membership = InstanceMember.objects.filter(
            instance=instance,
            user=request.user,
            role__in=['owner', 'admin', 'manager']
        ).first()

        if not membership:
            return Response({
                'error': 'You do not have permission to view members'
            }, status=status.HTTP_403_FORBIDDEN)

        members = InstanceMember.objects.filter(instance=instance, is_active=True)
        serializer = InstanceMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='invite-member')
    def invite_member(self, request, pk=None):
        """
        Invite a member to the instance
        POST /api/instances/{id}/invite-member/
        Body: {email, role}
        """
        instance = self.get_object()

        # Check if user is owner or admin
        membership = InstanceMember.objects.filter(
            instance=instance,
            user=request.user,
            role__in=['owner', 'admin']
        ).first()

        if not membership:
            return Response({
                'error': 'Only owners and admins can invite members'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = InstanceMemberInviteSerializer(
            data=request.data,
            context={'instance': instance}
        )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        role = serializer.validated_data['role']

        user = User.objects.get(email=email)

        # Create membership
        new_member = InstanceMember.objects.create(
            instance=instance,
            user=user,
            role=role,
            is_active=True
        )

        return Response({
            'message': f'User {email} has been added as {role}',
            'member': InstanceMemberSerializer(new_member).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        """
        Remove a member from the instance
        DELETE /api/instances/{id}/remove-member/
        Body: {user_id}
        """
        instance = self.get_object()

        # Check if user is owner or admin
        membership = InstanceMember.objects.filter(
            instance=instance,
            user=request.user,
            role__in=['owner', 'admin']
        ).first()

        if not membership:
            return Response({
                'error': 'Only owners and admins can remove members'
            }, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        member = InstanceMember.objects.filter(
            instance=instance,
            user_id=user_id,
            is_active=True
        ).first()

        if not member:
            return Response({
                'error': 'Member not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Prevent removing the owner
        if member.role == 'owner':
            return Response({
                'error': 'Cannot remove the owner'
            }, status=status.HTTP_400_BAD_REQUEST)

        member.is_active = False
        member.save()

        return Response({
            'message': 'Member removed successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'put'], url_path='business-hours')
    def business_hours(self, request, pk=None):
        """
        Get or update business hours
        GET /api/instances/{id}/business-hours/
        PUT /api/instances/{id}/business-hours/
        Body (PUT): [{day_of_week, open_time, close_time, is_closed}, ...]
        """
        instance = self.get_object()

        if request.method == 'GET':
            hours = BusinessHours.objects.filter(instance=instance).order_by('day_of_week')
            serializer = BusinessHoursSerializer(hours, many=True)
            return Response(serializer.data)

        elif request.method == 'PUT':
            # Check if user has permission
            membership = InstanceMember.objects.filter(
                instance=instance,
                user=request.user,
                role__in=['owner', 'admin', 'manager']
            ).first()

            if not membership:
                return Response({
                    'error': 'You do not have permission to update business hours'
                }, status=status.HTTP_403_FORBIDDEN)

            # Delete existing hours
            BusinessHours.objects.filter(instance=instance).delete()

            # Create new hours
            hours_data = request.data if isinstance(request.data, list) else [request.data]

            for hour_data in hours_data:
                hour_data['instance'] = instance.id
                serializer = BusinessHoursSerializer(data=hour_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            # Return updated hours
            hours = BusinessHours.objects.filter(instance=instance).order_by('day_of_week')
            serializer = BusinessHoursSerializer(hours, many=True)

            return Response({
                'message': 'Business hours updated successfully',
                'hours': serializer.data
            }, status=status.HTTP_200_OK)


class InstanceMemberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing instance members
    """
    queryset = InstanceMember.objects.filter(is_active=True)
    serializer_class = InstanceMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter to instances where the user is a member
        """
        user_instances = Instance.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        )

        return InstanceMember.objects.filter(
            instance__in=user_instances,
            is_active=True
        )
