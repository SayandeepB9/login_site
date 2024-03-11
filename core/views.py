from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import SignupForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages as message
from login_site.settings import EMAIL_HOST_USER
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils.http import base64
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Create your views here.
def index(request):
    return render(request, 'core/index.html')

def contact(request):
    return render(request, 'core/contact.html')

def send_verification_email(user, request):
    subject = 'Activate your account.'
    current_site = get_current_site(request)
    print(user.pk, force_bytes(user.pk))
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generate_token.make_token(user)

    print(uid, token)

    # activating the account using the verification code
    message = render_to_string('core/verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': uid,
        'token': token
    })
    
    email = EmailMessage(subject, message, EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = 'html'
    email.send()

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False

            user.save()

            message.success(request, 'Account created successfully')

            send_verification_email(user, request)

            return redirect('/login/')
    else:
        form = SignupForm()

    form = SignupForm(request.POST)
    return render(request, 'core/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        print(uidb64, b'MTE=')
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        message.success(request, 'Account activated successfully')
        return redirect('/login/')
    else:
        raise Http404('Invalid activation link')

@login_required
def custom_logout(request):
    logout(request)
    return render(request, 'core/index.html')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')