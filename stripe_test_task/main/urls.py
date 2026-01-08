from . import views 

from django.urls import path


urlpatterns = [
    path('', views.home, name='home'),
    path('orders/', views.show_orders, name='orders'),
    path('cart/', views.show_cart, name='cart'),
    path('make_order/', views.make_order, name='make_order'),
    path('item/<int:pk>/remove/', views.remove_item_view, name='remove_item'),
    path('item/<int:pk>/decrease/', views.decrease_item_in_cart, name='decrease_item'),
    path('item/<int:pk>/add/', views.add_to_cart_view, name='add_to_cart'),
    path('item/<int:pk>/', views.get_item_view, name='item_detail'),
    path('buy/<int:pk>/', views.buy_item_view, name='buy_item_view')
]
