from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.utils import timezone

from SaleInfo.models import *
from operator import attrgetter
from SaleInfo.forms import *
from django.urls import reverse

from mimetypes import guess_type

from django.http import HttpResponse, Http404

from django.db import transaction
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse

from django.views.decorators.csrf import ensure_csrf_cookie

import re

# Create your views here.

@login_required
def home(request):
    return render(request, 'SaleInfo/home.html', {})

def get_sales_information(request):
    context = {}
    res = Sales_Info.objects.all()
    context = {"sale_infos": res}
    return render(request, 'sale_infos.json', context, content_type='application/json')

@login_required
def get_favorite_info(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    favorite_brands = user_profile.favorite_brands.all()
    sale_infos = Sales_Info.objects.filter(brand__in=favorite_brands)
    context = {"sale_infos": sale_infos}
    return render(request, 'sale_infos.json', context, content_type='application/json')

def store_map(request, brand_id, sale_info_id):
    brand = get_object_or_404(Brand, id=brand_id)
    sale_info = get_object_or_404(Sales_Info, id=sale_info_id)
    context = {}
    context['brand_name'] = brand.brand_name
    context['sale_info_content'] = sale_info.content
    context['brand_id'] = brand_id
    context['sale_info_id'] = sale_info_id
    return render(request, 'SaleInfo/map.html', context)

def find_stores(request):
    sale_info = get_object_or_404(Sales_Info, id=request.POST["sale_info_id"])
    context = {}
    context['brand_name'] = request.POST["brand_name"]
    context['sale_info_content'] = sale_info.content
    context['brand_id'] = request.POST["brand_id"]
    context['zip_code'] = request.POST["zip_code"]
    context['sale_info_id'] = request.POST["sale_info_id"]
    return render(request, 'SaleInfo/map.html', context)

def sign_in_find(request):
    regex = re.compile(".*" + request.POST["brand_name"] + ".*", re.IGNORECASE)
    brand_set = set()
    for brand in Brand.objects.all():
        if re.match(regex, brand.brand_name) is not None:
            brand_set.add(brand)
    sale_infos = Sales_Info.objects.filter(brand__in=brand_set)
    context = {}
    context['sale_infos'] = sale_infos
    return render(request, 'SaleInfo/sign_in_find.html', context)

@login_required
def home_find(request):
    regex = re.compile(".*" + request.POST["brand_name"] + ".*", re.IGNORECASE)
    brand_set = set()
    for brand in Brand.objects.all():
        if re.match(regex, brand.brand_name) is not None:
            brand_set.add(brand)
    sale_infos = Sales_Info.objects.filter(brand__in=brand_set)
    context = {}
    context['sale_infos'] = sale_infos
    return render(request, 'SaleInfo/home_find.html', context)

@login_required
def favorite_find(request):
    regex = re.compile(".*" + request.POST["brand_name"] + ".*", re.IGNORECASE)
    user_profile = get_object_or_404(Profile, user=request.user)
    favorite_brands = user_profile.favorite_brands.all()
    brand_set = set()
    for brand in favorite_brands:
        if re.match(regex, brand.brand_name) is not None:
            brand_set.add(brand)
    sale_infos = Sales_Info.objects.filter(brand__in=brand_set)
    context = {}
    context['sale_infos'] = sale_infos
    return render(request, 'SaleInfo/favorite_find.html', context)

@login_required
def brand_find(request):
    regex = re.compile(".*" + request.POST["brand_name"] + ".*", re.IGNORECASE)
    brand_set = set()
    for brand in Brand.objects.all():
        if re.match(regex, brand.brand_name) is not None:
            brand_set.add(brand)
    context = {}
    user_profile = get_object_or_404(Profile, user=request.user)
    followed_brands = user_profile.favorite_brands.all()
    find_followed = set(followed_brands).intersection(brand_set)
    context['all_brands'] = brand_set
    context['followed_brand'] = find_followed
    return render(request, 'SaleInfo/brand_find.html', context)

@transaction.atomic
def sign_up(request):
    context = {}
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'SaleInfo/sign_up.html', context)
    
    form = RegistrationForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'SaleInfo/sign_up.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'], \
                                        password=form.cleaned_data['password1'], \
                                        email=form.cleaned_data['email'], \
                                        first_name=form.cleaned_data['first_name'], \
                                        last_name=form.cleaned_data['last_name'], \
                                        is_active=False)
    new_user.save()
    new_profile = Profile(user=new_user)
    profile_form = ProfileForm(request.POST, instance=new_profile)
    profile_form.save()
    
    token = default_token_generator.make_token(new_user)
    email_body = """Congratuation!!!
        http://%s%s
        """%(request.get_host(), reverse('confirm', args=(new_user.username, token)))
    
    send_mail(subject="Verify",
    message=email_body,
    from_email="weijaehe@gmail.com",
    recipient_list=[new_user.email],
    fail_silently=False)

    context['email'] = form.cleaned_data['email']
    context['topic'] = "Congratulation!! You need to confirm in your email: "
    return render(request, 'SaleInfo/confirm.html', context)

