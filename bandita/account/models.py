# your_app/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Account(models.Model):
    email       = models.EmailField('email', unique=True)
    password    = models.CharField('password', max_length=128)
    prenume     = models.CharField('prenume', max_length=30)
    nume        = models.CharField('nume', max_length=30)
    companie    = models.CharField('companie', max_length=100, blank=True)
    adresa1     = models.CharField('adresa_1', max_length=255)
    adresa2     = models.CharField('adresa_2', max_length=255, blank=True)
    oras        = models.CharField('oras', max_length=50)
    cod_postal  = models.CharField('cod postal', max_length=20)
    tara        = models.CharField('tara', max_length=50)
    judet       = models.CharField('judet', max_length=50)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.prenume} {self.nume} <{self.email}>"
