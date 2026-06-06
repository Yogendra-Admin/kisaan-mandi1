from django.db import models
from accounts.models import CustomUser
from marketplace.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending / प्रतीक्षारत'),
        ('confirmed', 'Confirmed / पुष्टि'),
        ('dispatched', 'Dispatched / भेजा गया'),
        ('delivered', 'Delivered / वितरित'),
        ('cancelled', 'Cancelled / रद्द'),
    ]
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('upi', 'UPI'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending / प्रतीक्षारत'),
        ('paid', 'Paid / भुगतान हो गया'),
        ('failed', 'Failed / विफल'),
    ]
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    delivery_address = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.buyer.username}"

class Cart(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.product.price_per_unit * self.quantity

    class Meta:
        unique_together = ('buyer', 'product')

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message_en = models.CharField(max_length=255)
    message_hi = models.CharField(max_length=255)
    message_ne = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message_en}"

    @classmethod
    def send(cls, user, message_en, message_hi, message_ne):
        return cls.objects.create(
            user=user,
            message_en=message_en,
            message_hi=message_hi,
            message_ne=message_ne
        )
