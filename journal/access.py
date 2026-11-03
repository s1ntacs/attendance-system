from .models import Lesson, Attendance, Assignment, Student

def is_admin(user): return user.is_authenticated and (user.role=='admin' or user.is_superuser)
def assignments(user):
    q=Assignment.objects.select_related('group','subject','teacher')
    if is_admin(user): return q
    if user.role=='teacher': return q.filter(teacher=user)
    return q.filter(group__students__user=user)
def lessons(user): return Lesson.objects.select_related('assignment__group','assignment__subject','assignment__teacher').filter(assignment__in=assignments(user))
def students(user):
    q=Student.objects.select_related('user','group')
    if is_admin(user): return q
    if user.role=='teacher': return q.filter(group__in=assignments(user).values('group')).distinct()
    return q.filter(user=user)
def marks(user):
    q=Attendance.objects.select_related('student','lesson__assignment__subject')
    if is_admin(user): return q
    if user.role=='teacher': return q.filter(lesson__in=lessons(user))
    return q.filter(student__user=user)
def statistics(user):
    q=marks(user)
    counts={key:q.filter(status=key).count() for key in ['present','absent','excused']}
    total=sum(counts.values())
    return {**counts,'total':total,'percentage':round(counts['present']*100/total,2) if total else None}
