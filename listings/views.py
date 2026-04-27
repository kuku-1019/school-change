from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q,Sum
from django.http import JsonResponse
from .models import Item, Category, Cart, CartItem, Order
from .forms import ItemForm, ItemImageFormSet
from django.contrib.auth.models import User
from chat_messages.forms import CommentForm

# -----------------
# 核心浏览功能
# -----------------

def home(request):
    categories = Category.objects.all()
    # 修正：只显示已审核且未删除的商品
    recent_items = Item.objects.filter(status='available', is_deleted=False).order_by('-created_at')[:8]
    context = {
        'categories': categories,
        'recent_items': recent_items
    }
    return render(request, 'listings/home.html', context)


def item_list(request, category_id=None):
    categories = Category.objects.all()

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        # 增加 is_deleted=False 过滤
        items = Item.objects.filter(category=category, status='available', is_deleted=False).order_by('-created_at')
        title = f'{category.name}类别下的商品'
    else:
        # 增加 is_deleted=False 过滤
        items = Item.objects.filter(status='available', is_deleted=False).order_by('-created_at')
        title = '所有可购买商品'

    context = {
        'categories': categories,
        'items': items,
        'title': title
    }
    return render(request, 'listings/item_list.html', context)


def item_detail(request, item_id):
    # 这里不需要过滤 is_deleted，防止用户点击历史订单时报错，或者可以用 get_object_or_404 处理 404
    item = get_object_or_404(Item, id=item_id)

    # 2. 实例化评论表单 (新增代码)
    comment_form = CommentForm()

    context = {
        'item': item,
        'comment_form': comment_form  # 3. 将表单加入 context 字典
    }
    return render(request, 'listings/item_detail.html', context)

def search_items(request):
    query = request.GET.get('q', '')

    if query:
        # 增加 is_deleted=False 过滤
        items = Item.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            status='available',
            is_deleted=False
        ).order_by('-created_at')
    else:
        items = Item.objects.none()

    context = {
        'items': items,
        'query': query,
        'title': f'搜索结果: {query}'
    }
    return render(request, 'listings/search_results.html', context)


# -----------------
# AJAX 接口
# -----------------

def load_more_items(request):
    offset = int(request.GET.get('offset', 8))  # 默认从第8个开始取
    limit = 4  # 每次多加载4个
    # 增加 is_deleted=False 过滤
    items = Item.objects.filter(status='available', is_deleted=False).order_by('-created_at')[offset:offset + limit]

    data = []
    for item in items:
        img_url = item.images.first().image.url if item.images.first() else '/static/img/no-image.png'
        data.append({
            'id': item.id,
            'title': item.title,
            'price': str(item.price),
            'description': item.description,
            'image_url': img_url,
            'created_at': item.created_at.strftime('%Y-%m-%d')
        })
    return JsonResponse({'items': data})


# -----------------
# 商品管理 (CRUD)
# -----------------

