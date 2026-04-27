# accounts/models.py
# 这是用户账户相关的模型文件，用于定义用户资料扩展功能

# 导入Django的数据库模型模块，包含所有基础的数据库字段类型和模型基类
from django.db import models

# 导入Django内置的用户模型，包含用户名、密码、邮箱等基础用户功能
# 这个User模型已经提供了完整的用户认证系统
from django.contrib.auth.models import User

# 导入数据库保存后信号，用于监听User模型的创建和修改事件
# 当User模型被保存时，这个信号会被触发
from django.db.models.signals import post_save

# 导入信号接收器装饰器，用于将函数注册为信号处理器
# 使用@receiver装饰器可以将普通函数转换为信号监听器
from django.dispatch import receiver

# 定义Profile模型，继承自Django的models.Model
# 这个模型用于扩展User模型，添加校园二手交易平台特有的用户信息
class Profile(models.Model):
    # 定义user字段：一对一关联到User模型
    # OneToOneField确保每个User只有一个Profile，每个Profile只对应一个User
    # on_delete=models.CASCADE表示当User被删除时，关联的Profile也会被自动删除
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 定义avatar字段：用户头像图片字段
    # ImageField专门用于存储图片文件
    # upload_to='avatars/'指定图片上传到media/avatars/目录下
    # default='avatars/default.png'设置默认头像，如果用户没有上传头像就使用这个默认图片
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    
    # 定义bio字段：用户个人简介
    # TextField用于存储长文本，最多500个字符
    # blank=True表示这个字段可以为空，表单验证时允许不填写
    bio = models.TextField(max_length=500, blank=True)
    
    # 定义student_id字段：学号
    # CharField用于存储字符串，最大长度20个字符
    # blank=True允许这个字段为空，方便不填学号的用户
    student_id = models.CharField(max_length=20, blank=True)
    
    # 定义wechat字段：微信号
    # CharField存储字符串，最大长度50个字符
    # blank=True允许为空，方便不想公开微信号的用户
    wechat = models.CharField(max_length=50, blank=True)
    
    # 定义phone字段：手机号
    # CharField存储字符串，最大长度15个字符（考虑国际号码格式）
    # blank=True允许为空，保护用户隐私
    phone = models.CharField(max_length=15, blank=True)
    
    # 定义__str__方法，返回对象的字符串表示
    # 当这个模型对象需要转换为字符串时（比如在admin后台显示）会自动调用
    # 返回格式：用户名+的个人资料，比如"zhangsan的个人资料"
    def __str__(self):
        return f'{self.user.username}的个人资料'

# 使用@receiver装饰器注册信号处理器
# 监听User模型的post_save信号，即User模型每次保存时都会触发这个函数
@receiver(post_save, sender=User)
# 定义create_user_profile函数，当新用户创建时自动创建对应的Profile
def create_user_profile(sender, instance, created, **kwargs):
    # sender：发送信号的模型类（这里是User）
    # instance：被保存的User实例对象
    # created：布尔值，True表示这是新创建的记录，False表示是更新现有记录
    # **kwargs：其他关键字参数（暂时用不到但需要接受）
    if created:
        # 如果是新用户创建（created=True），则自动创建对应的Profile
        # 使用Profile.objects.create()创建并保存Profile对象
        # 只传递user字段，设置为当前的User实例
        # 其他字段会使用默认值（avatar使用default，bio等使用blank=True的默认值）
        Profile.objects.create(user=instance)

# 同样监听User模型的post_save信号
@receiver(post_save, sender=User)
# 定义save_user_profile函数，确保User保存时同步保存Profile
def save_user_profile(sender, instance, **kwargs):
    # 这个函数在User每次保存时都会执行
    # 作用：确保User关联的Profile也被保存到数据库
    # instance.profile：这里利用了Django的OneToOneField自动提供的反向访问
    # 当访问user.profile时，Django会自动查询并返回对应的Profile对象
    # 然后调用.save()方法确保Profile的修改也被保存到数据库
    instance.profile.save()