"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import SaleInfo.views
import django.contrib.auth.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', SaleInfo.views.home),
    url(r'^SaleInfo/home$', SaleInfo.views.home, name='home'),
    url(r'^SaleInfo/sign_in$', django.contrib.auth.views.login, {'template_name':'SaleInfo/sign_in.html'}, name='sign_in'),
    url(r'^SaleInfo/sign_up$', SaleInfo.views.sign_up, name='sign_up'),
    
    # Jae - profile and edit profile
    url(r'^SaleInfo/my_profile$', SaleInfo.views.my_profile, name='my_profile'),
    url(r'^SaleInfo/edit_profile$', SaleInfo.views.edit_profile, name='edit_profile'),
    url(r'^SaleInfo/profile_photo/(?P<user_id>\d+)$', SaleInfo.views.profile_photo, name='profile_photo'),
    
    url(r'^SaleInfo/get_sales_information$', SaleInfo.views.get_sales_information, name='get_sales_information'),
    url(r'^SaleInfo/get_favorite_info$', SaleInfo.views.get_favorite_info, name='get_favorite_info'),
    
    url(r'^SaleInfo/store_map/(?P<brand_id>\d+)/(?P<sale_info_id>\d+)$', SaleInfo.views.store_map, name='store_map'),
    url(r'^SaleInfo/find_stores$', SaleInfo.views.find_stores, name='find_stores'),

    url(r'^SaleInfo/sign_in_find$', SaleInfo.views.sign_in_find, name='sign_in_find'),
    url(r'^SaleInfo/home_find$', SaleInfo.views.home_find, name='home_find'),
    url(r'^SaleInfo/favorite_find$', SaleInfo.views.favorite_find, name='favorite_find'),
    url(r'^SaleInfo/brand_find$', SaleInfo.views.brand_find, name='brand_find'),

    # Emily - Brand functions
    url(r'^SaleInfo/brand$', SaleInfo.views.brand, name='brand'),
    url(r'^SaleInfo/add_brand$', SaleInfo.views.add_brand, name='add_brand'),
    url(r'^SaleInfo/brand_photo/(?P<brand_id>\d+)$', SaleInfo.views.brand_photo, name='brand_photo'),

    url(r'^SaleInfo/favorite$', SaleInfo.views.favorite, name='favorite'),
    url(r'^confirm/(?P<user_name>.*)/(?P<get_token>.*)$', SaleInfo.views.confirm, name='confirm'),
    url(r'^SaleInfo/logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    url(r'^SaleInfo/confirm/(?P<user_name>.*)/(?P<get_token>.*)$', SaleInfo.views.confirm, name='confirm'),             
    url(r'^SaleInfo/follow/(?P<brand_id>\d+)$', SaleInfo.views.follow_brand, name='follow_brand'),
    url(r'^SaleInfo/unfollow/(?P<brand_id>\d+)$', SaleInfo.views.unfollow_brand, name='unfollow_brand'),

    # Emily- Coupon Exchange Page
    url(r'^SaleInfo/coupon_exchange$', SaleInfo.views.coupon_exchange, name='coupon_exchange'),
    url(r'^SaleInfo/coupon_exchange/coupon_photo/(?P<coupon_id>\d+)$', SaleInfo.views.coupon_photo, name='coupon_photo'),
    
    # Emily- Upload Coupon System
    url(r'^SaleInfo/coupon_exchange/add_coupon$', SaleInfo.views.add_coupon, name='add_coupon'),
    url(r'^SaleInfo/coupon_exchange/delete_coupon/(?P<coupon_id>\d+)$', SaleInfo.views.delete_coupon, name='delete_coupon'),
    url(r'^SaleInfo/coupon_exchange/check_expired$', SaleInfo.views.check_expired, name='check_expired'),
    
    # Emily- Coupon Exchange System
    url(r'^SaleInfo/coupon_exchange/add_exchange_coupon/(?P<coupon_id>\d+)$', SaleInfo.views.add_exchange_coupon, name='add_exchange_coupon'), 
    url(r'^SaleInfo/coupon_exchange/finish_exchange_coupon/(?P<match_coupon_id>\d+)/(?P<match_own_coupon_id>\d+)$', SaleInfo.views.finish_exchange_coupon, name='finish_exchange_coupon'), 

    # Emily- get coupons function(Returns all recent additions in the database, as JSON)
    url(r'^SaleInfo/coupon_exchange/get_coupons_owned$', SaleInfo.views.get_coupons_owned, name='get_coupons_owned'),
    url(r'^SaleInfo/coupon_exchange/get_coupons_owned/(?P<time>.+)$', SaleInfo.views.get_coupons_owned, name='get_coupons_owned_time'),

    # Emily- get coupons changes function(Returns all recent changes to the database, as JSON)
    url(r'^SaleInfo/coupon_exchange/get_changes_owned/$', SaleInfo.views.get_changes_owned, name='get_changes_owned'),
    url(r'^SaleInfo/coupon_exchange/get_changes_owned/(?P<time>.+)/$', SaleInfo.views.get_changes_owned, name='get_changes_owned_time'),

    # Emily- Rate Coupon
    url(r'^SaleInfo/coupon_exchange/rate_coupon/(?P<coupon_id>\d+)$', SaleInfo.views.rate_coupon, name='rate_coupon'),

    # Emily- Reset password
    url(r'^reset$', django.contrib.auth.views.password_reset, {'template_name':'SaleInfo/password_reset_form.html',
                                                               'from_email':'weijaehe@gmail.com',
                                                               'post_reset_redirect':'/reset/done'},
                                                                name='password_reset'),
    url(r'^reset/done$', django.contrib.auth.views.password_reset_done, {'template_name':'SaleInfo/password_reset_done.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', django.contrib.auth.views.password_reset_confirm, 
                                                                {'template_name':'SaleInfo/password_reset_confirm.html', 'post_reset_redirect':'/done'}, 
                                                                name='password_reset_confirm'),
    url(r'^done$', django.contrib.auth.views.password_reset_complete, {'template_name':'SaleInfo/password_reset_complete.html'}, name='reset_complete'),

    # Emily- Clean Coupon
    url(r'^SaleInfo/coupon_exchange/clean_coupon$', SaleInfo.views.clean_coupon, name='clean_coupon'),
]
