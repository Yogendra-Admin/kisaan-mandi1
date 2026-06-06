from django.db import models

class MarketPrice(models.Model):
    crop_name = models.CharField(max_length=100)
    crop_name_hi = models.CharField(max_length=100, blank=True)
    crop_name_ne = models.CharField(max_length=100, blank=True)
    mandi_name = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    modal_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='Quintal')
    date = models.DateField()
    trend = models.CharField(max_length=10, choices=[('up','Up'),('down','Down'),('stable','Stable')], default='stable')

    def save(self, *args, **kwargs):
        from marketplace.translation import translate_text
        if self.crop_name:
            self.crop_name_hi = translate_text(self.crop_name, 'hi')
            self.crop_name_ne = translate_text(self.crop_name, 'ne')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.crop_name} - {self.mandi_name} ({self.date})"

    class Meta:
        ordering = ['-date']
