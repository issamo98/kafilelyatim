from django.urls import path
from .views import create_student, edit_student, delete_student, mark_attendance, subscription_summary, update_payment, \
    print_receipt, teacher_paycheck, control_panel, create_teacher, create_class, create_study_level, student_profile, \
    student_delete, student_edit, print_subscription_receipt, teacher_edit, teacher_delete, class_edit, class_delete, \
    level_edit, level_delete

urlpatterns = [
    path('', create_student, name='create_student'),
    path('edit/<int:pk>/', edit_student, name='edit_student'),
    path('delete/<int:pk>/', delete_student, name='delete_student'),
    path('attendance/mark/', mark_attendance, name='mark_attendance'),
    # urls.py
    path('subscription-summary/', subscription_summary, name='subscription_summary'),
    path('subscription/update-payment/', update_payment, name='update_payment'),
    path('receipt/<int:student_id>', print_receipt, name='print_receipt'),
    path('teachers/paycheck-summary', teacher_paycheck, name='teacher_paycheck'),
    path("control-panel/", control_panel, name="control_panel"),
    path("create-study-level/", create_study_level, name="create_study_level"),
    path("create-class/", create_class, name="create_class"),
    path("create-teacher/", create_teacher, name="create_teacher"),
    path('teacher/<int:pk>/edit/', teacher_edit, name='teacher_edit'),
    path('teacher/<int:pk>/delete/', teacher_delete, name='teacher_delete'),
    path('class/<int:pk>/edit/', class_edit, name='class_edit'),
    path('class/<int:pk>/delete/', class_delete, name='class_delete'),

    path('level/<int:pk>/edit/', level_edit, name='level_edit'),
    path('level/<int:pk>/delete/', level_delete, name='level_delete'),


    path("student/<int:pk>/", student_profile, name="student_profile"),
    path('student/<int:pk>/edit/', student_edit, name='student_edit'),
    path('student/<int:pk>/delete/', student_delete, name='student_delete'),

    path('students/<int:student_id>/print-receipt/', print_subscription_receipt, name='print_subscription_receipt'),





]