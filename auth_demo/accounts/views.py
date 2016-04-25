from django.shortcuts import render
from django.contrib import messages, auth
from accounts.forms import UserRegistrationForm, UserLoginForm
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.conf import settings
import datetime
import stripe
import arrow

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                customer = stripe.Customer.create(
                        email=form.cleaned_data['email'],
                        card=form.cleaned_data['stripe_id'],
                        plan='REG_MONTHLY',
                )
            except stripe.error.CardError, e:
                messages.error(request, "Your card was declined!")
            if customer:
                user = form.save()
                user.stripe_id = customer.id
                user.subscription_end = arrow.now().replace(weeks=+4).datetime
                user.save()    
                # Hmm
                form.save()
                user = auth.authenticate(email=request.POST.get('email'),
                                         password=request.POST.get('password1'))
                if user:
                    auth.login(request, user)
                    messages.success(request, "You have successfully registered")
                    return redirect(reverse('profile'))
                else:
                    messages.error(request, "unable to log you in at this time!")
            else:
                messages.error(request, "We were unable to take a payment with that card!")
    else:
        today = datetime.date.today()
        form = UserRegistrationForm()
 
    args = {'form': form, 'publishable': settings.STRIPE_PUBLISHABLE}
    args.update(csrf(request))
 
    return render(request, 'accounts/register.html', args)

@login_required(login_url='/accounts/login/')
def cancel_subscription(request):
    try:
        customer = stripe.Customer.retrieve(request.user.stripe_id)
        customer.cancel_subscription(at_period_end=True)
    except Exception, e:
        messages.error(request, e)
    return redirect('profile')

login_required(login_url='/accounts/login/')
def profile(request):
    return render(request, 'accounts/profile.html')

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(email=request.POST.get('email'),
                                    password=request.POST.get('password'))
 
            if user is not None:
                auth.login(request, user)
                messages.error(request, "You have successfully logged in")
                return redirect(reverse('profile'))
            else:
                form.add_error(None, "Your email or password was not recognised")
 
    else:
        form = UserLoginForm()
 
    args = {'form':form}
    args.update(csrf(request))
    return render(request, 'accounts/login.html', args)

def logout(request):
    auth.logout(request)
    messages.success(request, 'You have successfully logged out')
    # what is a redirect reverse
    return redirect('/')
