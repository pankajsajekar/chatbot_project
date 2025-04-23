# students/models.py

from django.db import models
from django.utils import timezone

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when a record is created
    updated_at = models.DateTimeField(auto_now=True)      # Automatically set when a record is updated

    class Meta:
        abstract = True

class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


from django.utils import timezone

def generate_course_code(prefix=''):
    """Generate a unique with an optional prefix."""
    timestamp = str(int(timezone.now().timestamp()))
    return f"{prefix}{timestamp[:6]}"


# Define the Course model with additional fields
class Course(TimestampMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    credit_hours = models.IntegerField(null=True, blank=True)
    instructor_name = models.CharField(max_length=255, null=True, blank=True)
    
    # New additional fields
    prerequisites = models.TextField(null=True, blank=True)
    schedule = models.CharField(max_length=255, null=True, blank=True)
    level = models.CharField(max_length=50, choices=[('Undergraduate', 'Undergraduate'), ('Graduate', 'Graduate')], null=True, blank=True)
    syllabus_link = models.URLField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.course_code:
            self.course_code = generate_course_code(prefix=self.name[:4].upper())
        super().save(*args, **kwargs)
            


# Define the Student model with additional fields
class Student(TimestampMixin, SoftDeleteMixin, models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)  
    address = models.TextField(null=True, blank=True) 
    department = models.CharField(max_length=255, null=True, blank=True)
    enrollment_year = models.IntegerField(null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    marital_status = models.CharField(max_length=10, choices=[('Single', 'Single'), ('Married', 'Married')], null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    guardian_name = models.CharField(max_length=255, null=True, blank=True)
    guardian_email = models.EmailField(null=True, blank=True)
    guardian_phone_number = models.CharField(max_length=15, null=True, blank=True)
    
    emergency_contact_name = models.CharField(max_length=255, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, null=True, blank=True)

    scholarship_awarded = models.BooleanField(default=False)
    scholarship_name = models.CharField(max_length=255, null=True, blank=True)
    financial_aid_status = models.CharField(max_length=100, choices=[('None', 'None'), ('Full', 'Full'), ('Partial', 'Partial')], default='None')

    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Graduated', 'Graduated'), ('On Leave', 'On Leave')], default='Active')

    has_internship = models.BooleanField(default=False)
    internship_details = models.TextField(null=True, blank=True)
    extracurricular_activities = models.TextField(null=True, blank=True)

    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    academic_status = models.CharField(max_length=50, choices=[('Good Standing', 'Good Standing'), ('Probation', 'Probation')], default='Good Standing')

    profile_picture = models.ImageField(upload_to='student_pictures/', null=True, blank=True)

    def __str__(self):
        return self.name


class Grade(TimestampMixin, SoftDeleteMixin, models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, null=True, blank=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    exam_type = models.CharField(max_length=50, choices=[('Mid-Term', 'Mid-Term'), ('Final', 'Final'), ('Continuous', 'Continuous')], null=True, blank=True)
    remarks = models.TextField(null=True, blank=True) 
    semester = models.CharField(max_length=50, null=True, blank=True)
    academic_year = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.course.name} - {self.grade}"

    @property
    def percentage(self):
        if self.total_marks and self.total_marks > 0:
            return (self.marks_obtained / self.total_marks) * 100
        return 0


class Attendance(TimestampMixin, SoftDeleteMixin, models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    total_classes = models.IntegerField(null=True, blank=True)
    attended_classes = models.IntegerField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late')], default='Absent')
    remarks = models.TextField(null=True, blank=True)
    
    @property
    def attendance_percentage(self):
        if self.total_classes and self.total_classes > 0:
            return (self.attended_classes / self.total_classes) * 100
        return 0

    def __str__(self):
        return f"{self.student.name} - {self.course.name} - Attendance: {self.attendance_percentage}% on {self.date}"


class Performance(TimestampMixin, SoftDeleteMixin, models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Completed', 'Completed'), ('Ongoing', 'Ongoing'), ('Failed', 'Failed')], default='Ongoing')
    semester = models.CharField(max_length=50, null=True, blank=True)
    academic_year = models.CharField(max_length=10, null=True, blank=True)
    overall_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.course.name} - GPA: {self.gpa} - Status: {self.status}"

    @property
    def performance_status(self):
        if self.gpa and self.gpa >= 3.5:
            return 'Excellent'
        elif self.gpa and self.gpa >= 2.0:
            return 'Good'
        else:
            return 'Needs Improvement'


class Internship(TimestampMixin, SoftDeleteMixin, models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.company_name} - {self.role}"
