# listings/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Min
from .models import Category, Item, ItemImage, Order


# ==========================================
# 1. 定义内联 (Inlines)
# ==========================================

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1
    verbose_name = "商品图片"
    verbose_name_plural = "商品图片管理"

    # =================👇 这里是你需要新增的代码 👇=================
    readonly_fields = ('image_preview',)
    fields = ('image', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); object-fit: cover;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">暂无图片</span>')

    image_preview.short_description = '图片实时预览'
    # =================👆 这里是你需要新增的代码 👆=================

class ItemInline(admin.TabularInline):
    model = Item
    fields = ('item_link',)
    readonly_fields = ('item_link',)
    show_change_link = False
    extra = 0
    can_delete = False

    verbose_name = "该分类下的商品"
    verbose_name_plural = "该分类下的商品列表"

    def has_add_permission(self, request, obj):
        return False

    def item_link(self, obj):
        url = reverse('admin:listings_item_change', args=[obj.id])
        return format_html(
            '<a href="{}" class="item-tag-link">{}</a>',
            url, obj.title
        )

    item_link.short_description = "商品"


# ==========================================
# 2. 商品管理 (ItemAdmin)
# ==========================================
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('show_cover','title', 'show_price', 'category', 'seller', 'show_status', 'is_deleted', 'created_at')
    list_filter = ('status', 'category', 'is_deleted')
    search_fields = ('title', 'description', 'seller__username')
    list_per_page = 20
    inlines = [ItemImageInline]
    date_hierarchy = 'created_at'

    actions = ['make_available', 'make_pending']

    @admin.action(description='审核通过选中商品')
    def make_available(self, request, queryset):
        queryset.update(status='available')
        self.message_user(request, "所选商品已审核通过，状态变为【可购买】")

    @admin.action(description='驳回/设为待审核')
    def make_pending(self, request, queryset):
        queryset.update(status='pending')

    def show_status(self, obj):
        if obj.status == 'available':
            color = 'green'
            text = '可购买'
        elif obj.status == 'pending':
            color = 'orange'
            text = '待审核'
        elif obj.status == 'sold':
            color = 'gray'
            text = '已售出'
        else:
            color = 'blue'
            text = obj.get_status_display()
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, text)

    show_status.short_description = '当前状态'

    def show_price(self, obj):
        return f"¥{obj.price}"

    show_price.short_description = '价格'

    # =================👇 这里是你需要新增的代码 👇=================
    def show_cover(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" />',
                first_image.image.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #eee; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px;">无图</div>')

    show_cover.short_description = '封面图'
    # =================👆 这里是你需要新增的代码 👆=================
# ==========================================
# 3. 分类管理 (CategoryAdmin) - 🎨 样式调整区
# ==========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'item_count_display')
    list_display_links = ('name',)
    search_fields = ('name',)
    inlines = [ItemInline]

    def item_count_display(self, obj):
        count = Item.objects.filter(category=obj).count()
        color = 'green' if count > 0 else 'gray'
        return format_html('<span style="color: {}; font-weight: bold;">{} 件商品</span>', color, count)

    item_count_display.short_description = '库存在售'

    def clean_style(self, obj):
        return mark_safe("""
            <style>
                /* 隐藏 "Clean style:" 字段本身 */
                .field-clean_style {
                    display: none !important;
                }

                /* 🔥 关键调整：限制大方框的宽度 */
                #item_set-group {
                    max-width: 800px; /* 限制最大宽度为 800像素 */
                    width: 70%;       /* 或者占据屏幕的 70% */
                }

                /* 隐藏表格头部 */
                #item_set-group table thead { 
                    display: none; 
                }

                /* 弹性布局容器 */
                #item_set-group table tbody {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    padding: 10px 0;
                }

                /* 商品小方块样式 (排除隐藏行) */
                #item_set-group table tbody tr:not(.empty-form) {
                    display: inline-flex;
                    align-items: center;
                    border: 1px solid #dee2e6;
                    background-color: #f8f9fa;
                    border-radius: 4px;
                    padding: 4px 12px;
                    margin: 0 !important;
                }

                /* 确保隐藏行彻底不显示 */
                #item_set-group table tbody tr.empty-form {
                    display: none !important;
                }

                /* 鼠标悬停 */
                #item_set-group table tbody tr:not(.empty-form):hover {
                    background-color: #e9ecef;
                    border-color: #ced4da;
                    cursor: pointer;
                }

                /* 清除表格默认边距干扰 */
                #item_set-group table tbody td {
                    border: none !important;
                    padding: 0 !important;
                    background: none !important;
                }
                #item_set-group .original {
                    display: none !important;
                }
                #item_set-group .add-row {
                    display: none !important;
                }

                /* 链接文字 */
                .item-tag-link {
                    text-decoration: none;
                    color: #333;
                    font-size: 13px;
                }
                .item-tag-link:hover {
                    color: #0056b3;
                }
            </style>
        """)

    readonly_fields = ('clean_style',)
    fields = ('name', 'description', 'clean_style')


# ==========================================
# 4. 订单管理 (OrderAdmin)
# ==========================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'show_items_list', 'show_sellers', 'total_price', 'created_at', 'is_paid')
    list_filter = ('is_paid', 'created_at')
    date_hierarchy = 'created_at'

    fields = ('buyer', 'show_sellers', 'items', 'total_price', 'is_paid', 'created_at')
    readonly_fields = ('show_sellers', 'created_at')
    filter_horizontal = ('items',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _first_item_title=Min('items__title'),
            _first_seller_name=Min('items__seller__username')
        )
        return qs

    def show_items_list(self, obj):
        return ", ".join([item.title for item in obj.items.all()])

    show_items_list.short_description = '包含商品'
    show_items_list.admin_order_field = '_first_item_title'

    def show_sellers(self, obj):
        if not obj:
            return "-"
        sellers = set([item.seller.username for item in obj.items.all()])
        return ", ".join(sellers) if sellers else "无"

    show_sellers.short_description = '卖家'
    show_sellers.admin_order_field = '_first_seller_name'