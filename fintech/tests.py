from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import (
    SavingsGroup, GroupMembership, Contribution,
    Loan, Investment, UserProfile, TransactionHistory
)
from .services import (
    calculate_loan_eligibility,
    check_investment_limits,
    calculate_group_analytics
)

class GroupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.group = SavingsGroup.objects.create(
            name='Test Group',
            risk_tolerance='LOW',
            tier_level=1
        )
        self.membership = GroupMembership.objects.create(
            user=self.user,
            group=self.group,
            role='MEMBER'
        )

    def test_group_creation(self):
        self.assertEqual(self.group.name, 'Test Group')
        self.assertEqual(self.group.tier_level, 1)
        self.assertEqual(self.group.total_balance, Decimal('0'))

    def test_contribution(self):
        contribution = Contribution.objects.create(
            member=self.membership,
            amount=Decimal('1000.00'),
            transaction_type='DEPOSIT'
        )
        self.group.refresh_from_db()
        self.assertEqual(self.group.total_balance, Decimal('1000.00'))

class LoanTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.group = SavingsGroup.objects.create(
            name='Test Group',
            risk_tolerance='LOW'
        )
        self.membership = GroupMembership.objects.create(
            user=self.user,
            group=self.group
        )
        self.contribution = Contribution.objects.create(
            member=self.membership,
            amount=Decimal('1000.00'),
            transaction_type='DEPOSIT'
        )

    def test_loan_creation(self):
        loan = Loan.objects.create(
            borrower=self.membership,
            amount=Decimal('500.00'),
            interest_rate=Decimal('10.00'),
            due_date=timezone.now() + timedelta(days=30)
        )
        self.assertEqual(loan.status, 'PENDING')

    def test_loan_eligibility(self):
        eligibility = calculate_loan_eligibility(self.membership)
        self.assertEqual(eligibility, Decimal('3000.00'))  # 3x contributions

class InvestmentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.group = SavingsGroup.objects.create(
            name='Test Group',
            risk_tolerance='MEDIUM',
            tier_level=2
        )
        self.membership = GroupMembership.objects.create(
            user=self.user,
            group=self.group
        )
        self.contribution = Contribution.objects.create(
            member=self.membership,
            amount=Decimal('10000.00'),
            transaction_type='DEPOSIT'
        )

    def test_investment_creation(self):
        investment = Investment.objects.create(
            group=self.group,
            investment_type='UNIT_TRUST',
            amount=Decimal('5000.00'),
            current_value=Decimal('5000.00'),
            provider='Test Provider',
            annual_return_rate=Decimal('10.00')
        )
        self.assertEqual(investment.amount, Decimal('5000.00'))

    def test_investment_limits(self):
        can_invest = check_investment_limits(self.group)
        self.assertTrue(can_invest)

class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_profile_creation(self):
        profile = UserProfile.objects.get(user=self.user)
        self.assertFalse(profile.is_verified)

    def test_profile_verification(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.is_verified = True
        profile.save()
        self.assertTrue(profile.is_verified)

class TransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.group = SavingsGroup.objects.create(
            name='Test Group',
            risk_tolerance='LOW'
        )
        self.membership = GroupMembership.objects.create(
            user=self.user,
            group=self.group
        )

    def test_transaction_history_creation(self):
        contribution = Contribution.objects.create(
            member=self.membership,
            amount=Decimal('1000.00'),
            transaction_type='DEPOSIT'
        )
        transaction = TransactionHistory.objects.filter(
            user=self.user,
            transaction_type='CONTRIBUTION'
        ).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, Decimal('1000.00'))

class AnalyticsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.group = SavingsGroup.objects.create(
            name='Test Group',
            risk_tolerance='MEDIUM'
        )
        self.membership = GroupMembership.objects.create(
            user=self.user,
            group=self.group
        )
        self.contribution = Contribution.objects.create(
            member=self.membership,
            amount=Decimal('5000.00'),
            transaction_type='DEPOSIT'
        )
        self.investment = Investment.objects.create(
            group=self.group,
            investment_type='UNIT_TRUST',
            amount=Decimal('2000.00'),
            current_value=Decimal('2200.00'),
            provider='Test Provider',
            annual_return_rate=Decimal('10.00')
        )

    def test_group_analytics(self):
        analytics = calculate_group_analytics(self.group)
        self.assertEqual(analytics['total_investments'], Decimal('2000.00'))
        self.assertTrue('investment_returns' in analytics)
