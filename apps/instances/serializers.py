"""
Instances app serializers
Handles restaurant/bar instances, members, and business hours
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Instance, InstanceMember, BusinessHours

User = get_user_model()


class BusinessHoursSerializer(serializers.ModelSerializer):
    """
    Serializer for business hours
    """
    class Meta:
        model = BusinessHours
        fields = [
            'id', 'instance', 'day_of_week',
            'opening_time', 'closing_time', 'is_closed'
        ]
        read_only_fields = ['id']


class InstanceSerializer(serializers.ModelSerializer):
    """
    Full instance serializer with all details
    """
    business_hours = BusinessHoursSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Instance
        fields = [
            'id', 'name', 'slug', 'logo', 'description',
            'address', 'city', 'country',
            'phone', 'email', 'website', 'whatsapp',
            'cuisine_type', 'wifi_name', 'wifi_password',
            'show_wifi_on_menu', 'show_hours_on_menu',
            'google_business_url', 'google_rating', 'google_review_count',
            'show_google_rating', 'subscription_status',
            'trial_start_date', 'trial_end_date', 'subscription_start_date',
            'is_active', 'created_at', 'updated_at',
            'business_hours', 'member_count'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'google_rating', 'google_review_count']

    def get_member_count(self, obj):
        """Get total number of members in this instance"""
        return obj.members.count()


class InstanceListSerializer(serializers.ModelSerializer):
    """
    Lightweight instance serializer for list views
    """
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Instance
        fields = [
            'id', 'name', 'slug', 'logo', 'city', 'country',
            'subscription_status', 'created_at', 'member_count'
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def get_member_count(self, obj):
        """Get total number of members"""
        return obj.members.count()


class InstanceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new instances
    Automatically creates owner membership for the creator
    """
    class Meta:
        model = Instance
        fields = [
            'name', 'description', 'address', 'city',
            'country', 'phone', 'email', 'website', 'cuisine_type'
        ]

    def create(self, validated_data):
        """
        Create instance and add creator as owner
        """
        try:
            user = self.context['request'].user
            print(f"Creating instance with data: {validated_data}")
            print(f"User: {user}")

            instance = Instance.objects.create(**validated_data)
            print(f"Instance created: {instance.id}")

            # Create owner membership
            InstanceMember.objects.create(
                instance=instance,
                user=user,
                role='owner',
                is_active=True
            )
            print(f"Owner membership created")

            return instance
        except Exception as e:
            print(f"ERROR creating instance: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


class InstanceMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for instance members
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    instance_name = serializers.CharField(source='instance.name', read_only=True)

    class Meta:
        model = InstanceMember
        fields = [
            'id', 'instance', 'instance_name', 'user',
            'user_email', 'user_name', 'role',
            'is_active', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']


class InstanceMemberInviteSerializer(serializers.Serializer):
    """
    Serializer for inviting members to an instance
    """
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=['admin', 'manager', 'staff'])

    def validate_email(self, value):
        """Ensure user exists"""
        if not User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                "No user found with this email. They must register first."
            )
        return value.lower()

    def validate(self, data):
        """Ensure user is not already a member"""
        instance = self.context.get('instance')
        email = data.get('email')

        user = User.objects.get(email=email)
        if InstanceMember.objects.filter(instance=instance, user=user).exists():
            raise serializers.ValidationError("This user is already a member of this instance.")

        return data


class InstanceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating instance details
    """
    class Meta:
        model = Instance
        fields = [
            'name', 'logo', 'description', 'address',
            'city', 'country', 'phone', 'email', 'website',
            'whatsapp', 'cuisine_type', 'wifi_name', 'wifi_password',
            'show_wifi_on_menu', 'show_hours_on_menu',
            'google_business_url', 'show_google_rating'
        ]

    def update(self, instance, validated_data):
        """Update instance details"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
