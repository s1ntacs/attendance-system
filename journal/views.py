from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse,HttpResponseForbidden
from django.db import connection,transaction
from django.views.decorators.http import require_POST,require_GET
from .forms import RegisterForm,LessonForm
from .models import Attendance,Student
from . import access

def health(request):
    with connection.cursor() as cursor: cursor.execute('SELECT 1')
    return JsonResponse({'status':'ok','database':'connected'})
def register(request):
    form=RegisterForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save(); login(request,user); return redirect('home')
    return render(request,'form.html',{'form':form,'title':'Регистрация студента'})
@login_required
@require_GET
def home(request):
    return render(request,'home.html',{'stats':access.statistics(request.user),'lessons':access.lessons(request.user),'can_edit':access.is_admin(request.user) or request.user.role=='teacher'})
@login_required
def lesson_edit(request,pk=None):
    if not (access.is_admin(request.user) or request.user.role=='teacher'): return HttpResponseForbidden('Недостаточно прав')
    item=get_object_or_404(access.lessons(request.user),pk=pk) if pk else None
    form=LessonForm(request.POST or None,instance=item,user=request.user)
    if request.method=='POST' and form.is_valid():
        item=form.save(); return redirect('lesson',pk=item.pk)
    return render(request,'form.html',{'form':form,'title':'Редактирование занятия' if pk else 'Новое занятие'})
@login_required
def lesson(request,pk):
    item=get_object_or_404(access.lessons(request.user),pk=pk)
    can_edit=access.is_admin(request.user) or request.user.role=='teacher'
    students=access.students(request.user).filter(group=item.assignment.group)
    error=None
    if request.method=='POST':
        if not can_edit: return HttpResponseForbidden('Недостаточно прав')
        updates=[(student,request.POST.get(f'status_{student.pk}','')) for student in students]
        if any(value not in ['',*Attendance.Status.values] for _,value in updates): error='Недопустимый статус. Изменения не сохранены.'
        else:
            with transaction.atomic():
                for student,value in updates:
                    if value: Attendance.objects.update_or_create(lesson=item,student=student,defaults={'status':value,'marked_by':request.user})
                    else: Attendance.objects.filter(lesson=item,student=student).delete()
            return redirect('lesson',pk=pk)
    existing={x.student_id:x.status for x in access.marks(request.user).filter(lesson=item)}
    return render(request,'lesson.html',{'lesson':item,'rows':[(s,existing.get(s.pk,'')) for s in students],'statuses':Attendance.Status.choices,'can_edit':can_edit,'error':error})
@login_required
def lesson_delete(request,pk):
    if not (access.is_admin(request.user) or request.user.role=='teacher'): return HttpResponseForbidden('Недостаточно прав')
    item=get_object_or_404(access.lessons(request.user),pk=pk)
    if request.method=='POST' and request.POST.get('confirm')=='yes':
        with transaction.atomic(): item.delete()
        return redirect('home')
    return render(request,'delete.html',{'lesson':item})
@login_required
@require_GET
def api_docs(request):
    resources=[('users','Учетные записи — администратор'),('groups','Учебные группы'),('students','Профили студентов'),('subjects','Дисциплины'),('assignments','Назначения преподавателей'),('lessons','Занятия'),('attendance','Отметки посещения')]
    return render(request,'api.html',{'resources':resources})
