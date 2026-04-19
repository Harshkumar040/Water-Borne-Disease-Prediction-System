from django.db import models

class WaterData(models.Model):
    ph = models.FloatField()
    turbidity = models.FloatField()
    temperature = models.FloatField()
    quality = models.CharField(max_length=100)
    disease = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