def confirm(request, user_name, get_token):
    currUser = get_object_or_404(User, username=user_name)
    if default_token_generator.check_token(currUser, get_token):
        currUser.is_active = True
        currUser.save()
        login(request, currUser)
        return redirect('/SaleInfo/home')
    else:
        raise Http404

@login_required
def my_profile(request):
    currProfile = get_object_or_404(Profile, user=request.user)
    isMyself = True
    context = {'currUsername': request.user.username, \
               'currFirstname': request.user.first_name, \
               'currLastname': request.user.last_name, \
               'currReputation': currProfile.reputation, \
               'currNumberOfRates': currProfile.number_of_rates, \
               'isMyself': isMyself, \
               'id': request.user.id}

    context['brands'] = currProfile.favorite_brands.all()
    context['own_coupons'] = Coupon.get_coupons_by_profile(profile=currProfile)
    return render(request, 'SaleInfo/profile.html', context)

@login_required
def edit_profile(request):
    context = {}
    context['id'] = request.user.id
    currProfile = get_object_or_404(Profile, user=request.user)
    currFavorites = currProfile.favorite_brands.all()
    currUser = request.user
    if request.method == 'POST':
        # use form to store image file
        form = ProfileForm(request.POST, request.FILES, instance=currProfile)
        # use form1 to check the other fields
        form1 = EditProfileForm(request.POST)
        if not form.is_valid() or not form1.is_valid():
            context['form'] = form
            context['form1'] = form1
            context['first_name'] = currUser.first_name
            context['last_name'] = currUser.last_name
            context['email'] = currUser.email
            return render(request, 'SaleInfo/edit_profile.html', context)
        form.cleaned_data['favorite_brands'] = currFavorites
        form.save()
        currUser.first_name = form1.cleaned_data['first_name']
        currUser.last_name = form1.cleaned_data['last_name']
        currUser.email = form1.cleaned_data['email']
        currUser.save()
        return redirect(reverse('my_profile'))
    
    form = ProfileForm(instance=currProfile)
    context['form'] = form
    context['first_name'] = currUser.first_name
    context['last_name'] = currUser.last_name
    context['email'] = currUser.email
    return render(request, 'SaleInfo/edit_profile.html', context)

@login_required
def profile_photo(request, user_id):
    currUser = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=currUser)
    if not profile.picture:
        raise Http404
    return HttpResponse(profile.picture)

# brand ------Start
@login_required
def brand(request):
    context = {}
    user_profile = get_object_or_404(Profile, user=request.user)
    context['all_brands'] = Brand.get_all_brands()
    context['followed_brand'] = user_profile.favorite_brands.all()
    return render(request, 'SaleInfo/brand.html', context)

def add_brand(request):
    context = {}

    if request.method == 'GET':
        context['form'] = BrandForm()
        return render(request, 'SaleInfo/add_brand.html', context)

    form = BrandForm(request.POST, request.FILES)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'SaleInfo/add_brand.html', context)

    new_brand = form.save()
    return redirect(reverse('brand'))

