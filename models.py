from django.db import models

class WaterData(models.Model):
    ph          = models.FloatField()
    turbidity   = models.FloatField()
    temperature = models.FloatField()
    quality     = models.CharField(max_length=100)
    disease     = models.CharField(max_length=200)
    created_at  = models.DateTimeField(auto_now_add=True)

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
    answers    = models.TextField()  # stored as JSON string
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} — {self.risk_level} ({self.score})"

    class Meta:
        ordering     = ['-created_at']
        verbose_name = 'Survey Result'