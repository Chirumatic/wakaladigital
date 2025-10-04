from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils import timezone
import uuid

class TransactionHistory(models.Model):
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=50,
        choices=[
            ('CONTRIBUTION', 'Contribution'),
            ('LOAN', 'Loan'),
            ('INVESTMENT', 'Investment'),
            ('WITHDRAWAL', 'Withdrawal')
        ]
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed')
        ],
        default='PENDING'
    )

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class SavingsGroup(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    total_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')],
        default='LOW'
    )
    tier_level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    contribution_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=1000000.00
    )
    members = models.ManyToManyField(User, through='GroupMembership')

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(SavingsGroup, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[('ADMIN', 'Admin'), ('MEMBER', 'Member')],
        default='MEMBER'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    contribution_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=10000.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

class Contribution(models.Model):
    member = models.ForeignKey(GroupMembership, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(
        max_length=20,
        choices=[('DEPOSIT', 'Deposit'), ('WITHDRAWAL', 'Withdrawal')]
    )
    transaction = models.OneToOneField(
        TransactionHistory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new contributions
            # Create transaction history
            transaction = TransactionHistory.objects.create(
                user=self.member.user,
                transaction_type='CONTRIBUTION',
                amount=self.amount,
                balance_after=self.member.group.total_balance + self.amount,
                description=f"{self.transaction_type} to group {self.member.group.name}",
                status='COMPLETED'
            )
            self.transaction = transaction
            
            # Update group balance
            if self.transaction_type == 'DEPOSIT':
                self.member.group.total_balance += self.amount
            else:
                self.member.group.total_balance -= self.amount
            self.member.group.save()
            
        super().save(*args, **kwargs)

class Loan(models.Model):
    borrower = models.ForeignKey(GroupMembership, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    start_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('PAID', 'Paid'),
            ('DEFAULTED', 'Defaulted')
        ],
        default='PENDING'
    )
    transaction = models.OneToOneField(
        TransactionHistory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def calculate_interest(self):
        principal = self.amount
        rate = self.interest_rate / Decimal('100.00')
        time_diff = self.due_date - self.start_date
        time_in_years = Decimal(time_diff.days) / Decimal('365')
        interest = principal * rate * time_in_years
        return interest

    def total_repayment_amount(self):
        return self.amount + self.calculate_interest()

    def save(self, *args, **kwargs):
        if not self.pk and self.status == 'APPROVED':  # Only for new approved loans
            transaction = TransactionHistory.objects.create(
                user=self.borrower.user,
                transaction_type='LOAN',
                amount=self.amount,
                balance_after=self.borrower.group.total_balance - self.amount,
                description=f"Loan disbursement for {self.borrower.user.username}",
                status='COMPLETED'
            )
            self.transaction = transaction
            self.borrower.group.total_balance -= self.amount
            self.borrower.group.save()
        
        super().save(*args, **kwargs)

class Investment(models.Model):
    group = models.ForeignKey(SavingsGroup, on_delete=models.CASCADE)
    investment_type = models.CharField(
        max_length=20,
        choices=[
            ('UNIT_TRUST', 'Unit Trust'),
            ('BOND', 'Bond'),
            ('SHARES', 'Shares')
        ]
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateTimeField(auto_now_add=True)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    provider = models.CharField(max_length=100)  # e.g., "Stanbic", "Old Mutual"
    annual_return_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    transaction = models.OneToOneField(
        TransactionHistory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def calculate_returns(self, as_of_date=None):
        if not as_of_date:
            as_of_date = timezone.now()
        
        time_diff = as_of_date - self.date
        time_in_years = Decimal(time_diff.days) / Decimal('365')
        rate = self.annual_return_rate / Decimal('100.00')
        
        return self.amount * (Decimal('1.00') + rate) ** time_in_years - self.amount

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new investments
            transaction = TransactionHistory.objects.create(
                user=self.group.members.first(),  # Consider adding investment creator field
                transaction_type='INVESTMENT',
                amount=self.amount,
                balance_after=self.group.total_balance - self.amount,
                description=f"{self.investment_type} investment with {self.provider}",
                status='COMPLETED'
            )
            self.transaction = transaction
            self.group.total_balance -= self.amount
            self.group.save()
        
        super().save(*args, **kwargs)

class FinancialEducation(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    difficulty_level = models.CharField(
        max_length=20,
        choices=[('BASIC', 'Basic'), ('INTERMEDIATE', 'Intermediate'), ('ADVANCED', 'Advanced')]
    )
    points = models.IntegerField(default=0)

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(FinancialEducation, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('PAYMENT_DUE', 'Payment Due'),
            ('MILESTONE', 'Milestone'),
            ('ALERT', 'Alert'),
            ('EDUCATION', 'Education')
        ]
    )
