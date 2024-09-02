from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, Contribution
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .forms import GroupCreationForm
from django.db.models import Sum, Value, DecimalField
from .forms import AddMemberForm
from django.db.models import Q
from .forms import InvitationForm
from .models import Invitation
from .forms import ContributionForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Invitation
from datetime import date
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User



@login_required
def add_contribution(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Check if the current user is the owner of the group
    if request.user != group.manager:
        return redirect('group_detail', group_id=group_id)

    if request.method == 'POST':
        form = ContributionForm(request.POST, group=group)
        if form.is_valid():
           contribution = form.save(commit=False)
           contribution.group = group
           contribution.member == form.cleaned_data['member']
           contribution.date = date.today()
           contribution.save()
           return redirect('group_detail', group_id=group_id)
    else:
        form = ContributionForm(group=group)

    return render(request, 'savings/add_contribution.html', {'form': form, 'group': group})

@login_required
def profile(request):
    return render(request, 'savings/profile.html')

@login_required
def respond_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id, user=request.user)

    if request.method == 'POST':
        if request.POST.get('action') == 'accept':
            invitation.status = 'Accepted'
            invitation.group.members.add(request.user)  # Add the user to the group
        else:
            invitation.status = 'Declined'
        invitation.save()
        return redirect('dashboard')

    return redirect('dashboard')


@login_required
def send_invitation(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.manager:
        return redirect('group_detail', group_id=group_id)  # Only the manager can send invitations

    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.group = group
            invitation.invited_by = request.user
            invitation.save()
            return redirect('group_detail', group_id=group_id)
    else:
        form = InvitationForm()

    return render(request, 'savings/send_invitation.html', {'form': form, 'group': group})

@login_required
def add_member(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.manager:
        return redirect('group_detail', group_id=group_id)  # Only the manager can add members

    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            group.members.add(user)
            return redirect('group_detail', group_id=group_id)
    else:
        form = AddMemberForm()

    return render(request, 'savings/add_member.html', {'form': form, 'group': group})

def homepage(request):
    return render(request, 'savings/homepage.html')



@login_required
def dashboard(request):
    # Fetch groups where the user is either the manager or a member
    groups = Group.objects.filter(
        Q(manager=request.user) | Q(members=request.user)
    ).distinct()

    # Fetch all contributions made by the logged-in user
    contributions = Contribution.objects.filter(member=request.user)

    # Fetch pending invitations for the logged-in user
    invitations = Invitation.objects.filter(user=request.user, status='Pending')

    context = {
        'groups': groups,
        'contributions': contributions,
        'invitations': invitations,
    }

    return render(request, 'savings/dashboard.html', context)

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "savings/register.html", {"form": form})

@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupCreationForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.manager = request.user  # Set the current user as the manager of the group
            group.save()
            return redirect('dashboard')  # Redirect to the dashboard after creating the group
    else:
        form = GroupCreationForm()
    
    return render(request, 'savings/create_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    # Fetch all members of the group, including the manager
    members = group.members.all() | User.objects.filter(id=group.manager.id)

    # Get contributions and include members with no contributions
    contributions_by_member = []
    for member in members:
        total_contributed = Contribution.objects.filter(group=group, member=member).aggregate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        )['total']
        contributions_by_member.append({
            'member': member.username,
            'total': total_contributed
        })

    total_contributions = Contribution.objects.filter(group=group).aggregate(Sum('amount'))['amount__sum'] or 0

    # Fetch contributions ordered by date descending
    contributions = Contribution.objects.filter(group=group).order_by('-date')

    context = {
        'group': group,
        'contributions': contributions,  # This is where the contributions are passed
        'contributions_by_member': contributions_by_member,
        'total_contributions': total_contributions,
    }

    return render(request, 'savings/group_detail.html', context)
