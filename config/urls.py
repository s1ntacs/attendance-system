from django.urls import path,include
from django.contrib.auth import views as auth
from rest_framework.routers import DefaultRouter
from journal import views,api
router=DefaultRouter()
for name,view in [('users',api.UserViewSet),('groups',api.GroupViewSet),('students',api.StudentViewSet),('subjects',api.SubjectViewSet),('assignments',api.AssignmentViewSet),('lessons',api.LessonViewSet),('attendance',api.AttendanceViewSet)]: router.register(name,view,basename=name)
urlpatterns=[path('',views.home,name='home'),path('health/',views.health),path('login/',auth.LoginView.as_view(template_name='login.html'),name='login'),path('logout/',auth.LogoutView.as_view(),name='logout'),path('register/',views.register,name='register'),path('lessons/new/',views.lesson_edit,name='lesson_new'),path('lessons/<int:pk>/',views.lesson,name='lesson'),path('lessons/<int:pk>/edit/',views.lesson_edit,name='lesson_edit'),path('lessons/<int:pk>/delete/',views.lesson_delete,name='lesson_delete'),path('api/docs/',views.api_docs),path('api/me/',api.me),path('api/stats/',api.stats),path('api/',include(router.urls))]
