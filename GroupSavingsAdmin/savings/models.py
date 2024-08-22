from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Contribution(models.Model):
    group = models.ForeignKey(Group, related_name='contributions', on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.member.username} - {self.amount}"

class ProgressEmbed(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    embed_link = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Embed for {self.group.name}"
