from django.db import models
from store.models import Product,Variation
from accounts.models import Account

# Create your models here.

class CartItem(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    variations = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):    # one product's = total
        return self.product.price * self.quantity
    
    def __unicode__(self): 
        return self.product 