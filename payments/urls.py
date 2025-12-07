from django.urls import path
from . import views

urlpatterns = [
    path('premium/', views.premium_pricing, name='premium_pricing'),
    path('premium/features/', views.premium_features, name='premium_features'),
    path('payment/<str:plan_type>/', views.process_payment, name='process_payment'),
    path('payment/pending/<str:transaction_id>/', views.payment_pending, name='payment_pending'),
    path('payment/status/<str:transaction_id>/', views.check_payment_status, name='check_payment_status'),
    path('payment/success/', views.premium_success, name='premium_success'),
]