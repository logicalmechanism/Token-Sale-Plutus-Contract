from django.urls import path

from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('wallet', views.wallet, name='wallet'),
    path('buy', views.buy_from_smart_contract, name='buy'),
    path('sell', views.sell_to_smart_contract, name='sell'),
    path('order', views.processing_order, name='order'),
    path('split', views.create_collateral, name='split'),
    path('error', views.error_page, name='error'),
    path('start_contract', views.starting_a_contract, name='start_contract'),
    path('', views.index, name=''),
]