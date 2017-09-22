from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Max
from django.utils.html import escape
from SaleInfo.choices import * 
from django.db.models import Q
from datetime import datetime
# Create your models here.

class Brand(models.Model):
	url = models.URLField(default='')
	brand_name = models.CharField(max_length=200)
	brand_image = models.ImageField(upload_to='brand_picture', default='')
	
	def __str__(self):
		return self.brand_name

	@staticmethod
	def get_all_brands():
		return Brand.objects.all()

class Sales_Info(models.Model):
    brand = models.ForeignKey(Brand)
    content = models.TextField(max_length=2000)
    number_of_likes = models.PositiveIntegerField(default=0)
    number_of_dislikes = models.IntegerField(default=0)

    @property
    def html(self):
        return "<div class='container'> \
                    <div class='jumbotron my-sign-in-blog grad'> \
                        <div class='col-xs-6 col-sm-3 brand-placeholder'> \
                            <img src='/SaleInfo/brand_photo/%s' width='150' height='150' alt='Generic placeholder thumbnail'> \
                        </div> \
                        <h2 class='saleinfo-title'>%s</h2> \
                        <p class='saleinfo-content'>%s</p> \
                        <p> \
                        <a class='btn btn-lg btn-danger' href='/SaleInfo/store_map/%s/%s' role='button'><span class='glyphicon glyphicon-map-marker' aria-hidden='true'></span> Find Stores</a> \
                        <label>&nbsp;&nbsp;&nbsp;&nbsp;</label> \
                        <a class='btn btn-lg btn-warning' href='%s' role='button' target='_blank'><span class='glyphicon glyphicon-home' aria-hidden='true'></span> Sale Home Page</a> \
                        <label>&nbsp;&nbsp;&nbsp;&nbsp;</label> \
                        <a class='btn btn-lg btn-primary' href='https://www.facebook.com/sharer/sharer.php?u=ec2-52-91-6-230.compute-1.amazonaws.com/SaleInfo/store_map/%s/%s' target='_blank'><span class='glyphicon glyphicon-share' aria-hidden='true'></span> Share on Facebook</a> \
                        </p> \
                    </div> \
                </div>" % (self.brand.id, self.brand.brand_name, self.content, self.brand.id, self.id, self.brand.url, self.brand.id, self.id)

class Price_Tracking(models.Model):
	url = models.URLField(max_length=200, default='')
	price = models.PositiveIntegerField()

class Profile(models.Model):
    user = models.OneToOneField(User)
    picture = models.ImageField(upload_to='profile_picture', default='profile_picture/head.png', blank=True)
    reputation = models.FloatField(default=0, blank=True)
    number_of_rates = models.PositiveIntegerField(default=0, blank=True)
    favorite_sales_info = models.ManyToManyField(Sales_Info, blank=True)
    favorite_brands = models.ManyToManyField(Brand, related_name="favorite_brands", blank=True)
    price_tracking = models.ManyToManyField(Price_Tracking, blank=True)

class Comment(models.Model):
	user_profile = models.ForeignKey(Profile)
	content = models.TextField(max_length=2000)
	sales_info = models.ForeignKey(Sales_Info)

