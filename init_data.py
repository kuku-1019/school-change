import os
import django
import random

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_glimmer.settings')
django.setup()

from django.contrib.auth.models import User
from listings.models import Category, Item
from accounts.models import Profile


def create_data():
    print("🚀 开始初始化基础数据...")

    # 1. 创建测试用户
    users = []
    user_data = [
        ('admin', 'admin@example.com', 'admin123', True),  # 超级管理员
        ('seller1', 'seller1@example.com', '123456', False),
        ('student_li', 'li@example.com', '123456', False),
        ('wang_xiao', 'wang@example.com', '123456', False),
        ('zhang_san', 'zhang@example.com', '123456', False),
    ]

    for username, email, password, is_staff in user_data:
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.is_staff = is_staff
            user.is_superuser = is_staff
            user.save()
            # 确保有 Profile
            Profile.objects.get_or_create(user=user)
            print(f"✅ 创建用户: {username}")
        else:
            print(f"   用户已存在: {username}")
        users.append(user)

    # 排除管理员，只用普通用户发商品
    sellers = [u for u in users if not u.is_staff]

    # 2. 创建分类
    categories = {}
    cat_data = [
        ('数码电子', '手机、电脑、耳机、键盘等'),
        ('教材书籍', '考研资料、专业课教材、课外书'),
        ('生活用品', '收纳盒、台灯、风扇、排插'),
        ('运动健身', '球拍、哑铃、瑜伽垫'),
        ('美妆护肤', '未拆封的化妆品、护肤品'),
        ('校园代步', '自行车、电动车、滑板'),
    ]

    for name, desc in cat_data:
        cat, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
        categories[name] = cat
        if created:
            print(f"✅ 创建分类: {name}")

    # 3. 准备商品数据
    # 格式: (标题, 价格, 分类名, 描述, 成色)
    items_data = [
        ('罗技 G304 无线鼠标', 99.00, '数码电子', '大一买的，用了不到一个月，换了更好的所以出。箱说全，没有任何问题。',
         '95新'),
        ('考研英语一黄皮书真题', 45.00, '教材书籍', '2024版，只写了前两套，后面都是新的。送单词书。', '9成新'),
        ('小米台灯1S', 80.00, '生活用品', '毕业带不走，光线很舒服，支持米家APP控制。', '8成新'),
        ('尤尼克斯羽毛球拍', 150.00, '运动健身', '入门款，线刚穿的24磅，手胶也是新的。', '85新'),
        ('捷安特山地自行车', 400.00, '校园代步', '骑了两年，刹车灵敏，变速顺滑，送一把U型锁。自提。', '7成新'),
        ('AirPods Pro 2', 1200.00, '数码电子', '官网入手的，有刻字。带Apple Care+。', '99新'),
        ('高等数学同济第七版上下册', 20.00, '教材书籍', '祖传教材，笔记很全，期末突击必备。', '5成新'),
        ('宜家收纳推车', 50.00, '生活用品', '白色三层，轮子顺滑，放零食很方便。', '9成新'),
        ('李宁篮球', 30.00, '运动健身', '室外场打过的，手感还可以，耐磨。', '6成新'),
        ('雅诗兰黛小棕瓶', 300.00, '美妆护肤', '专柜赠品，15ml小样，全新未拆封。', '全新'),
        ('机械革命极光Pro', 4500.00, '数码电子', 'i7+4060，打游戏很爽，因为要实习了换轻薄本。', '9成新'),
        ('C语言程序设计', 15.00, '教材书籍', '计算机学院大一教材，几乎全新。', '99新'),
        ('宿舍遮光帘', 25.00, '生活用品', '全封闭式，遮光效果100%，送支架。', '8成新'),
        ('电动滑板车', 600.00, '校园代步', '续航20公里，折叠方便，上课神器。', '85新'),
        ('索尼 WH-1000XM4', 1100.00, '数码电子', '降噪无敌，自习室神器。耳罩有点磨损。', '8成新'),
        ('四级真题试卷', 10.00, '教材书籍', '买了没做，全新。', '全新'),
        ('瑜伽垫', 15.00, '运动健身', '加厚防滑，女生自用，很干净。', '9成新'),
        ('迪奥999口红', 120.00, '美妆护肤', '朋友送的，色号不适合我，仅试色。', '99新'),
    ]

    # 4. 批量创建商品
    created_count = 0
    for i, (title, price, cat_name, desc, condition) in enumerate(items_data):
        # 检查是否已存在
        if Item.objects.filter(title=title).exists():
            continue

        seller = random.choice(sellers)
        category = categories.get(cat_name)

        # 随机分配状态
        rand_status = random.choices(
            ['available',  'sold'],
            weights=[80, 20],
            k=1
        )[0]

        item = Item.objects.create(
            title=title,
            price=price,
            category=category,
            description=desc,
            condition=condition,
            seller=seller,
            status=rand_status if rand_status != 'available' else 'available',
            is_deleted=False
        )

        # 默认让所有生成的商品通过审核
        if rand_status == 'available':
            item.status = 'available'
            item.save()

        # 注意：这里不再创建 ItemImage，前端会自动显示默认图

        created_count += 1
        print(f"📦 发布商品: {title} (状态: {item.get_status_display()})")

    print(f"\n🎉 初始化完成！新增了 {created_count} 个商品。")
    print("👉 请使用账号: student_li / 123456 登录体验。")


if __name__ == '__main__':
    create_data()