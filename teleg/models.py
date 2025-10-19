from django.db import models
from data.models import User_profile, Obj, System, Atributes, Data

# Create your models here.
class Alarm(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=50, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    status=models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged')
    ], default='active')
    system = models.ForeignKey(Atributes, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.severity}'


class Bot (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    system = models.ForeignKey(Atributes, on_delete=models.CASCADE)
    tocken = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name