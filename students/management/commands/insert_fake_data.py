# students/management/commands/insert_fake_data.py

from django.core.management.base import BaseCommand
from faker import Faker
from students.models import Student, Course, Grade, Attendance, Performance, Internship
from argparse import ArgumentParser

class Command(BaseCommand):
    help = 'Insert fake data into the database'
    
    def add_arguments(self, parser):
        parser.add_argument('--students', type=int, default=10, help='Number of students to create')
        parser.add_argument('--courses', type=int, default=5, help='Number of courses to create')


    def handle(self, *args, **options):
        fake = Faker('en_IN')
        
        num_students = options['students']
        num_courses = options['courses']
        
        self.stdout.write(self.style.SUCCESS(f'Creating {num_students} students and {num_courses} courses...'))
            
        departments = [ 'CSE', 'ECE', 'ME', 'CE', 'EE', 'IT', 'BBA', 'MBA']
        courses_name = [ 'Data Structures', 'Algorithms', 'Database Management Systems', 'Operating Systems', 'Computer Networks', 'Software Engineering', 'Web Development', 'Machine Learning', 'Artificial Intelligence', 'Cloud Computing']

        # Create fake courses
        courses = []
        for _ in range(num_courses):
            course = Course.objects.create(
                name=fake.random_element(elements=courses_name),
                description=fake.text(),
                department=fake.random_element(elements=departments),
                credit_hours=fake.random_int(min=3, max=6),
                instructor_name=fake.name(),
                prerequisites=fake.sentence(),
                schedule=fake.word(),
                level=fake.random_element(elements=('Undergraduate', 'Graduate')),
                syllabus_link=fake.url(),
                is_active=fake.boolean()
            )
            courses.append(course)

        self.stdout.write(self.style.SUCCESS('courses inserted fake data into the database'))
        
        # Create fake students
        students = []
        for _ in range(num_students):
            student = Student.objects.create(
                student_id=fake.random_int(min=1000, max=9999),
                name=fake.name(),
                age=fake.random_int(min=18, max=30),
                email=fake.email(),
                phone_number=fake.phone_number(),
                address=fake.address(),
                department=fake.random_element(elements=departments),
                enrollment_year=fake.year(),
                graduation_year=fake.year(),
                gender=fake.random_element(elements=('Male', 'Female', 'Other')),
                marital_status=fake.random_element(elements=('Single', 'Married')),
                nationality=fake.country(),
                guardian_name=fake.name(),
                guardian_email=fake.email(),
                guardian_phone_number=fake.phone_number(),
                emergency_contact_name=fake.name(),
                emergency_contact_phone=fake.phone_number(),
                scholarship_awarded=fake.boolean(),
                scholarship_name=fake.random_element(elements=departments),
                financial_aid_status=fake.random_element(elements=('None', 'Full', 'Partial')),
                status=fake.random_element(elements=('Active', 'Graduated', 'On Leave')),
                has_internship=fake.boolean(),
                internship_details=fake.text(),
                extracurricular_activities=fake.text(),
                gpa=fake.random_int(min=10, max=40) / 10.0,  # Ensure GPA is a valid decimal (e.g., 3.5)
                academic_status=fake.random_element(elements=('Good Standing', 'Probation')),
                profile_picture=fake.file_name(extension='jpg')
            )
            students.append(student)
            
        
        self.stdout.write(self.style.SUCCESS('students inserted fake data into the database'))

        # Assign grades to students
        for student in students:
            for course in courses:
                Grade.objects.create(
                    student=student,
                    course=course,
                    grade=fake.random_element(elements=('A', 'B', 'C', 'D', 'F')),
                    marks_obtained=fake.random_int(min=50, max=100),  # Ensure marks are valid integers
                    total_marks=100,  # Total marks should be a valid number
                    exam_type=fake.random_element(elements=('Mid-Term', 'Final', 'Continuous')),
                    semester=fake.random_element(elements=('Fall', 'Spring', 'Summer')),
                    academic_year=fake.year(),
                    remarks=fake.sentence(),
                )

        # Assign attendance to students
        for student in students:
            for course in courses:
                Attendance.objects.create(
                    student=student,
                    course=course,
                    total_classes=fake.random_int(min=20, max=50),
                    attended_classes=fake.random_int(min=10, max=50),
                    date=fake.date_this_year(),
                    status=fake.random_element(elements=('Present', 'Absent', 'Late')),
                    remarks=fake.sentence()
                )

        # Assign performance to students
        for student in students:
            for course in courses:
                Performance.objects.create(
                    student=student,
                    course=course,
                    gpa=fake.random_int(min=0, max=40) / 10.0,  # Ensure GPA is valid
                    status=fake.random_element(elements=('Completed', 'Ongoing', 'Failed')),
                    semester=fake.random_element(elements=('Fall', 'Spring', 'Summer')),
                    academic_year=fake.year(),
                    remarks=fake.sentence()
                )

        # Assign internships to students
        for student in students:
            if fake.boolean():
                Internship.objects.create(
                    student=student,
                    company_name=fake.company(),
                    role=fake.job(),
                    start_date=fake.date_this_year(),
                    end_date=fake.date_this_year(),
                    description=fake.text()
                )

        self.stdout.write(self.style.SUCCESS('Successfully inserted fake data into the database'))
