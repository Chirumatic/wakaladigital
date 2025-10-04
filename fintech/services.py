from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import models
from datetime import timedelta
from decimal import Decimal
from .models import (
    Loan, Investment, Contribution, Notification,
    TransactionHistory, UserProfile, SavingsGroup
)

def send_verification_email(user, token):
    """Send account verification email"""
    subject = 'Verify your Wakala Digital account'
    message = f'Click the link to verify your account: {settings.SITE_URL}/verify/{token}/'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_password_reset_email(user, token):
    """Send password reset email"""
    subject = 'Reset your Wakala Digital password'
    message = f'Click the link to reset your password: {settings.SITE_URL}/reset-password/{token}/'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def calculate_loan_eligibility(member):
    """Calculate how much a member can borrow"""
    total_contributions = Contribution.objects.filter(
        member=member,
        transaction_type='DEPOSIT'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Can borrow up to 3 times their total contributions
    return total_contributions * Decimal('3.0')

def check_investment_limits(group):
    """Check if a group can make more investments based on their tier"""
    total_investments = Investment.objects.filter(group=group).aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    if group.tier_level == 1:
        return total_investments < group.total_balance * Decimal('0.3')  # 30% limit
    elif group.tier_level == 2:
        return total_investments < group.total_balance * Decimal('0.5')  # 50% limit
    else:
        return total_investments < group.total_balance * Decimal('0.7')  # 70% limit

def create_loan_notification(loan):
    """Create notification for loan status changes"""
    Notification.objects.create(
        user=loan.borrower.user,
        title=f'Loan {loan.status.lower()}',
        message=f'Your loan request for {loan.amount} has been {loan.status.lower()}',
        notification_type='ALERT'
    )

def check_and_update_loan_status():
    """Check for overdue loans and update their status"""
    overdue_loans = Loan.objects.filter(
        status='APPROVED',
        due_date__lt=timezone.now()
    )
    for loan in overdue_loans:
        loan.status = 'DEFAULTED'
        loan.save()
        Notification.objects.create(
            user=loan.borrower.user,
            title='Loan Defaulted',
            message=f'Your loan of {loan.amount} is overdue',
            notification_type='PAYMENT_DUE'
        )

def update_investment_values():
    """Update current values of investments based on their return rates"""
    investments = Investment.objects.all()
    for investment in investments:
        returns = investment.calculate_returns()
        investment.current_value = investment.amount + returns
        investment.save()

def process_group_upgrade(group):
    """Check and process group tier upgrades"""
    if group.tier_level < 3:
        total_balance = group.total_balance
        member_count = group.members.count()
        avg_balance = total_balance / member_count if member_count > 0 else 0
        
        if group.tier_level == 1 and avg_balance >= Decimal('1000000'):  # 1M threshold
            group.tier_level = 2
            group.save()
            create_group_upgrade_notification(group)
        elif group.tier_level == 2 and avg_balance >= Decimal('5000000'):  # 5M threshold
            group.tier_level = 3
            group.save()
            create_group_upgrade_notification(group)

def create_group_upgrade_notification(group):
    """Create notification for group tier upgrade"""
    for member in group.members.all():
        Notification.objects.create(
            user=member,
            title='Group Tier Upgraded',
            message=f'Your group {group.name} has been upgraded to Tier {group.tier_level}',
            notification_type='MILESTONE'
        )

def calculate_group_analytics(group):
    """Calculate analytics for group dashboard"""
    now = timezone.now()
    month_ago = now - timedelta(days=30)
    
    # Monthly contribution growth
    current_month_contributions = Contribution.objects.filter(
        member__group=group,
        date__gte=month_ago,
        transaction_type='DEPOSIT'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Investment performance
    investments = Investment.objects.filter(group=group)
    total_investment = sum(inv.amount for inv in investments)
    current_value = sum(inv.current_value for inv in investments)
    investment_return = ((current_value - total_investment) / total_investment * 100) if total_investment > 0 else 0
    
    # Loan statistics
    active_loans = Loan.objects.filter(
        borrower__group=group,
        status='APPROVED'
    ).count()
    
    return {
        'monthly_contributions': current_month_contributions,
        'total_investments': total_investment,
        'investment_returns': investment_return,
        'active_loans': active_loans
    }
