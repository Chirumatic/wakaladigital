from django.contrib import admin
from .models import (
    SavingsGroup, GroupMembership, Contribution,
    Loan, Investment, FinancialEducation,
    UserProgress, Notification
)

@admin.register(SavingsGroup)
class SavingsGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_balance', 'risk_tolerance', 'tier_level')
    search_fields = ('name',)

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'joined_at')
    list_filter = ('role',)

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'date', 'transaction_type')
    list_filter = ('transaction_type',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('borrower', 'amount', 'interest_rate', 'status', 'due_date')
    list_filter = ('status',)

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('group', 'investment_type', 'amount', 'current_value', 'provider')
    list_filter = ('investment_type', 'provider')

@admin.register(FinancialEducation)
class FinancialEducationAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty_level', 'points')
    list_filter = ('difficulty_level',)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'completed', 'score')
    list_filter = ('completed',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'created_at', 'read')
    list_filter = ('notification_type', 'read')
