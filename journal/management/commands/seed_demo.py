import os
from datetime import datetime
from django.core.management.base import BaseCommand,CommandError
from django.db import transaction
from django.utils import timezone
from journal.models import User,Group,Student,Subject,Assignment,Lesson,Attendance
class Command(BaseCommand):
    help='Создает демонстрационные данные. Пароль задается DEMO_PASSWORD. Существующие пароли не меняются.'
    @transaction.atomic
    def handle(self,*args,**options):
        password=os.environ.get('DEMO_PASSWORD')
        if not password or len(password)<12: raise CommandError('Установите DEMO_PASSWORD длиной от 12 символов.')
        users={}
        for name,role in [('admin','admin'),('teacher','teacher'),('student','student'),('student2','student')]:
            user,created=User.objects.get_or_create(username=name,defaults={'role':role})
            if created: user.set_password(password);user.save()
            users[name]=user
        group,_=Group.objects.get_or_create(name='ДЕМО-01')
        subject,_=Subject.objects.get_or_create(name='Проектирование информационных систем')
        assignment,_=Assignment.objects.get_or_create(teacher=users['teacher'],group=group,subject=subject)
        for name,full in [('student','Иванов Иван — демонстрационный студент'),('student2','Петров Петр — демонстрационный студент')]:
            Student.objects.get_or_create(user=users[name],defaults={'group':group,'full_name':full})
        for day,topic in [(2,'Проектирование базы данных'),(3,'Аутентификация и REST API')]:
            lesson,_=Lesson.objects.get_or_create(assignment=assignment,starts_at=timezone.make_aware(datetime(2026,11,day,10,0)),defaults={'topic':topic})
            for name,status in [('student','present'),('student2','absent' if day==2 else 'excused')]:
                Attendance.objects.get_or_create(lesson=lesson,student=users[name].student,defaults={'status':status,'marked_by':users['teacher']})
        self.stdout.write(self.style.SUCCESS('Демонстрационные данные готовы: admin, teacher, student, student2.'))
