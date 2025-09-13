from django.db import models
from django.utils import timezone

# Optional if using built-in users
from django.contrib.auth.models import User


class Speciality(models.Model):
    SPECIALTIES = (
        ('scientifique', 'Sientifique'),
        ('math', 'Math'),
        ('math technique', 'Math Technique'),
        ('gestion', 'Gestion'),
        ('langue', 'Langue'),
        ('philo', 'Philo'),
        ('aucune', 'Aucune')
    )
    name = models.CharField(choices=SPECIALTIES, max_length=50, null=True)
    def __str__(self):
        return self.name
class School(models.Model):
    SCHOOL_TYPE = (
        ('primaire', 'Primaire'),
        ('cem', 'Cem'),
        ('lycee', 'Lycee'),
    )
    name = models.CharField(max_length=50, choices=SCHOOL_TYPE, null=True)
    def __str__(self):
        return self.name

class StudyLevel(models.Model):
    LEVELS = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    )
    level = models.CharField(max_length=50, choices=LEVELS, null=True)
    specialty = models.ForeignKey(Speciality, on_delete=models.CASCADE, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.level} - {self.school} - {self.specialty}"



class Teacher(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.full_name

# ----------------------------
# CLASS
# ----------------------------
class Class(models.Model):
    name = models.CharField(max_length=100)
    level = models.ForeignKey(StudyLevel, on_delete=models.CASCADE, related_name="classes")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name="classes")

    def __str__(self):
        return f"{self.name} ({self.level.level})"






# ----------------------------
# STUDENT
# ----------------------------
class Student(models.Model):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    levels = models.ManyToManyField(StudyLevel)
    sub_payed = models.BooleanField(null=True, verbose_name="Subscription Paid")
    sub_montant = models.DecimalField(null=True, max_digits=8, decimal_places=2, verbose_name="Subscription Amount")
    created_at = models.DateTimeField(auto_now_add=True)
    parents_name = models.CharField(max_length=100, null=True)
    parents_number = models.CharField(max_length=100, null=True)
    is_orphan = models.BooleanField(null=True)

    def __str__(self):
        return self.full_name


# ----------------------------
# ENROLLED CLASS (per student)
# ----------------------------
class EnrolledClass(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.student.full_name} → {self.enrolled_class.name} (DZD{self.monthly_fee})"



# ----------------------------
# CLASS SESSION
# ----------------------------
class Session(models.Model):
    course_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    topic = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.course_class.name} - {self.date}"


# ----------------------------
# ATTENDANCE (for each session and student)
# ----------------------------
from django.db import models

# models.py

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )

    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True, blank=True)
    enrolled_class = models.ForeignKey('EnrolledClass', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"



class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.amount} DA"
