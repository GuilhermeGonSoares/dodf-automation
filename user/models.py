from django.db import models
from django.contrib.auth.models import User
from mpc.models import Jurisdicionada, Unidade

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unidades = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='user_profiles', null=True)
    jurisdicionadas = models.ManyToManyField(Jurisdicionada, related_name='user_profiles')

