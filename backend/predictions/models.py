from django.db import models

class Prediction(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	state = models.CharField(max_length=50)
	district = models.CharField(max_length=50)
	season = models.CharField(max_length=10)
	nitrogen = models.FloatField()
	phosphorus = models.FloatField()
	potassium = models.FloatField()
	ph = models.FloatField()
	top_crop = models.CharField(max_length=50)
	top_crop_suitability = models.FloatField()
	expected_yield_min = models.FloatField(null=True, blank=True)
	expected_yield_max = models.FloatField(null=True, blank=True)

	def __str__(self):
		return f"{self.timestamp} - {self.top_crop} ({self.state}, {self.district})"

import uuid

class KVK(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    official_id = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=255)
    
    # Administrative
    state = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    atari_zone = models.CharField(max_length=50, null=True, blank=True)
    
    # Organization
    host_organization = models.CharField(max_length=255, null=True, blank=True)
    host_organization_type = models.CharField(max_length=100, null=True, blank=True)
    
    # Contact
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    
    # Geospatial
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Data provenance
    source_name = models.CharField(max_length=255, null=True, blank=True)
    source_url = models.URLField(null=True, blank=True)
    source_verified_at = models.DateTimeField(null=True, blank=True)
    data_last_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Coordinate provenance
    coordinate_source = models.CharField(max_length=255, null=True, blank=True)
    coordinate_verified_at = models.DateTimeField(null=True, blank=True)
    coordinate_accuracy = models.CharField(max_length=100, null=True, blank=True)
    geocoding_status = models.CharField(max_length=50, null=True, blank=True)
    
    # Services
    has_soil_testing = models.BooleanField(null=True, blank=True)
    has_mobile_lab = models.BooleanField(null=True, blank=True)
    offers_expert_consultation = models.BooleanField(null=True, blank=True)
    soil_testing_price_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    soil_testing_price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Operational
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['state', 'district']),
        ]

    def __str__(self):
        return f"{self.name} ({self.district}, {self.state})"
