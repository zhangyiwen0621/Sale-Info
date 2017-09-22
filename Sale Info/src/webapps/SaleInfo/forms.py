from django import forms
from django.contrib.auth.models import User
from SaleInfo.models import *
from SaleInfo.choices import *
import re

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length = 20,
                               label = 'User Name')
    first_name = forms.CharField(max_length = 200,
                               label = 'First Name')
    last_name = forms.CharField(max_length = 200,
                               label = 'Last Name')
    password1 = forms.CharField(max_length = 200,
                                label = 'Password',
                                widget = forms.PasswordInput())
    password2 = forms.CharField(max_length = 200,
                                label = 'Re-type Password',
                                widget = forms.PasswordInput())
    email = forms.EmailField(help_text='Please enter a valid email address.',
                             label = 'Email')
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        email = cleaned_data.get('email')
        print(len(password1))
        if len(password1) < 7:
            raise forms.ValidationError("Password length has to be more than 6 characters.")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError("Email is already taken")
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)
        widgets = {'picture': forms.FileInput()}

class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length = 200,
                                 label = 'First Name')
    last_name = forms.CharField(max_length = 200,
                                label = 'Last Name')
    email = forms.CharField(max_length = 200,
                            label = 'Email')
    def clean(self):
        cleaned_data = super(EditProfileForm, self).clean()
        return cleaned_data

class BrandForm(forms.Form):
    url = forms.URLField()
    brand_name = forms.CharField(max_length=200)
    brand_image = forms.FileField(label='Brand Image')

    def clean_brand_name(self):
        brand_name = self.cleaned_data.get('brand_name')
        brand_exists = Brand.objects.filter(brand_name__exact=brand_name)
        if brand_exists and self.initial['brand_name'] != brand_name:
            raise forms.ValidationError('Brand name is already taken.')
        return brand_name

    def clean_url(self):
        url = self.cleaned_data.get('url')
        brand_exists = Brand.objects.filter(url__exact=url)
        if brand_exists and self.initial['url'] != url:
            raise forms.ValidationError('URL is already taken.')
        return url

    def save(self):
        new_brand = Brand(url=self.cleaned_data.get('url'), \
                          brand_name=self.cleaned_data.get('brand_name'), \
                          brand_image=self.cleaned_data.get('brand_image'))
        new_brand.save()
        return new_brand

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['brand','category','expiration_date','content','picture']
        widgets = {
                    'brand': forms.Select(attrs={'class': 'form-control'}),
                    'category': forms.Select(attrs={'class': 'form-control'}),
                    'picture': forms.FileInput(attrs={'id': 'coupon_picture'}),
                    'content': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'i.e. $5 off'}),
                    'expiration_date': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'datetimepicker', 'placeholder': 'i.e. 2006-10-25 14:30:59'}),
                  }


    def clean_expiration_date(self):
        expiration_date = self.cleaned_data.get('expiration_date')
        if expiration_date < timezone.now():
            raise forms.ValidationError('You entered an invalid coupon.')
        return expiration_date

    def save(self, coupon_instance):
        coupon_instance.brand = self.cleaned_data.get('brand')
        coupon_instance.category = self.cleaned_data.get('category')
        coupon_instance.expiration_date = self.cleaned_data.get('expiration_date')
        coupon_instance.previous_profile = coupon_instance.profile

        if self.cleaned_data.get('content'):
            coupon_instance.content = self.cleaned_data.get('content')
        
        if self.cleaned_data.get('picture'):
            coupon_instance.picture = self.cleaned_data.get('picture')
        
        coupon_instance.save()
        return coupon_instance

class ExchangeForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['request_coupon_brand', 'request_coupon_category']
        widgets = {
                    'request_coupon_brand': forms.Select(attrs={'class': 'form-control'}),
                    'request_coupon_category': forms.Select(attrs={'class': 'form-control'}),
                  }

    def save(self, exchange_instance):
        if self.cleaned_data.get('request_coupon_brand'):
            exchange_instance.request_coupon_brand = self.cleaned_data.get('request_coupon_brand')
        
        if self.cleaned_data.get('request_coupon_category'):
            exchange_instance.request_coupon_category = self.cleaned_data.get('request_coupon_category')
        
        exchange_instance.save()
        return exchange_instance   
        