def brand_photo(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    if not brand.brand_image:
        raise Http404

    content_type = guess_type(brand.brand_image.name)
    return HttpResponse(brand.brand_image, content_type=content_type)
# brand ------End

@login_required
def favorite(request):
    return render(request, 'SaleInfo/favorite.html', {})

#follow a brand
@login_required
def follow_brand(request, brand_id):
    context = {}
    brand_to_follow = get_object_or_404(Brand, id=brand_id)
    currentUser = request.user
    user_profile = get_object_or_404(Profile, user=currentUser)
    if brand_to_follow not in user_profile.favorite_brands.all():
        user_profile.favorite_brands.add(brand_to_follow)
    return HttpResponse("")

#unfollow a brand
@login_required()
def unfollow_brand (request, brand_id):
    context = {}
    brand_to_follow = get_object_or_404(Brand, id=brand_id)
    currentUser = request.user
    user_profile = get_object_or_404(Profile, user=currentUser)
    if brand_to_follow in user_profile.favorite_brands.all():
        user_profile.favorite_brands.remove(brand_to_follow)
    return HttpResponse("")

# Emily-Coupon Exchange System
@login_required
def coupon_exchange(request):
    context = {}
    context['coupon_form'] = CouponForm()
    context['exchange_form'] = ExchangeForm()
    return render(request, 'SaleInfo/coupon_exchange.html', context)
    
@login_required
def coupon_photo(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if not coupon.picture:
        raise Http404

    content_type = guess_type(coupon.picture.name)
    return HttpResponse(coupon.picture, content_type=content_type)


@login_required
def add_coupon(request):
    profile = Profile.objects.get(user=request.user)
    new_coupon = Coupon(profile=profile)
    coupon_form = CouponForm(request.POST, request.FILES, instance=new_coupon)

    if not coupon_form.is_valid():
        return HttpResponse("form invalid")

    # Creates the new coupon from the valid form data
    coupon_form.save(coupon_instance=new_coupon)

    return HttpResponse("")

@login_required
def delete_coupon(request, coupon_id):
    try:
        coupon_to_delete = Coupon.objects.get(id=coupon_id)
        coupon_to_delete.in_exchange = False
        coupon_to_delete.valid = False  # Just mark items as deleted.
        coupon_to_delete.save()
    except ObjectDoesNotExist:
        return HttpResponse("The coupon did not exist")

    return HttpResponse("")  # Empty response on success.

@login_required
def check_expired(request):
    context = {}
    coupons = Coupon.get_valid_coupons()
    
    for coupon in coupons:
        if coupon.is_past_due:
            coupon.in_exchange = False
            coupon.valid = False
            coupon.save()

    return HttpResponse("")

@login_required
def add_exchange_coupon(request, coupon_id):
    try:
        coupon_to_exchange = get_object_or_404(Coupon, id=coupon_id)
        coupon_to_exchange.in_exchange = True
        
        exchange_form = ExchangeForm(request.POST, instance=coupon_to_exchange)

        if not exchange_form.is_valid():
            return HttpResponse("form invalid")

        exchange_form.save(exchange_instance=coupon_to_exchange)

    except ObjectDoesNotExist:
        return HttpResponse("The coupon did not exist")

    return HttpResponse("")

@login_required
def finish_exchange_coupon(request, match_coupon_id, match_own_coupon_id):
    try:
        match_coupon = get_object_or_404(Coupon, id=match_coupon_id, valid=True, in_exchange=True)
    except ObjectDoesNotExist:
        return HttpResponse("The match_coupon does not exist")
    
    try:
        match_own_coupon = get_object_or_404(Coupon, id=match_own_coupon_id, valid=True, in_exchange=True)
    except ObjectDoesNotExist:
        return HttpResponse("The match_own_coupon does not exist")
    
    try:
        exchange = Exchange.objects.get(match_coupon=match_own_coupon, match_own_coupon=match_coupon, deleted=False)
        
        # Switch owner
        match_own_coupon.previous_profile = match_own_coupon.profile
        match_coupon.previous_profile = match_coupon.profile
        match_own_coupon.profile = match_coupon.previous_profile
        match_coupon.profile = match_own_coupon.previous_profile

        # Change coupon status
        match_coupon.in_exchange = False
        match_own_coupon.in_exchange = False
        match_coupon.rated = False
        match_own_coupon.rated = False

        match_coupon.save()
        match_own_coupon.save()

        # Remove exchange
        exchange.deleted = True
        exchange.save()

        exchanges = Exchange.objects.filter(Q(match_coupon=match_own_coupon)|Q(match_coupon=match_coupon), deleted=False)
        for exchange_coupon in exchanges:
            exchange_coupon.deleted = True
            exchange_coupon.save()


    except Exchange.DoesNotExist:
        exchange=Exchange.objects.get_or_create(match_coupon=match_coupon, match_own_coupon=match_own_coupon, deleted=False)
        return HttpResponse("")

    return HttpResponse("succeed")

@login_required
def get_coupons_owned(request, time="1970-01-01T00:00+00:00"):
    profile = Profile.objects.get(user=request.user)
    max_time = Coupon.get_max_time(profile=profile)
    coupons = Coupon.get_coupons_by_profile(profile=profile, time=time)
    in_exchange_owned_coupons = coupons.filter(valid=True, in_exchange=True)
    match_coupons = []
    match_own_coupons = []
    exchanges = []
    for coupon in in_exchange_owned_coupons:
        match_coupons_of_one = coupon.get_match_coupons(profile=profile)
        match_coupons.extend(match_coupons_of_one)
        for match_coupon in match_coupons_of_one:
            match_own_coupons.append(coupon)
            try:
                exchange = Exchange.objects.get(match_coupon=match_coupon, match_own_coupon=coupon, deleted=False)
                exchange_status = True
            except Exchange.DoesNotExist:
                exchange_status = False
            exchanges.append(exchange_status)
        
    context = {"profile_id": profile.id, "max_time": max_time, "coupons": coupons, "match_coupons": match_coupons, "match_own_coupons": match_own_coupons, "exchanges":exchanges}
    return render(request, 'coupons.json', context, content_type='application/json')

@login_required
def get_changes_owned(request, time="1970-01-01T00:00+00:00"):
    profile = Profile.objects.get(user=request.user)
    max_time = Coupon.get_max_time(profile=profile)
    coupons = Coupon.get_changes_by_profile(profile=profile, time=time)
    owned_coupons = Coupon.get_coupons_by_profile(profile=profile)
    in_exchange_owned_coupons = owned_coupons.filter(valid=True, in_exchange=True)
    match_coupons = []
    match_own_coupons = []
    exchanges = []
    for coupon in in_exchange_owned_coupons:
        match_coupons_of_one = coupon.get_match_coupons(profile=profile)
        match_coupons.extend(match_coupons_of_one)
        for match_coupon in match_coupons_of_one:
            match_own_coupons.append(coupon)
            try:
                exchange = Exchange.objects.get(match_coupon=match_coupon, match_own_coupon=coupon, deleted=False)
                exchange_status = "True"
            except Exchange.DoesNotExist:
                exchange_status = "False"
            exchanges.append(exchange_status)
        
    context = {"profile_id": profile.id, "max_time": max_time, "coupons": coupons, "match_coupons": match_coupons, "match_own_coupons": match_own_coupons, "exchanges":exchanges}
    return render(request, 'coupons.json', context, content_type='application/json')

@login_required
def rate_coupon(request, coupon_id):

    coupon = get_object_or_404(Coupon, id=coupon_id)
    own_profile = get_object_or_404(Profile, user=request.user)
    previous_profile = coupon.previous_profile
    if previous_profile == own_profile or coupon.rated:
        return HttpResponse("")
    
    reputation_total = previous_profile.reputation*previous_profile.number_of_rates+int('0'+request.POST['rate'])
    previous_profile.number_of_rates = previous_profile.number_of_rates+1
    previous_profile.reputation = reputation_total/previous_profile.number_of_rates
    previous_profile.save()
    
    coupon.rated = True
    coupon.save()

    return HttpResponse("")

def clean_coupon(request):
    Coupon.objects.all().delete()
    return redirect('/SaleInfo/home')
    
