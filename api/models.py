from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=255)
    registration_date = models.DateField()
    registration_number = models.CharField(max_length=100)
    address = models.TextField()
    contact_person = models.CharField(max_length=255)
    departments = models.JSONField()
    number_of_employees = models.IntegerField()
    contact_phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Employee(models.Model):
    company = models.ForeignKey(Company, related_name='employees', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=100, unique=True, null=True)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    date_started = models.DateField()
    date_left = models.DateField(null=True, blank=True)
    duties = models.TextField()

    def __str__(self):
        return self.name