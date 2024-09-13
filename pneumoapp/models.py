from django.db import models

class ChestXRay(models.Model):
    image = models.ImageField(upload_to='chest_xrays/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=100, blank=True)  
    probability = models.FloatField(null=True, blank=True)
    patient_name = models.CharField(max_length=100)

    def __str__(self):
        return f"ChestXRay {self.id} - {self.result}"