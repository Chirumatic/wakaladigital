from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    SavingsGroup, GroupMembership, Contribution, 
    Loan, Investment, FinancialEducation,
    UserProgress, Notification
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class SavingsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGroup
        fields = '__all__'

class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = '__all__'

class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = '__all__'

class FinancialEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialEducation
        fields = '__all__'

class UserProgressSerializer(serializers.ModelSerializer):
    module = FinancialEducationSerializer(read_only=True)
    
    class Meta:
        model = UserProgress
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
