from django.db import models  # 장고의 ORM을 지원하는 핵심 모듈
# Db 테이블 정의하고 관리하는 모듈
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)  # status 가 published 인 것만 반환


class Post(models.Model):
    # Create your models here.
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    body = models.TextField()

    #jaewoo    jjjjj
    # DJDJDJDJDJD
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=1)
    updated = models.DateTimeField(auto_now=1)

    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.PUBLISHED)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')

    # table에 영향을 주지 않기 때문에 migrate를 사용하지 않아도 됨 / 객체생성
    objects = models.Manager()  # administrator
    published = PublishedManager()  # sub admin
    tags = TaggableManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publish']  # publish field 를 기준으로 내림차순 정렬
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'

    class Meta:  # 정렬 처리할때 사용
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]
