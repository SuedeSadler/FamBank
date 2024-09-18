from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
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
from collections import defaultdict
from django.http import JsonResponse, HttpResponse
import requests
from django.conf import settings  # Import the settings
from django.shortcuts import redirect
from urllib.parse import urlencode
import jwt
import datetime
import secrets
import base64

def generate_jwt():
    private_key = settings.PRIVATE_KEY

    # Ensure private key is in bytes
    if isinstance(private_key, str):
        private_key = private_key.encode('utf-8')

    # Load the private key object
    private_key_obj = load_pem_private_key(private_key, password=None, backend=default_backend())

    client_id = settings.CLIENT_ID

    # Generate a random nonce and state
    nonce = secrets.token_hex(16)
    state = secrets.token_hex(16)

    # Define the payload for the JWT
    payload = {
        "iss": client_id,  # Client ID provided by the API provider
        "aud": "https://api-nomatls.apicentre.middleware.co.nz",  # Audience
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5),  # Expiration time
        "nbf": datetime.datetime.now(datetime.timezone.utc),  # Not before time
        "scope": "openid accounts",  # Scope for account information
        "response_type": "code id_token",  # Response type as per the documentation
        "redirect_uri": "https://ropuapp-ekbhcfaseqf2gjh3.australiacentral-01.azurewebsites.net/oauth/callback/",  # Replace with your actual callback URL
        "client_id": client_id,  # Client ID from settings
        "nonce": nonce,  # Unique nonce to prevent replay attacks
        "state": state  # Optional state to track the request
    }

    # Sign the JWT using the loaded private key
    headers = {
        "kid": settings.KEY_ID  # Use the Key ID if required by the API
    }

    token = jwt.encode(payload, private_key_obj, algorithm='RS256', headers=headers)

    return token, nonce, state

def start_oauth(request):
    base_url = "https://api-nomatls.apicentre.middleware.co.nz/middleware-nz-sandbox/v1.0/oauth/authorize"
    
    # Generate JWT
    jwt_token, nonce, state = generate_jwt()
    # Display the token in the browser for debugging
    #return HttpResponse(f"Generated JWT Token: {jwt_token}")

    client_id = settings.CLIENT_ID
    redirect_url = 'https://ropuapp-ekbhcfaseqf2gjh3.australiacentral-01.azurewebsites.net/oauth/callback/'  # Your registered callback URL
    
    params = {
        "scope": "openid accounts",  # or "openid payments" if you're doing payments
        "response_type": "code id_token",
        "client_id": client_id,
        "redirect_uri": redirect_url,
        "request": jwt_token,  # The JWT you just generated
        "nonce": nonce,  # Replace with a unique nonce
        "state": state,  # Replace with a unique state
        "Intent Identifier": "your_account_request_id_or_payment_id"
    }
    
    # Construct the full authorization URL
    auth_url = f"{base_url}?{urlencode(params)}"
    
    return redirect(auth_url)

def oauth_callback(request):
    

    # Token exchange URL
    token_url = 'https://api-nomatls.apicentre.middleware.co.nz/middleware-nz-sandbox/v1.0/oauth/token'
    
    # Get client_id and client_secret from settings
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET

    # Encode the client ID and client secret for Basic Auth
    credentials = f"{client_id}:{client_secret}".encode('utf-8')
    auth_header = base64.b64encode(credentials).decode('utf-8')

    # Set headers for the POST request
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Data for the token request
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'https://ropuapp-ekbhcfaseqf2gjh3.australiacentral-01.azurewebsites.net/oauth/callback/',  # Your registered callback URL
    }

    # Make the POST request to exchange the authorization code for an access token
    response = requests.post(token_url, data=data, headers=headers)

    if response.status_code == 200:
        tokens = response.json()
        # Handle tokens (access_token, id_token, refresh_token)
        return HttpResponse(f"Access Token: {tokens.get('access_token')}")
    else:
        # Handle error from the token exchange step
        return HttpResponse(f"Token exchange failed: {response.text}", status=response.status_code)
    
# def oauth_callback(request):
#     # Check for error parameters in the callback URL
#     error = request.GET.get('error')
#     error_description = request.GET.get('error_description')

#     if error:
#         # Handle the error case
#         return HttpResponse(f"Error: {error_description}")

#     # Proceed with the normal flow if no error is present
#     code = request.GET.get('code')
#     if not code:
#         return HttpResponse("Authorization code not found.", status=400)

#     token_url = 'https://api-nomatls.apicentre.middleware.co.nz/middleware-nz-sandbox/v1.0/oauth/token'
#     client_id = settings.CLIENT_ID
#     client_secret = settings.CLIENT_SECRET
#     redirect_url = 'https://ropuapp-ekbhcfaseqf2gjh3.australiacentral-01.azurewebsites.net/oauth/callback/'

#     # Create the Basic Auth header by base64 encoding client_id:client_secret
#     auth_string = f"{client_id}:{client_secret}"
#     encoded_auth_string = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

#     headers = {
#         'Authorization': f'Basic {encoded_auth_string}',
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }

#     data = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': redirect_url,
#         'scope': 'openid accounts'
#     }

#     response = requests.post(token_url, headers=headers, data=data)

#     if response.status_code == 200:
#         tokens = response.json()
#         # Handle tokens (access_token, id_token, refresh_token)
#         return HttpResponse(f"Access Token: {tokens.get('access_token')}")
#     else:
#         # Log the response for debugging
#         print(f"Token exchange failed: {response.text}")
#         # Handle error from the token exchange step
#         return HttpResponse(f"Token exchange failed: {response.text}", status=response.status_code)


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)[:10]  # Limit to 10 results
        results = [{'id': user.id, 'username': user.username} for user in users]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

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
        user_id = request.POST.get('user')  # Get the selected user ID from the hidden field
        if user_id:
            invited_user = get_object_or_404(User, id=user_id)
            # Prevent sending duplicate invitations
            existing_invitation = Invitation.objects.filter(group=group, user=invited_user).exists()

            if not existing_invitation:
                # Create and save the invitation
                invitation = Invitation(group=group, user=invited_user, invited_by=request.user)
                invitation.save()
                return redirect('group_detail', group_id=group_id)
            else:
                return render(request, 'savings/send_invitation.html', {'group': group, 'error': 'User has already been invited.'})

    return render(request, 'savings/send_invitation.html', {'group': group})


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

     # Fetch contributions ordered by date descending
    contributions = Contribution.objects.filter(member=request.user).order_by('-date')
    
   
    
      # Add total contributions to each group
    for group in groups:
        group.total_contributions = Contribution.objects.filter(group=group).aggregate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        )['total']

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
    
    # Aggregate contributions by each member using a dictionary
    contributions_by_member = defaultdict(lambda: 0)

    # Sum the contributions for each member once
    for member in members:
        contributions = Contribution.objects.filter(group=group, member=member).aggregate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        )['total']
        contributions_by_member[member.username] = contributions

    # Convert to a list of dictionaries for easier template usage
    contributions_by_member = [{'member': member, 'total': total} for member, total in contributions_by_member.items()]

    # Get total contributions for the group
    total_contributions = Contribution.objects.filter(group=group).aggregate(Sum('amount'))['amount__sum'] or 0

    # Fetch contributions ordered by date descending
    contributions = Contribution.objects.filter(group=group).order_by('-date')

    context = {
        'group': group,
        'contributions': contributions,
        'contributions_by_member': contributions_by_member,
        'total_contributions': total_contributions,
    }

    return render(request, 'savings/group_detail.html', context)