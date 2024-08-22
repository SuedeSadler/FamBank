from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, Contribution
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .forms import GroupCreationForm
from django.db.models import Sum

def homepage(request):
    return render(request, 'savings/homepage.html')

from django.db.models import Q

@login_required
def dashboard(request):
    # Fetch groups where the user is either the manager or a member
    groups = Group.objects.filter(Q(manager=request.user) | Q(contributions__member=request.user)).distinct()

    # Fetch all contributions made by the logged-in user
    contributions = Contribution.objects.filter(member=request.user)

    context = {
        'groups': groups,
        'contributions': contributions,
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
    contributions = Contribution.objects.filter(group=group)

    total_contributions = contributions.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'group': group,
        'contributions': contributions,
        'total_contributions': total_contributions,
    }

    return render(request, 'savings/group_detail.html', context)