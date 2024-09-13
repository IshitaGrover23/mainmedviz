from django.db import models
from django.utils import timezone

class Prediction(models.Model):
    """
    Model to store diabetes prediction results and input data.
    """
    input_data = models.JSONField(help_text="Input data for the prediction")
    result = models.CharField(max_length=50, help_text="Prediction result")
    timestamp = models.DateTimeField(default=timezone.now, help_text="Time of prediction")

    def __str__(self):
        return f"Prediction {self.id}: {self.result} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']