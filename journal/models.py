from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN='admin','Администратор'
        TEACHER='teacher','Преподаватель'
        STUDENT='student','Студент'
    role=models.CharField(max_length=10,choices=Role.choices,default=Role.STUDENT)

class Group(models.Model):
    name=models.CharField(max_length=50,unique=True)
    def __str__(self): return self.name

class Student(models.Model):
    user=models.OneToOneField(User,on_delete=models.PROTECT,related_name='student')
    group=models.ForeignKey(Group,on_delete=models.PROTECT,related_name='students')
    full_name=models.CharField(max_length=150)
    def __str__(self): return self.full_name

class Subject(models.Model):
    name=models.CharField(max_length=100,unique=True)
    def __str__(self): return self.name

class Assignment(models.Model):
    teacher=models.ForeignKey(User,on_delete=models.PROTECT,related_name='assignments')
    group=models.ForeignKey(Group,on_delete=models.PROTECT)
    subject=models.ForeignKey(Subject,on_delete=models.PROTECT)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['teacher','group','subject'],name='unique_assignment')]
    def __str__(self): return f'{self.group} / {self.subject} / {self.teacher.username}'

class Lesson(models.Model):
    assignment=models.ForeignKey(Assignment,on_delete=models.PROTECT,related_name='lessons')
    starts_at=models.DateTimeField()
    topic=models.CharField(max_length=200)
    class Meta:
        ordering=['-starts_at','id']
        constraints=[models.UniqueConstraint(fields=['assignment','starts_at'],name='unique_lesson_time')]
    def __str__(self): return f'{self.topic} ({self.starts_at:%d.%m.%Y})'

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT='present','Присутствовал'
        ABSENT='absent','Отсутствовал'
        EXCUSED='excused','Уважительный пропуск'
    lesson=models.ForeignKey(Lesson,on_delete=models.CASCADE,related_name='marks')
    student=models.ForeignKey(Student,on_delete=models.PROTECT,related_name='marks')
    status=models.CharField(max_length=10,choices=Status.choices)
    marked_by=models.ForeignKey(User,on_delete=models.PROTECT)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['lesson','student'],name='unique_lesson_student'),models.CheckConstraint(condition=models.Q(status__in=['present','absent','excused']),name='valid_attendance_status')]
