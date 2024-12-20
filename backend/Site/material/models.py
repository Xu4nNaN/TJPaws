from django.contrib.auth.models import User  # Django自带的用户模型
# from django.contrib.gis.db import models as geomodels
# !!!在 Django 的 GIS 模块（即 django.contrib.gis）中，如果你需要使用地理空间字段（如 PointField、PolygonField 等），你必须在系统中安装 GDAL 和相关的依赖。
# !!!这是因为这些字段依赖于 GDAL 和 GEOS 等底层库来处理地理空间数据的解析和验证。所以暂时改掉这个字段!
from django.db import models


class Animal(models.Model):
    # 动物资料
    nickname = models.CharField(max_length=100, verbose_name="昵称")
    species = models.CharField(max_length=50, verbose_name="动物种类")
    breed = models.CharField(max_length=100, blank=True, null=True, verbose_name="品种")
    thumbnail = models.ForeignKey(
        'AnimalImage',  # 外键关联到 AnimalImage 模型
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='thumbnails',
        verbose_name="概述图片"
    )
    description = models.TextField(blank=True, null=True, verbose_name="简介")
    # location = geomodels.PointField(blank=True, null=True, verbose_name="活动范围")  # 动物的活动范围（地理位置）
    location = models.JSONField(blank=True, null=True, verbose_name="活动范围")  # !!!暂时改成JSONField
    notes = models.TextField(blank=True, null=True, verbose_name="备注")  # 管理员做标记用

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = "动物资料"
        verbose_name_plural = "动物资料"
        # TODO 
        # 受限于依赖暂时放弃
        # indexes = [
        #     models.Index(fields=['location']),
        # ]  # 提高地理位置查询效率


class AnimalImage(models.Model):
    """动物的图片资源"""
    animal = models.ForeignKey(
        'Animal',  # 外键关联到 Animal 模型
        on_delete=models.CASCADE,
        related_name='images',  # 通过 animal.images 获取关联的所有图片
        verbose_name="动物"
    )
    image = models.ImageField(upload_to='animals/images/', verbose_name="图片路径")
    order = models.PositiveIntegerField(default=0, verbose_name="排序")  # 图片在动物图片集中的排序
    description = models.CharField(max_length=255, blank=True, verbose_name="图片描述")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")

    def __str__(self):
        return f"Image of {self.animal.nickname}"


class Feedback(models.Model):
    # 反馈
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="反馈用户")  # 反馈的用户（可选，用于非匿名反馈；不过应该只有用户才能反馈？）
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="关联动物资料")  # 关联的动物资料
    suggested_changes = models.JSONField(verbose_name="建议的修改值")  # 被修改的字段及其建议值，使用 JSON 字段存储
    feedback_notes = models.TextField(blank=True, verbose_name="反馈意见")  # 用户附加反馈意见
    STATUS_CHOICES = [
        ("pending", "未处理"),
        ("in_progress", "处理中"),
        ("resolved", "已处理"),
    ]  # 反馈状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="处理状态")
    admin_notes = models.TextField(blank=True, verbose_name="管理员备注")  # 管理员的处理备注
    # 创建时间和更新时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"反馈 #{self.id} - {self.animal.nickname} ({self.get_status_display()})"

class AnimalLeaderBoard(models.Model):
    # 动物排行榜
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE, verbose_name="动物")
    auto_update_score = models.BooleanField(default=True, verbose_name="自动更新得分")
    score = models.IntegerField(verbose_name="得分")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def set_score(self, score):
        self.score = score
        self.save()

    class Meta:
        verbose_name = "动物排行榜"
        verbose_name_plural = "动物排行榜"
        ordering = ['-score']

class Like_Animal(models.Model):
    # 点赞
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="动物")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ['user', 'animal']
        verbose_name = "点赞"
        verbose_name_plural = "点赞"
