from django.contrib import admin
from .models import StudyLevel, Class, Student, EnrolledClass, Session, Attendance, Teacher, Speciality, School

admin.site.register(StudyLevel)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(EnrolledClass)
admin.site.register(Session)
admin.site.register(Attendance)
admin.site.register(Teacher)
admin.site.register(Speciality)
admin.site.register(School)


