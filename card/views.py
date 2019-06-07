from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from card.models import CardInfo

#тут все на столько сырое, что скоро выростут грибы

@login_required(redirect_field_name='login_card')
def home(request):
    context = {}
    return render(request, 'card/home.html', context)


def login_card(request):
    context = {}
    if request.method == "POST":
        cardID = request.POST['username']
        password = request.POST['password']
        print(cardID in request.session)
        User = get_user_model()
        card = authenticate(request, cardID=cardID, password=password)
        if card:
            login(request, card)
            return HttpResponseRedirect(reverse('home'))
        else:
            if User.objects.filter(cardID=cardID).exists():
                print(request.session.get(cardID))
                if cardID in request.session:
                    request.session[cardID] += 1
                else: 
                    request.session[cardID] = 1
                request.session.modified = True
                print(cardID in request.session)
                #request.session.set_expiry(300)
                #request.session[cardID] = request.session.get(cardID, 0) + 1
                if request.session.get(cardID) >= 3:
                    print("some2")
                    card = User.objects.get(cardID=cardID)
                    print(card.balance)
                    card.is_active = False
                    card.save()
                return HttpResponseRedirect(reverse('login_card'))
            context['error'] = 'Wrong card data!'
            return render(request, 'card/login.html', context)
    else:
        return render(request, 'card/login.html', context)


@login_required(redirect_field_name='login_card')
def balance(request):
    return render(request, 'card/balance.html')


@login_required(redirect_field_name='login_card')
def refill(request):
    context = {}
    if request.method == "POST":
        summ = int(request.POST['summ'])
        card = request.user
        card.balance=card.balance+summ
        card.save()
        context['success'] = 'Operation done successful'
        return render(request, 'card/refill.html', context)
    else:
        return render(request, 'card/refill.html', context)


@login_required(redirect_field_name='login_card')
def cash(request):
    context = {}
    if request.method == "POST":
        summ = int(request.POST['summ'])
        card = request.user
        if card.balance >= summ:
            card.balance=card.balance-summ
            card.save()
            context['comment'] = 'Operation done successful'
            return render(request, 'card/cash.html', context)
        else:
            context['comment'] = 'Insufficient funds in your account!'
            return render(request, 'card/cash.html', context)

    else:
        return render(request, 'card/cash.html', context)


@login_required(redirect_field_name='login_card')
def pin_change(request):
    context = {}
    if request.method == "POST":
        card = request.user
        current_pin = card.password
        new_pin = request.POST['password']
        if current_pin != new_pin:
            if pin_valid(new_pin):
                card.set_password(new_pin)
                card.save()
                context['comment'] = 'Your pin was changed'
                return render(request, 'card/pin_change.html', context)
            else:
                context['comment'] = 'Incorrect pin format. Try another one'
                return render(request, 'card/pin_change.html', context)
        else: 
            context['comment'] = 'New pin can not be the same old'
            return render(request, 'card/pin_change.html', context)
    else:
        return render(request, 'card/pin_change.html', context)
        
        
@login_required(redirect_field_name='login_card')
def logout_card(request):
    logout(request)
    return render(request, 'card/login.html')


def pin_valid(pin):
    return False if len(pin)!=4 and pin[0]==pin[1] and pin[2]==pin[3] else True
