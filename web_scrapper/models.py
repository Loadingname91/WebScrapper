from django.db import models


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200,unique=True)
    product_price = models.CharField(max_length=200)
    product_description = models.TextField(blank=True)
    product_category = models.CharField(max_length=200)
    product_images = models.TextField(blank=True)
    product_features = models.TextField(blank=True)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name_plural = 'Product Descriptions'
        ordering = ['product_category']


class ProductResources(models.Model):
    product_url = models.TextField(blank=False)
    product_collected_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Task(models.Model):
    task_id = models.CharField(max_length=200, primary_key=True)
    task_status = models.CharField(max_length=200)
    task_created_date = models.DateTimeField(auto_now_add=True)
    task_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_id

    class Meta:
        verbose_name_plural = 'Task Details'
        ordering = ['task_created_date']