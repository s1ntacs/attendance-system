from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from .models import User, Group, Student, Subject, Assignment, Lesson, Attendance
from .serializers import UserSerializer, GroupSerializer, StudentSerializer, SubjectSerializer, AssignmentSerializer, LessonSerializer, AttendanceSerializer
from . import access

def exception_handler(exc,context):
    if isinstance(exc,ProtectedError): return Response({'detail':'Запись используется другими данными. Удаление запрещено.'},status=409)
    if isinstance(exc,IntegrityError): return Response({'detail':'Нарушено ограничение целостности или запись уже существует.'},status=409)
    return drf_exception_handler(exc,context)

class AdminOnly(permissions.BasePermission):
    def has_permission(self,request,view): return access.is_admin(request.user)
class CatalogPermission(permissions.BasePermission):
    def has_permission(self,request,view):
        return request.user.is_authenticated and (request.method in permissions.SAFE_METHODS or access.is_admin(request.user))
class JournalPermission(permissions.BasePermission):
    def has_permission(self,request,view):
        return request.user.is_authenticated and (request.method in permissions.SAFE_METHODS or access.is_admin(request.user) or request.user.role=='teacher')
class AtomicViewSet(viewsets.ModelViewSet):
    @transaction.atomic
    def create(self,*args,**kwargs): return super().create(*args,**kwargs)
    @transaction.atomic
    def update(self,*args,**kwargs): return super().update(*args,**kwargs)
    @transaction.atomic
    def destroy(self,*args,**kwargs): return super().destroy(*args,**kwargs)
class UserViewSet(AtomicViewSet):
    queryset=User.objects.all().order_by('id'); serializer_class=UserSerializer; permission_classes=[AdminOnly]
class GroupViewSet(AtomicViewSet):
    serializer_class=GroupSerializer; permission_classes=[CatalogPermission]
    def get_queryset(self):
        return Group.objects.all().order_by('id') if access.is_admin(self.request.user) else Group.objects.filter(pk__in=access.assignments(self.request.user).values('group')).order_by('id')
class SubjectViewSet(AtomicViewSet):
    serializer_class=SubjectSerializer; permission_classes=[CatalogPermission]
    def get_queryset(self):
        return Subject.objects.all().order_by('id') if access.is_admin(self.request.user) else Subject.objects.filter(pk__in=access.assignments(self.request.user).values('subject')).order_by('id')
class StudentViewSet(AtomicViewSet):
    serializer_class=StudentSerializer; permission_classes=[CatalogPermission]
    def get_queryset(self): return access.students(self.request.user).order_by('id')
class AssignmentViewSet(AtomicViewSet):
    serializer_class=AssignmentSerializer; permission_classes=[CatalogPermission]
    def get_queryset(self): return access.assignments(self.request.user).order_by('id')
class LessonViewSet(AtomicViewSet):
    serializer_class=LessonSerializer; permission_classes=[JournalPermission]
    def get_queryset(self): return access.lessons(self.request.user)
    @transaction.atomic
    def destroy(self,request,*args,**kwargs):
        lesson=self.get_object()
        if lesson.marks.exists() and request.query_params.get('confirm')!='true':
            return Response({'detail':'Занятие содержит отметки. Подтвердите удаление: ?confirm=true'},status=409)
        return super().destroy(request,*args,**kwargs)
class AttendanceViewSet(AtomicViewSet):
    serializer_class=AttendanceSerializer; permission_classes=[JournalPermission]
    def get_queryset(self): return access.marks(self.request.user).order_by('id')
    def perform_create(self,serializer): serializer.save(marked_by=self.request.user)
    def perform_update(self,serializer): serializer.save(marked_by=self.request.user)
@api_view(['GET'])
def me(request): return Response(UserSerializer(request.user).data)
@api_view(['GET'])
def stats(request): return Response(access.statistics(request.user))