@login_required
def new_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        formset = ItemImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.status = 'pending'  # 强制设为待审核
            item.save()

            for form in formset:
                if form.cleaned_data and form.cleaned_data.get('image'):
                    image = form.save(commit=False)
                    image.item = item
                    image.save()

            messages.success(request, '商品已发布，请等待管理员审核！')
            return redirect('my_items')
    else:
        form = ItemForm()
        formset = ItemImageFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': '发布新商品'
    }
    return render(request, 'listings/item_form.html', context)


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # 检查权限
    if item.seller != request.user:
        messages.error(request, '您没有权限编辑此商品！')
        return redirect('item_detail', item_id=item.id)

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        formset = ItemImageFormSet(request.POST, request.FILES, instance=item)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, '商品信息已更新！')
            return redirect('item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)
        formset = ItemImageFormSet(instance=item)

    context = {
        'form': form,
        'formset': formset,
        'title': '编辑商品',
        'item': item
    }
    return render(request, 'listings/item_form.html', context)


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # 检查权限
    if item.seller != request.user:
        messages.error(request, '您没有权限删除此商品！')
        return redirect('item_detail', item_id=item.id)

    if request.method == 'POST':
        # 修改为软删除
        item.is_deleted = True
        item.save()
        messages.success(request, '商品已成功删除！')
        return redirect('my_items')

    context = {'item': item}
    return render(request, 'listings/item_confirm_delete.html', context)


@login_required
def mark_sold(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # 检查权限
    if item.seller != request.user:
        messages.error(request, '您没有权限更改此商品状态！')
        return redirect('item_detail', item_id=item.id)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [s[0] for s in Item.STATUS_CHOICES]:
            item.status = status
            item.save()
            messages.success(request, f'商品状态已更新为{dict(Item.STATUS_CHOICES)[status]}！')
        return redirect('item_detail', item_id=item.id)

    context = {'item': item}
    return render(request, 'listings/mark_sold.html', context)


@login_required
def my_items(request):
    # 只显示未删除的商品
    items = Item.objects.filter(seller=request.user, is_deleted=False).order_by('-created_at')
    context = {
        'items': items,
        'title': '我的商品'
    }
    return render(request, 'listings/my_items.html', context)


# -----------------
# 购物车与订单
# -----------------

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # 防止卖家购买自己的商品
    if item.seller == request.user:
        messages.warning(request, '您不能购买自己的商品')
        return redirect('item_detail', item_id=item_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    # 检查是否已经在购物车
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        messages.info(request, '该商品已在购物车中')
    else:
        messages.success(request, '已加入购物车')

    return redirect('item_detail', item_id=item_id)


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    # 计算总价
    total_price = sum(item.item.price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'listings/cart.html', context)


# listings/views.py

@login_required  # 建议加上登录验证
def remove_from_cart(request, item_id):
    # 1. 获取要删除的商品对象
    item = get_object_or_404(Item, id=item_id)

    # 2. 获取当前用户的购物车
    # 使用 filter().first() 比 get() 更安全，防止购物车不存在时报错
    cart = Cart.objects.filter(user=request.user).first()

    if cart:
        # 3. 查找购物车里对应的条目并删除
        # CartItem 是连接购物车和商品的中间表
        CartItem.objects.filter(cart=cart, item=item).delete()
        messages.success(request, '商品已从购物车移除')

    # 4. 跳转回正确的购物车页面视图名 'view_cart'
    return redirect('view_cart')
@login_required
def checkout(request):
    if request.method != 'POST':
        messages.warning(request, '请从购物车页面点击结算')
        return redirect('view_cart')

    # 获取用户勾选的 CartItem ID 列表
    selected_cart_item_ids = request.POST.getlist('selected_items')

    if not selected_cart_item_ids:
        messages.warning(request, '您没有勾选任何商品进行结算')
        return redirect('view_cart')

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.warning(request, '购物车为空')
        return redirect('item_list')

    # 过滤出用户勾选的购物车条目
    # id__in 是 Django 的查找语法，匹配列表中的 ID
    target_cart_items = cart.items.filter(id__in=selected_cart_item_ids)

    if not target_cart_items.exists():
        messages.warning(request, '结算商品无效或已失效')
        return redirect('view_cart')

    # 计算总价 (只计算勾选的)
    total_price = sum(ci.item.price for ci in target_cart_items)

    # 创建订单
    order = Order.objects.create(
        buyer=request.user,
        total_price=total_price,
        is_paid=True
    )

    processed_count = 0
    # 处理商品状态
    for cart_item in target_cart_items:
        item = cart_item.item
        if item.status == 'available' and not item.is_deleted:
            item.status = 'sold'
            item.save()
            order.items.add(item)
            processed_count += 1
        else:
            messages.warning(request, f'商品 "{item.title}" 已失效，未包含在订单中')

    # 核心修改：只删除已结算的购物车条目，而不是清空整个购物车
    target_cart_items.delete()

    if processed_count > 0:
        messages.success(request, f'支付成功！订单号：{order.id}')
    else:
        order.delete()  # 如果没有有效商品，删除空订单
        messages.error(request, '订单创建失败，所有选中商品均已失效。')

    return redirect('my_orders')


# listings/views.py 的末尾追加

def seller_shop(request, seller_id):
    # 获取卖家对象，如果找不到直接返回404
    seller = get_object_or_404(User, id=seller_id)

    # 获取该卖家所有“可购买”且“未删除”的商品
    items = Item.objects.filter(seller=seller, status='available', is_deleted=False).order_by('-created_at')

    # 统计已售出数量（展示卖家信誉）
    sold_count = Item.objects.filter(seller=seller, status='sold', is_deleted=False).count()

    context = {
        'seller': seller,
        'items': items,
        'sold_count': sold_count,
    }
    return render(request, 'listings/seller_shop.html', context)


# listings/views.py 末尾追加

@login_required
def buy_now(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # 防止卖家购买自己的商品
    if item.seller == request.user:
        messages.warning(request, '您不能购买自己的商品')
        return redirect('item_detail', item_id=item_id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

    # 无论是否新建，都提示并直接跳转到购物车
    if not created:
        messages.info(request, '该商品已在购物车中，已为您跳转')
    else:
        messages.success(request, '商品已加入购物车，请结算')

    return redirect('view_cart')  # 核心区别：跳转到 view_cart

@login_required
def my_orders(request):
    # 查询当前用户买过的所有订单，按时间倒序排列
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items').order_by('-created_at')

    # 计算累计消费
    # aggregate 会返回一个字典，例如 {'total_price__sum': 1234.50}
    # 如果没有订单，结果可能是 None，所以用 'or 0' 来处理
    total_spent_data = orders.aggregate(total_spent=Sum('total_price'))
    total_spent = total_spent_data['total_spent'] or 0

    context = {
        'orders': orders,
        'title': '我的订单',
        'total_spent': total_spent,  # 将计算结果传给模板
    }
    return render(request, 'listings/order_list.html', context)