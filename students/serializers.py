# students/serializers.py

from rest_framework import serializers
from .models import Student, Course, Grade, Attendance, Performance, Internship

# Serializer for the Course model
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

# Serializer for the Student model
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

# Serializer for the Grade model
class GradeSerializer(serializers.ModelSerializer):
    # Read-only field to get student name from student ID
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Grade
        fields = '__all__'

# Serializer for the Attendance model
class AttendanceSerializer(serializers.ModelSerializer):
    # Read-only field to get student name from student ID
    student_name = serializers.CharField(source='student.name', read_only=True)
    class Meta:
        model = Attendance
        fields = '__all__'

# Serializer for the Performance model
class PerformanceSerializer(serializers.ModelSerializer):
    # Read-only field to get student name from student ID
    student_name = serializers.CharField(source='student.name', read_only=True)
    class Meta:
        model = Performance
        fields = '__all__'

# Serializer for the Internship model
class InternshipSerializer(serializers.ModelSerializer):
    # Read-only field to get student name from student ID
    student_name = serializers.CharField(source='student.name', read_only=True)
    class Meta:
        model = Internship
        fields = '__all__'
