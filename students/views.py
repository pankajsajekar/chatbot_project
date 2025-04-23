# students/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import generics
from .models import Student, Course, Grade, Attendance, Performance, Internship
from .serializers import StudentSerializer, CourseSerializer, GradeSerializer, AttendanceSerializer, PerformanceSerializer, InternshipSerializer


# API view for Dashboard
class DashboardView(APIView):
    def get(self, request):
        # Example data for the dashboard
        data = {
            "total_students": Student.objects.count(),
            "total_courses": Course.objects.count(),
            "total_grades": Grade.objects.count(),
            "total_attendance": Attendance.objects.count(),
            "total_performance": Performance.objects.count(),
            "total_internships": Internship.objects.count(),
        }
        return Response(data, status=status.HTTP_200_OK)

# API view for Student model (CRUD operations)
class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentProfileView(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        grades = Grade.objects.filter(student=student)
        attendance = Attendance.objects.filter(student=student)
        performance = Performance.objects.filter(student=student)
        internships = Internship.objects.filter(student=student)

        data = {
            "student": StudentSerializer(student).data,
            "grades": GradeSerializer(grades, many=True).data,
            "attendance": AttendanceSerializer(attendance, many=True).data,
            "performance": PerformanceSerializer(performance, many=True).data,
            "internships": InternshipSerializer(internships, many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)

# API view for Course model (CRUD operations)
class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# API view for Grade model (CRUD operations)
class GradeListCreateView(generics.ListCreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

class GradeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

# API view for Attendance model (CRUD operations)
class AttendanceListCreateView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

# API view for Performance model (CRUD operations)
class PerformanceListCreateView(generics.ListCreateAPIView):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

class PerformanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

# API view for Internship model (CRUD operations)
class InternshipListCreateView(generics.ListCreateAPIView):
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer

class InternshipDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer
