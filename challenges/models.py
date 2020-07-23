from django.db import models

# Create your models here.
# pylint: disable=no-member
class User(models.Model):
    id=models.AutoField(primary_key=True)
    username=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    salt=models.CharField(max_length=100)
    created=models.DateTimeField('created')
    objects = models.Manager()
    def __str__(self):
        return self.username

class Challenge(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    category=models.CharField(max_length=100)
    reward=models.IntegerField(default=0)
    top=models.IntegerField()
    created=models.DateTimeField('created')
    objects = models.Manager()
    def __str__(self):
        return self.name
    
class UserChallenge(models.Model):
    id=models.AutoField(primary_key=True)
    id_user=models.ForeignKey(User, on_delete=models.CASCADE)
    id_challenge=models.ForeignKey(Challenge, on_delete=models.CASCADE)
    point=models.IntegerField(default=0)
    created=models.DateTimeField('created')
    objects = models.Manager()
