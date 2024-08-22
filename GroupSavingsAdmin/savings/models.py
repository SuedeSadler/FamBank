from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_groups')
    members = models.ManyToManyField(User, related_name='group_memberships', blank=True)  # Change related_name
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Invitation(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, related_name='sent_invitations', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Declined', 'Declined')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitation to {self.user.username} for {self.group.name}"

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
