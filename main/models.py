from django.db import models

class WaterData(models.Model):
    # existing fields — kept for history page compatibility
    ph          = models.FloatField(null=True, blank=True)
    turbidity   = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    quality     = models.CharField(max_length=100)
    disease     = models.CharField(max_length=200, default='')

    # new fields
    check_type  = models.CharField(max_length=10, default='quick')  # quick / detailed
    risk_level  = models.CharField(max_length=10, default='NORMAL')
    pincode     = models.CharField(max_length=10, default='000000')
    summary     = models.TextField(blank=True, default='')

    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class ContactQuery(models.Model):
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.subject}"

    class Meta:
        ordering            = ['-created_at']
        verbose_name        = 'Contact Query'
        verbose_name_plural = 'Contact Queries'

class SurveyResult(models.Model):
    user       = models.CharField(max_length=100)
    score      = models.IntegerField()
    risk_level = models.CharField(max_length=50)
    answers    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} — {self.risk_level} ({self.score})"

    class Meta:
        ordering     = ['-created_at']
        verbose_name = 'Survey Result'