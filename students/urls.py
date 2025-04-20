# students/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Student API URLs
    path('students/', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),

    # Course API URLs
    path('courses/', views.CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),

    # Grade API URLs
    path('grades/', views.GradeListCreateView.as_view(), name='grade-list-create'),
    path('grades/<int:pk>/', views.GradeDetailView.as_view(), name='grade-detail'),

    # Attendance API URLs
    path('attendance/', views.AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('attendance/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance-detail'),

    # Performance API URLs
    path('performance/', views.PerformanceListCreateView.as_view(), name='performance-list-create'),
    path('performance/<int:pk>/', views.PerformanceDetailView.as_view(), name='performance-detail'),

    # Internship API URLs
    path('internships/', views.InternshipListCreateView.as_view(), name='internship-list-create'),
    path('internships/<int:pk>/', views.InternshipDetailView.as_view(), name='internship-detail'),
]
