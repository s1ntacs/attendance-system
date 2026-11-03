from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from rest_framework.test import APIClient
from .models import User, Group, Student, Subject, Assignment, Lesson, Attendance

class JournalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin=User.objects.create_user(username='admin',password='StrongDemoPass!2026',role='admin')
        cls.teacher=User.objects.create_user(username='teacher',password='StrongDemoPass!2026',role='teacher')
        cls.other=User.objects.create_user(username='other',password='StrongDemoPass!2026',role='teacher')
        cls.student_user=User.objects.create_user(username='student',password='StrongDemoPass!2026')
        cls.peer_user=User.objects.create_user(username='peer',password='StrongDemoPass!2026')
        cls.group=Group.objects.create(name='A')
        cls.other_group=Group.objects.create(name='B')
        cls.student=Student.objects.create(user=cls.student_user,group=cls.group,full_name='Student')
        cls.peer=Student.objects.create(user=cls.peer_user,group=cls.other_group,full_name='Peer')
        cls.subject=Subject.objects.create(name='Databases')
        cls.assignment=Assignment.objects.create(teacher=cls.teacher,group=cls.group,subject=cls.subject)
        cls.other_assignment=Assignment.objects.create(teacher=cls.other,group=cls.other_group,subject=cls.subject)
        cls.lesson=Lesson.objects.create(assignment=cls.assignment,starts_at=timezone.now(),topic='Schema')
        cls.other_lesson=Lesson.objects.create(assignment=cls.other_assignment,starts_at=timezone.now(),topic='Foreign')
    def setUp(self): self.api=APIClient()
    def auth(self,user): self.api.force_authenticate(user)
    def mark(self,status='present'):
        return Attendance.objects.create(lesson=self.lesson,student=self.student,status=status,marked_by=self.teacher)
    def test_anonymous_cannot_read(self):
        self.assertEqual(self.api.get('/api/lessons/').status_code,403)
    def test_password_is_hashed(self):
        self.assertNotEqual(self.teacher.password,'StrongDemoPass!2026')
        self.assertTrue(self.teacher.check_password('StrongDemoPass!2026'))
    def test_login_and_logout(self):
        c=Client();self.assertTrue(c.login(username='teacher',password='StrongDemoPass!2026'))
        self.assertContains(c.get('/'),'teacher')
        self.assertEqual(c.post('/logout/').status_code,302)
        self.assertEqual(c.get('/').status_code,302)
    def test_login_csrf_required(self):
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.post('/login/',{'username':'teacher','password':'StrongDemoPass!2026'}).status_code,403)
    def test_session_api_csrf_required(self):
        c=APIClient(enforce_csrf_checks=True);c.login(username='teacher',password='StrongDemoPass!2026')
        self.assertEqual(c.post('/api/lessons/',{},format='json').status_code,403)
    def test_registration_cannot_choose_role(self):
        c=Client();r=c.post('/register/',{'username':'newstudent','password1':'StrongDemoPass!2026','password2':'StrongDemoPass!2026','role':'admin'})
        self.assertEqual(r.status_code,302)
        self.assertEqual(User.objects.get(username='newstudent').role,'student')
    def test_teacher_only_own_lessons(self):
        self.auth(self.teacher)
        self.assertEqual([x['id'] for x in self.api.get('/api/lessons/').data],[self.lesson.id])
        self.assertEqual(self.api.get(f'/api/lessons/{self.other_lesson.id}/').status_code,404)
    def test_teacher_cannot_create_foreign_lesson(self):
        self.auth(self.teacher)
        r=self.api.post('/api/lessons/',{'assignment':self.other_assignment.id,'starts_at':timezone.now().isoformat(),'topic':'X'})
        self.assertEqual(r.status_code,400)
    def test_student_read_only(self):
        self.auth(self.student_user)
        self.assertEqual(self.api.post('/api/attendance/',{}).status_code,403)
        self.assertEqual(self.api.delete(f'/api/lessons/{self.lesson.id}/').status_code,403)
    def test_student_cannot_read_other_marks(self):
        self.mark();Attendance.objects.create(lesson=self.other_lesson,student=self.peer,status='absent',marked_by=self.other)
        self.auth(self.student_user)
        self.assertEqual(len(self.api.get('/api/attendance/').data),1)
        self.assertEqual(len(self.api.get('/api/students/').data),1)
    def test_wrong_group_rejected(self):
        self.auth(self.teacher)
        r=self.api.post('/api/attendance/',{'lesson':self.lesson.id,'student':self.peer.id,'status':'present'})
        self.assertEqual(r.status_code,400)
    def test_invalid_status_rejected(self):
        self.auth(self.teacher)
        self.assertEqual(self.api.post('/api/attendance/',{'lesson':self.lesson.id,'student':self.student.id,'status':'invalid'}).status_code,400)
    def test_duplicate_mark_rejected_and_patch_works(self):
        mark=self.mark();self.auth(self.teacher)
        self.assertEqual(self.api.post('/api/attendance/',{'lesson':self.lesson.id,'student':self.student.id,'status':'absent'}).status_code,400)
        self.assertEqual(self.api.patch(f'/api/attendance/{mark.id}/',{'status':'absent'}).status_code,200)
        self.assertEqual(Attendance.objects.count(),1)
        mark.refresh_from_db();self.assertEqual(mark.status,'absent')
    def test_catalog_crud_admin(self):
        self.auth(self.admin)
        r=self.api.post('/api/groups/',{'name':'C'});self.assertEqual(r.status_code,201);pk=r.data['id']
        self.assertEqual(self.api.get(f'/api/groups/{pk}/').status_code,200)
        self.assertEqual(self.api.patch(f'/api/groups/{pk}/',{'name':'D'}).status_code,200)
        self.assertEqual(self.api.delete(f'/api/groups/{pk}/').status_code,204)
    def test_teacher_cannot_manage_users(self):
        self.auth(self.teacher);self.assertEqual(self.api.get('/api/users/').status_code,403)
    def test_protected_group_deletion(self):
        self.auth(self.admin);self.assertEqual(self.api.delete(f'/api/groups/{self.group.id}/').status_code,409)
    def test_delete_lesson_requires_confirmation_and_cascades(self):
        self.mark();self.auth(self.teacher)
        self.assertEqual(self.api.delete(f'/api/lessons/{self.lesson.id}/').status_code,409)
        self.assertTrue(Attendance.objects.exists())
        self.assertEqual(self.api.delete(f'/api/lessons/{self.lesson.id}/?confirm=true').status_code,204)
        self.assertFalse(Attendance.objects.exists())
    def test_lesson_crud(self):
        self.auth(self.teacher)
        r=self.api.post('/api/lessons/',{'assignment':self.assignment.id,'starts_at':(timezone.now()+timedelta(days=1)).isoformat(),'topic':'New'})
        self.assertEqual(r.status_code,201);pk=r.data['id']
        self.assertEqual(self.api.get(f'/api/lessons/{pk}/').status_code,200)
        self.assertEqual(self.api.patch(f'/api/lessons/{pk}/',{'topic':'Edited'}).status_code,200)
        self.assertEqual(self.api.delete(f'/api/lessons/{pk}/').status_code,204)
    def test_empty_statistics(self):
        self.auth(self.student_user);self.assertIsNone(self.api.get('/api/stats/').data['percentage'])
    def test_statistics_does_not_count_unmarked(self):
        self.mark();self.auth(self.student_user)
        Lesson.objects.create(assignment=self.assignment,starts_at=timezone.now()+timedelta(days=2),topic='Unmarked')
        self.assertEqual(self.api.get('/api/stats/').data['percentage'],100)
        self.assertEqual(self.api.get('/api/stats/').data['total'],1)
    def test_student_cannot_be_moved_after_marks(self):
        self.mark();self.auth(self.admin)
        self.assertEqual(self.api.patch(f'/api/students/{self.student.id}/',{'group':self.other_group.id}).status_code,400)
    def test_assignment_cannot_change_after_lessons(self):
        self.auth(self.admin)
        self.assertEqual(self.api.patch(f'/api/assignments/{self.assignment.id}/',{'teacher':self.other.id}).status_code,400)
    def test_role_cannot_break_assignment(self):
        self.auth(self.admin)
        self.assertEqual(self.api.patch(f'/api/users/{self.teacher.id}/',{'role':'student'}).status_code,400)
    def test_html_repeat_save_does_not_duplicate(self):
        self.client.force_login(self.teacher)
        for _ in range(2): self.assertEqual(self.client.post(f'/lessons/{self.lesson.id}/', {f'status_{self.student.id}':'present'}).status_code,302)
        self.assertEqual(Attendance.objects.count(),1)
    def test_html_invalid_batch_is_atomic(self):
        self.mark();self.client.force_login(self.teacher)
        self.client.post(f'/lessons/{self.lesson.id}/',{f'status_{self.student.id}':'invalid'})
        self.assertEqual(Attendance.objects.get().status,'present')
    def test_four_lesson_screens(self):
        self.client.force_login(self.teacher)
        for path in ['/', '/lessons/new/',f'/lessons/{self.lesson.id}/',f'/lessons/{self.lesson.id}/edit/']:
            self.assertEqual(self.client.get(path).status_code,200)
