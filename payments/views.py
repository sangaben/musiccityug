from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Payment, SubscriptionPlan
from accounts.models import UserProfile

def premium_pricing(request):
    """Premium pricing page"""
    plans = [
        {
            'name': 'Free',
            'price': 0,
            'period': 'forever',
            'description': 'Basic access to our music library',
            'features': [
                {'text': 'Access to all songs', 'included': True},
                {'text': 'Standard audio quality', 'included': True},
                {'text': 'Limited skips (5 per hour)', 'included': True},
                {'text': 'With occasional ads', 'included': True},
                {'text': 'Offline downloads', 'included': False},
                {'text': 'High quality audio', 'included': False},
                {'text': 'Unlimited skips', 'included': False},
                {'text': 'Ad-free experience', 'included': False},
                {'text': 'Early access to new releases', 'included': False},
                {'text': 'Exclusive content', 'included': False},
            ],
            'popular': False,
            'cta_text': 'Current Plan',
            'cta_disabled': True
        },
        {
            'name': 'Premium',
            'price': 4.99,
            'period': 'month',
            'description': 'Enhanced listening experience',
            'features': [
                {'text': 'Access to all songs', 'included': True},
                {'text': 'High quality audio (320kbps)', 'included': True},
                {'text': 'Unlimited skips', 'included': True},
                {'text': 'Ad-free experience', 'included': True},
                {'text': 'Offline downloads', 'included': True},
                {'text': 'Early access to new releases', 'included': True},
                {'text': 'Exclusive content', 'included': True},
                {'text': 'Priority support', 'included': True},
                {'text': 'Multiple device support', 'included': True},
                {'text': 'Custom playlists', 'included': True},
            ],
            'popular': True,
            'cta_text': 'Upgrade to Premium',
            'cta_disabled': False
        },
        # ... other plans
    ]
    
    # Check if user already has premium
    user_has_premium = False
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            user_has_premium = user_profile.is_premium
        except UserProfile.DoesNotExist:
            pass
    
    context = {
        'plans': plans,
        'user_has_premium': user_has_premium,
        'title': 'Upgrade to Premium'
    }
    return render(request, 'payments/pricing.html', context)

@login_required
def process_payment(request, plan_type):
    """Process premium payment with mobile money options"""
    if plan_type not in ['premium', 'premium_plus']:
        messages.error(request, 'Invalid plan selected.')
        return redirect('premium_pricing')
    
    # Get plan details
    plan_details = {
        'premium': {'name': 'Premium', 'price': 4.99, 'duration': 30},
        'premium_plus': {'name': 'Premium Plus', 'price': 9.99, 'duration': 30}
    }
    
    plan = plan_details[plan_type]
    
    if request.method == 'POST':
        # Get payment method and phone number
        payment_method = request.POST.get('payment_method')
        phone_number = request.POST.get('phone_number')
        network = request.POST.get('network')
        
        if not phone_number:
            messages.error(request, 'Please enter your phone number.')
            return redirect('process_payment', plan_type=plan_type)
        
        try:
            # Process mobile money payment
            if payment_method in ['mtn', 'airtel']:
                result = process_mobile_money_payment(
                    request.user,
                    plan_type,
                    phone_number,
                    network,
                    plan['price']
                )
                
                if result['success']:
                    messages.success(request, f'Payment initiated! {result["message"]}')
                    return redirect('payment_pending', transaction_id=result['transaction_id'])
                else:
                    messages.error(request, f'Payment failed: {result["message"]}')
                    return redirect('process_payment', plan_type=plan_type)
            
            else:
                messages.error(request, 'Invalid payment method selected.')
                return redirect('process_payment', plan_type=plan_type)
                
        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('process_payment', plan_type=plan_type)
    
    context = {
        'plan': plan,
        'plan_type': plan_type,
    }
    return render(request, 'payments/payment.html', context)

@login_required
def payment_pending(request, transaction_id):
    """Show payment pending page while waiting for mobile money confirmation"""
    context = {
        'transaction_id': transaction_id,
    }
    return render(request, 'payments/payment_pending.html', context)

@login_required
def check_payment_status(request, transaction_id):
    """API endpoint to check payment status"""
    # Check if payment was completed
    payment_completed = check_mobile_money_payment_status(transaction_id)
    
    if payment_completed:
        # Update user to premium
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.upgrade_to_premium('premium', 30)
        
        return JsonResponse({
            'status': 'completed',
            'message': 'Payment completed successfully!'
        })
    else:
        return JsonResponse({
            'status': 'pending',
            'message': 'Waiting for payment confirmation...'
        })

@login_required
def premium_success(request):
    """Premium subscription success page"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        context = {
            'user_profile': user_profile,
            'plan_name': user_profile.get_premium_plan_display() if user_profile.premium_plan else 'Premium'
        }
        return render(request, 'payments/success.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def premium_features(request):
    """Showcase premium features"""
    features = [
        {
            'icon': 'fas fa-download',
            'title': 'Offline Downloads',
            'description': 'Download your favorite songs and listen offline without using data.'
        },
        # ... other features
    ]
    
    user_has_premium = False
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            user_has_premium = user_profile.is_premium
        except UserProfile.DoesNotExist:
            pass
    
    context = {
        'features': features,
        'user_has_premium': user_has_premium
    }
    return render(request, 'payments/features.html', context)