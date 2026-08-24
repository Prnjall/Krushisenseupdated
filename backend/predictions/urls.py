from django.urls import path
from . import views
from .interoperability import views as interop_views

urlpatterns = [
    path('health', views.health_check_view, name='health_check'),
    path('predict-crop', views.predict_crop_view, name='predict_crop'),
    path('weather', views.get_weather_view, name='get_weather'),
    path('satellite-test', views.satellite_test_view, name='satellite_test'),
    path('satellite-ndvi', views.satellite_ndvi_view, name='satellite_ndvi'),
    path('agri-advisory', views.agri_advisory_view, name='agri_advisory'),
    path('disease-detection', views.disease_detection_view, name='disease_detection'),
    path('disease-advisory', views.disease_advisory_view, name='disease_advisory'),
    path('v1/interop/advisory/', interop_views.interop_advisory_view, name='interop_advisory'),
        # path('predict-yield', views.predict_yield_view, name='predict_yield'),
]
