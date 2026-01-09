from django.db import models
from accounts.models import Account
from store.models import Product,Variation

# Create your models here.
class Payment(models.Model):

    user = models.ForeignKey(Account,on_delete=models.CASCADE)

    payment_id = models.CharField(max_length=100,null=True)
    transaction_uuid = models.CharField(max_length=100,blank=True)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100) 
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self): 
        return self.payment_id

class Order(models.Model):
    
    user = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)

    order_number = models.CharField(max_length=20)
    transaction_uuid = models.CharField(max_length=100,blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    address1 = models.CharField(max_length=50)
    address2 = models.CharField(max_length=50,blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50) 

     
    payment_category =  [
        ('esewa','eSewa'),
        ('khalti','Khalti'),
        ('cod','Cash On Delivery'),
    ]

    payment_option = models.CharField(max_length=100,choices=payment_category,default='cod')
    order_total = models.FloatField()
    tax = models.FloatField() 
 
    STATUS =  [
        ('NEW','NEW'),
        ('ACCEPTED','ACCEPTED'), 
        ('COMPLETE','COMPLETE'),
        ('CANCELED','CANCELED'),
    ]

    status = models.CharField(max_length=100,choices=STATUS,default='NEW') 
    ip = models.CharField(blank=True,max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address1} {self.address2}'

    def __str__(self):
        return self.order_number
    
class OrderProduct(models.Model):

    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    payment =models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation,blank=True)

    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name