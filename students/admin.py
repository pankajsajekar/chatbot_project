# students/admin.py

from django.contrib import admin
from .models import Student, Course, Grade, Attendance, Performance, Internship

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'age', 'email', 'department', 'gpa', 'status')
    search_fields = ('student_id', 'name', 'email')
    list_filter = ('department', 'enrollment_year', 'status')
    ordering = ('name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'department', 'credit_hours', 'instructor_name')
    search_fields = ( 'name', 'instructor_name')
    list_filter = ('department',)
    ordering = ('name',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'grade', 'marks_obtained', 'total_marks', 'exam_type', 'semester')
    search_fields = ('student__name', 'course__name')
    list_filter = ('exam_type', 'semester')
    ordering = ('student', 'course')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'attended_classes', 'total_classes', 'attendance_percentage', 'status')
    search_fields = ('student__name', 'course__name')
    list_filter = ('status', 'course')
    ordering = ('student', 'course')

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'gpa', 'status', 'overall_gpa')
    search_fields = ('student__name', 'course__name')
    list_filter = ('status',)
    ordering = ('student', 'course')

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('student', 'company_name', 'role', 'start_date', 'end_date')
    search_fields = ('student__name', 'company_name')
    list_filter = ('start_date',)
    ordering = ('start_date',)
