from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Item(models.Model):
    name = models.CharField(max_length=20, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.PositiveIntegerField(verbose_name='Цена')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Товар')
    amount = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return f"{self.amount} x {self.item.name} ({self.user})"
    
    class Meta:
        unique_together = ('user', 'item')
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    paid_at = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name='Время покупки')
    stripe_session_id = models.CharField(max_length=255, unique=True, verbose_name='ID покупки')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return f"Заказ #{self.id} — {self.user}"
    
    class Meta:
        verbose_name='Заказ'
        verbose_name_plural='Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name='Товар')
    amount = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return f"{self.amount} x {self.item.name}"
    
    class Meta:
        verbose_name='Товар в заказе'
        verbose_name_plural='Товары в заказе'
