from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import User, Group, Student, Subject, Assignment, Lesson, Attendance
from .access import is_admin, assignments

class UserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,required=False)
    class Meta:
        model=User
        fields=['id','username','first_name','last_name','role','password']
    def validate(self,attrs):
        if not self.instance and not attrs.get('password'): raise serializers.ValidationError({'password':'Обязательное поле.'})
        if 'password' in attrs:
            try: validate_password(attrs['password'],User(username=attrs.get('username',getattr(self.instance,'username',''))))
            except DjangoValidationError as e: raise serializers.ValidationError({'password':e.messages})
        if self.instance and 'role' in attrs and attrs['role'] != self.instance.role:
            if self.instance.assignments.exists() or hasattr(self.instance,'student'):
                raise serializers.ValidationError('Нельзя менять роль пользователя, связанного с назначениями или профилем студента.')
        return attrs
    def create(self,data): return User.objects.create_user(**data)
    def update(self,instance,data):
        password=data.pop('password',None)
        instance=super().update(instance,data)
        if password: instance.set_password(password); instance.save(update_fields=['password'])
        return instance

class GroupSerializer(serializers.ModelSerializer):
    class Meta: model=Group; fields=['id','name']
class SubjectSerializer(serializers.ModelSerializer):
    class Meta: model=Subject; fields=['id','name']
class StudentSerializer(serializers.ModelSerializer):
    class Meta: model=Student; fields=['id','user','group','full_name']
    def validate(self,data):
        user=data.get('user',getattr(self.instance,'user',None))
        if user.role!='student': raise serializers.ValidationError('Профиль доступен только роли студент.')
        if self.instance and self.instance.marks.exists():
            if data.get('group',self.instance.group)!=self.instance.group or user!=self.instance.user:
                raise serializers.ValidationError('После отметок нельзя менять группу или владельца профиля.')
        return data
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta: model=Assignment; fields=['id','teacher','group','subject']
    def validate(self,data):
        teacher=data.get('teacher',getattr(self.instance,'teacher',None))
        if teacher.role!='teacher': raise serializers.ValidationError('Требуется преподаватель.')
        if self.instance and self.instance.lessons.exists() and any(data.get(k,getattr(self.instance,k))!=getattr(self.instance,k) for k in ['teacher','group','subject']):
            raise serializers.ValidationError('Назначение с занятиями нельзя менять: создайте новое.')
        return data
class LessonSerializer(serializers.ModelSerializer):
    class Meta: model=Lesson; fields=['id','assignment','starts_at','topic']
    def validate_assignment(self,value):
        if not assignments(self.context['request'].user).filter(pk=value.pk).exists(): raise serializers.ValidationError('Нет доступа к назначению.')
        if self.instance and self.instance.marks.exists() and value.pk!=self.instance.assignment_id: raise serializers.ValidationError('Нельзя менять назначение после отметок.')
        return value
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Attendance; fields=['id','lesson','student','status','marked_by','updated_at']; read_only_fields=['marked_by','updated_at']
    def validate(self,data):
        lesson=data.get('lesson',getattr(self.instance,'lesson',None))
        student=data.get('student',getattr(self.instance,'student',None))
        if not assignments(self.context['request'].user).filter(pk=lesson.assignment_id).exists(): raise serializers.ValidationError('Нет доступа к занятию.')
        if student.group_id!=lesson.assignment.group_id: raise serializers.ValidationError('Студент не входит в группу занятия.')
        if self.instance and (lesson.pk!=self.instance.lesson_id or student.pk!=self.instance.student_id): raise serializers.ValidationError('Менять можно только статус отметки.')
        return data
