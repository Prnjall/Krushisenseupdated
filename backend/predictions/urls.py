from django.urls import path
from . import views

urlpatterns = [
    path('health', views.health_check_view, name='health_check'),
    path('predict-crop', views.predict_crop_view, name='predict_crop'),
        # path('predict-yield', views.predict_yield_view, name='predict_yield'),
]
