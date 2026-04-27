from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ==========================================
# 1. 商品分类模型
# ==========================================
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="分类描述")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name


# ==========================================
# 2. 商品模型
# ==========================================
class Item(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('available', '可购买'),
        ('sold', '已售出'),
    )

    title = models.CharField(max_length=200, verbose_name="商品标题")
    description = models.TextField(verbose_name="商品描述")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="所属分类")
    condition = models.CharField(max_length=100, verbose_name="成色")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="卖家")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="当前状态")
    is_deleted = models.BooleanField(default=False, verbose_name="是否已删除")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "二手商品"
        verbose_name_plural = verbose_name


# ==========================================
# 3. 商品图片模型
# ==========================================
class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images', verbose_name="所属商品")
    image = models.ImageField(upload_to='items/', verbose_name="商品图片")

    def __str__(self):
        return f"{self.item.title}的图片"

    class Meta:
        verbose_name = "商品图片"
        verbose_name_plural = verbose_name


# ==========================================
# 4. 购物车模型
# ==========================================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return f"{self.user.username}的购物车"

    class Meta:
        verbose_name = "用户购物车"
        verbose_name_plural = verbose_name


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="所属购物车")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="商品")
    quantity = models.PositiveIntegerField(default=1, verbose_name="数量")

    def __str__(self):
        return f"{self.item.title} x {self.quantity}"

    class Meta:
        verbose_name = "购物车条目"
        verbose_name_plural = verbose_name


# ==========================================
# 5. 订单模型
# ==========================================
class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="买家")
    items = models.ManyToManyField(Item, verbose_name="包含商品")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单总价")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="下单时间")
    is_paid = models.BooleanField(default=True, verbose_name="是否已支付")

    def __str__(self):
        return f"订单 #{self.id} - {self.buyer.username}"

    class Meta:
        verbose_name = "交易订单"
        verbose_name_plural = verbose_name