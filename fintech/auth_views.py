from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Get CSRF token for the frontend
    """
    token = get_token(request)
    response = JsonResponse({'csrfToken': token})
    response['X-CSRFToken'] = token
    return response

@require_POST
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login view that accepts username and password
    """
    data = request.data
    username = data.get('username')
    password = data.get('password')
    
    if username is None or password is None:
        return Response({
            'error': 'Please provide both username and password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    login(request, user)
    return Response({'detail': 'Successfully logged in'})

@require_POST
@api_view(['POST'])
def logout_view(request):
    """
    Logout view
    """
    logout(request)
    return Response({'detail': 'Successfully logged out'})