class Coupon(models.Model):
	profile = models.ForeignKey(Profile)
	brand = models.ForeignKey(Brand)
	expiration_date = models.DateTimeField()
	last_changed = models.DateTimeField(auto_now=True)
	content = models.TextField(max_length=200, blank=True)
	picture = models.ImageField(upload_to='coupon_picture', default='coupon_picture/coupon.jpg', blank=True)
	valid = models.BooleanField(default=True)
	in_exchange = models.BooleanField(default=False)
	category = models.CharField(
		max_length=2,
		choices=DISCOUNT_CATEGORY_CHOICES,
		default=PERCENTOFF,
	)
	request_coupon_brand = models.ForeignKey(Brand, related_name="request_coupon_brand", null=True)
	request_coupon_category = models.CharField(
		max_length=2,
		choices=DISCOUNT_CATEGORY_CHOICES,
		default=PERCENTOFF,
	)
	previous_profile = models.ForeignKey(Profile, related_name="previous_profile", null=True)
	rated = models.BooleanField(default=False)



	def __str__(self):
		return "%s %s (%s)" % (escape(self.brand.brand_name), self.content, self.expiration_date)

	def get_match_coupons(self, profile, time="1970-01-01T00:00+00:00"):
		return Coupon.objects.exclude(profile=profile).filter(valid=True, in_exchange=True, 
									 last_changed__gt=time, brand=self.request_coupon_brand, 
									 category=self.request_coupon_category,request_coupon_brand=self.brand, 
									 request_coupon_category=self.category).distinct().order_by('-expiration_date')
	@staticmethod
	def get_max_time(profile):
		return Coupon.objects.filter(profile=profile).aggregate(Max('last_changed'))['last_changed__max'] or "1970-01-01T00:00+00:00"

	@staticmethod
	def get_coupons_by_profile(profile, time="1970-01-01T00:00+00:00"):
		return Coupon.objects.filter(profile=profile, valid=True, 
									 last_changed__gt=time).distinct().order_by('-expiration_date')

	@staticmethod
	def get_changes_by_profile(profile, time="1970-01-01T00:00+00:00"):
		return Coupon.objects.filter(Q(profile=profile) | Q(previous_profile=profile), last_changed__gt=time).distinct().order_by('-expiration_date')

	@staticmethod
	def get_valid_coupons():
		return Coupon.objects.filter(valid=True).distinct().order_by('-expiration_date')

	@property
	def owned_html(self):
		return "<li id='coupon_%d' profile_id='%d'><div class='jumbotron my-coupon-blog transparent'><h2 style='display: inline-block;' class='saleinfo-title'>%s </h2>&nbsp;&nbsp;&nbsp;<button style='display: inline-block;' class='btn btn-danger' id='delete-coupon-btn'>Delete</button><h3 class='saleinfo-content'>Category: %s <br>%s</h3><h4 class='saleinfo-content'>Exchange Status: %s<br>Request Brand: %s<br>Request Category: %s</h4><h5 class='saleinfo-content'>Expiration Date:%s</h5><img src='/SaleInfo/coupon_exchange/coupon_photo/%d' alt='%s' width='300'></div>" % (self.id, 
				self.profile.id, self.brand, self.category, self.content, self.in_exchange, self.request_coupon_brand, self.request_coupon_category, self.expiration_date, self.id, escape(self.profile.user.username))

	@property
	def exchange_html(self):
		return "<option id='%d'>%s [%s] %s expired on (%s)</option>" % (self.id, 
				self.brand, self.category, self.content, self.expiration_date)

	@property
	def match_html(self):
		return "<li id='match_%d'><div class='jumbotron my-coupon-blog transparent' id='match_html'><h2 class='saleinfo-title'>%s</h2><h3 class='saleinfo-content'>Category: %s <br>%s</h3><h4 class='saleinfo-content'>Owned by %s %s <br>Reputation: %s </h4><h5 class='saleinfo-content'>Expiration Date:%s</h5><img src='/SaleInfo/coupon_exchange/coupon_photo/%d' alt='%s' width='300'><hr><div id='match_own_coupon'></div></div>" % (self.id, 
				self.brand, self.category, self.content, escape(self.profile.user.first_name), escape(self.profile.user.last_name), escape(self.profile.reputation), self.expiration_date, self.id, escape(self.profile.user.username))

	@property
	def match_own_html(self):
		return "<h2 class='saleinfo-title'>%s</h2><h3 class='saleinfo-content'>Category: %s <br>%s</h3><h4 class='saleinfo-content'>Owned by %s %s <br>Reputation: %s </h4><h5 class='saleinfo-content'>Expiration Date:%s</h5><img src='/SaleInfo/coupon_exchange/coupon_photo/%d' alt='%s' width='300'><hr>" % (self.brand, self.category, self.content, escape(self.profile.user.first_name), escape(self.profile.user.last_name), escape(self.profile.reputation), self.expiration_date, self.id, escape(self.profile.user.username))
	
	@property
	def is_past_due(self):
	    return self.expiration_date < timezone.now()

class Exchange(models.Model):
	match_coupon = models.ForeignKey(Coupon, related_name='match_coupon')
	match_own_coupon = models.ForeignKey(Coupon, related_name='match_own_coupon')
	deleted = models.BooleanField(default=False)
	last_changed = models.DateTimeField(auto_now=True)






