from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .models import (
    SavingsGroup, GroupMembership, Contribution, 
    Loan, Investment, FinancialEducation,
    UserProgress, Notification
)
from .serializers import (
    UserSerializer, SavingsGroupSerializer, GroupMembershipSerializer,
    ContributionSerializer, LoanSerializer, InvestmentSerializer,
    FinancialEducationSerializer, UserProgressSerializer, NotificationSerializer
)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class SavingsGroupViewSet(viewsets.ModelViewSet):
    queryset = SavingsGroup.objects.all()
    serializer_class = SavingsGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    @action(detail=True, methods=['post'])
    def join_group(self, request, pk=None):
        group = self.get_object()
        user = request.user
        
        if GroupMembership.objects.filter(user=user, group=group).exists():
            return Response({'detail': 'Already a member'}, status=status.HTTP_400_BAD_REQUEST)
        
        GroupMembership.objects.create(user=user, group=group)
        return Response({'detail': 'Joined successfully'})

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        group = self.get_object()
        memberships = GroupMembership.objects.filter(group=group)
        serializer = GroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contribution.objects.filter(member__user=self.request.user)

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        loan = self.get_object()
        loan.status = 'APPROVED'
        loan.save()
        return Response({'detail': 'Loan approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        loan = self.get_object()
        loan.status = 'REJECTED'
        loan.save()
        return Response({'detail': 'Loan rejected'})

class InvestmentViewSet(viewsets.ModelViewSet):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Investment.objects.filter(group__members=self.request.user)

class FinancialEducationViewSet(viewsets.ModelViewSet):
    queryset = FinancialEducation.objects.all()
    serializer_class = FinancialEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def complete_module(self, request, pk=None):
        module = self.get_object()
        user = request.user
        score = request.data.get('score', 0)
        
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            module=module,
            defaults={'score': score, 'completed': True}
        )
        
        if not created:
            progress.score = score
            progress.completed = True
            progress.save()
        
        return Response({'detail': 'Module completed successfully'})

class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
