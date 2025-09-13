from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import StudentForm, EnrolledClassForm
from .models import Student, EnrolledClass, Teacher

from django.forms import inlineformset_factory
from django.forms import modelformset_factory


EnrolledFormSet = inlineformset_factory(
    Student,
    EnrolledClass,
    form=EnrolledClassForm,
    extra=1,
    can_delete=True
)


def create_student(request):
    EnrolledClassFormSet = modelformset_factory(EnrolledClass, form=EnrolledClassForm, extra=1, can_delete=True)

    levels = StudyLevel.objects.all()
    selected_level_id = request.GET.get('level')


    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        formset = EnrolledClassFormSet(request.POST, queryset=EnrolledClass.objects.none())

        if student_form.is_valid() and formset.is_valid():
            student = student_form.save()
            for form in formset:
                enrollment = form.save(commit=False)
                enrollment.student = student
                enrollment.save()
            return redirect('create_student')
    else:
        student_form = StudentForm()
        formset = EnrolledClassFormSet(queryset=EnrolledClass.objects.none())

    if selected_level_id:
        students = Student.objects.filter(
            enrollments__enrolled_class__level_id=selected_level_id
        ).distinct()
    else:
        students = Student.objects.all()



    return render(request, 'students/student_form.html', {
        'student_form': student_form,
        'formset': formset,
        'students': students,
        'levels': levels,
        'selected_level_id': selected_level_id,

    })


from django.shortcuts import get_object_or_404

def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    # Linked enrolled classes for this student
    EnrolledClassFormSet = modelformset_factory(
        EnrolledClass, form=EnrolledClassForm, extra=0, can_delete=True
    )

    if request.method == 'POST':
        student_form = StudentForm(request.POST, instance=student)
        formset = EnrolledClassFormSet(request.POST, queryset=EnrolledClass.objects.filter(student=student))

        if student_form.is_valid() and formset.is_valid():
            student_form.save()

            # Save formset and assign the student to new added forms
            enrolled_classes = formset.save(commit=False)

            for obj in formset.deleted_objects:
                obj.delete()

            for enrolled in enrolled_classes:
                enrolled.student = student
                enrolled.save()

            return redirect('create_student')  # or a 'student_detail' page
    else:
        student_form = StudentForm(instance=student)
        formset = EnrolledClassFormSet(queryset=EnrolledClass.objects.filter(student=student))

    students = Student.objects.all()

    return render(request, 'students/student_form.html', {
        'form': student_form,
        'formset': formset,
        'students': students,
        'edit_mode': True,
        'edit_id': student.id,
    })


def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('create_student')

# views.py
from django.shortcuts import render, redirect
from .models import StudyLevel, Class, EnrolledClass, Attendance, Student
from django.utils import timezone
from django.contrib import messages

def mark_attendance(request):
    levels = StudyLevel.objects.all()
    classrooms = Class.objects.none()
    students = []

    selected_level = request.GET.get('level')
    selected_classroom = request.GET.get('classroom')
    selected_date = request.GET.get('date') or timezone.now().date()

    if selected_level:
        classrooms = Class.objects.filter(level_id=selected_level)

    if selected_level and selected_classroom:
        enrolled_classes = EnrolledClass.objects.filter(
            enrolled_class_id=selected_classroom,
            enrolled_class__level_id=selected_level
        ).select_related('student')

        students = [e.student for e in enrolled_classes]

    if request.method == 'POST':
        data = request.POST
        date = data.get('date') or timezone.now().date()
        for key in data:
            if key.startswith('status_'):
                student_id = key.split('_')[1]
                status = data[key]
                enrolled = EnrolledClass.objects.get(
                    student_id=student_id,
                    enrolled_class_id=selected_classroom
                )
                Attendance.objects.update_or_create(
                    student_id=student_id,
                    enrolled_class=enrolled,
                    date=date,
                    defaults={'status': status}
                )
        messages.success(request, "Attendance saved successfully.")
        return redirect('mark_attendance')
    if selected_level and selected_classroom and selected_date:
        submitted_attendance = Attendance.objects.filter(
            enrolled_class__enrolled_class__level_id=selected_level,
            enrolled_class__enrolled_class_id=selected_classroom,
            date=selected_date
        ).select_related(
            'enrolled_class__student',
            'enrolled_class__enrolled_class'
        )
    else:
        submitted_attendance = Attendance.objects.none()

    return render(request, 'students/attendance_mark.html', {
        'levels': levels,
        'classrooms': classrooms,
        'students': students,
        'selected_level': selected_level,
        'selected_classroom': selected_classroom,
        'selected_date': selected_date,
        'submitted_attendance': submitted_attendance,

    })



from django.db.models import Sum
from datetime import datetime
from django.shortcuts import render
from .models import StudyLevel, Student, EnrolledClass, Attendance, Payment

def subscription_summary(request):
    levels = StudyLevel.objects.all()
    students_data = []

    selected_level_id = request.GET.get('level')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if selected_level_id and start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        students = Student.objects.filter(
            enrollments__enrolled_class__level_id=selected_level_id
        ).distinct()

        for student in students:
            enrolled_classes = EnrolledClass.objects.filter(
                student=student,
                enrolled_class__level_id=selected_level_id
            ).select_related('enrolled_class')

            total_attendance = 0
            total_estimated = 0
            attendance_details = []

            for enrolled in enrolled_classes:
                class_obj = enrolled.enrolled_class
                attendance_count = Attendance.objects.filter(
                    enrolled_class=enrolled,
                    date__range=(start_date, end_date)
                ).count()

                subtotal = enrolled.monthly_fee * attendance_count
                total_attendance += attendance_count
                total_estimated += subtotal

                attendance_details.append({
                    'class_name': class_obj.name,
                    'attendance_count': attendance_count,
                    'fee': enrolled.monthly_fee,
                    'subtotal': subtotal,
                })

            total_paid = Payment.objects.filter(
                student=student,
                payment_date__range=(start_date, end_date)
            ).aggregate(total=Sum('amount'))['total'] or 0

            remaining = total_estimated - total_paid

            students_data.append({
                'student': student,
                'attendance_details': attendance_details,
                'total_attendance': total_attendance,
                'total_estimated': total_estimated,
                'total_paid': total_paid,
                'remaining': remaining,
            })

    return render(request, 'students/subscription_summary.html', {
        'levels': levels,
        'students_data': students_data,
        'selected_level_id': selected_level_id,
        'start_date': start_date,
        'end_date': end_date,
    })


from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


@require_POST
def update_payment(request):
    student_id = request.POST.get('student_id')
    total_paid = request.POST.get('total_paid')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    level = request.POST.get('level')

    try:
        student = Student.objects.get(id=student_id)
        total_paid = float(total_paid)

        # Create or update a payment record (simplified logic)
        Payment.objects.create(
            student=student,
            amount=total_paid,
            payment_date=timezone.now()  # you can use specific payment_date if needed
        )

        messages.success(request, f"Payment updated for {student.full_name}")
    except Exception as e:
        messages.error(request, f"Error updating payment: {e}")

    return redirect(f"{reverse('subscription_summary')}?level={level}&start_date={start_date}&end_date={end_date}")







from django.shortcuts import render, get_object_or_404
from .models import Student  # Import your Student model

def print_receipt(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Retrieve from GET instead of POST
    total_paid = request.GET.get('total_paid')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    level_id = request.GET.get('level')
    remaining = request.GET.get('remaining')


    level_obj = None
    level_name = "N/A"
    if level_id:
        level_obj = get_object_or_404(StudyLevel, id=level_id)
        level_name = f"{level_obj.level} - {level_obj.school.name} - {level_obj.specialty.name}"


    context = {
        'student': student,
        'student_id': student_id,
        'total_paid': total_paid,
        'start_date': start_date,
        'end_date': end_date,
        'level': level_obj,
        'level_name': level_name,
        'receipt_date': timezone.now().date(),
        'remaining': remaining,
    }

    return render(request, 'students/print_receipt.html', context)



from django.db.models import Sum, F, DecimalField
from decimal import Decimal

def teacher_paycheck(request):
    teachers_data = []
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        teachers = Teacher.objects.all()

        for teacher in teachers:
            total_revenue = Decimal(0)
            total_sessions = 0

            # Loop through teacher's classes
            for course_class in teacher.classes.all():
                enrollments = EnrolledClass.objects.filter(enrolled_class=course_class)

                for enrollment in enrollments:
                    # Count attendance
                    attendance_count = Attendance.objects.filter(
                        enrolled_class=enrollment,
                        date__range=(start_date, end_date)
                    ).count()

                    subtotal = enrollment.monthly_fee * attendance_count
                    total_revenue += subtotal
                    total_sessions += attendance_count

            teacher_paycheck = total_revenue * Decimal("0.66")

            teachers_data.append({
                "teacher": teacher,
                "total_sessions": total_sessions,
                "total_revenue": total_revenue,
                "paycheck": teacher_paycheck,
            })

    return render(request, "teachers/paycheck_summary.html", {
        "teachers_data": teachers_data,
        "start_date": start_date,
        "end_date": end_date,
    })


def control_panel(request):
    study_levels = StudyLevel.objects.all()
    classes = Class.objects.all()
    teachers = Teacher.objects.all()
    students = Student.objects.all()

    return render(request, "students/control_panel.html", {
        "study_levels": study_levels,
        "classes": classes,
        "teachers": teachers,
        "students": students,
    })

from django.shortcuts import render, redirect
from .forms import StudyLevelForm, ClassForm, TeacherForm

def create_study_level(request):
    if request.method == "POST":
        form = StudyLevelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_study_level')
    else:
        form = StudyLevelForm()
    levels = StudyLevel.objects.all()
    return render(request, 'students/create_study_level.html', {'form': form, 'levels': levels})


def create_class(request):
    if request.method == "POST":
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_class')
    else:
        form = ClassForm()

    classes = Class.objects.all()
    return render(request, 'students/create_class.html', {'form': form, 'classes': classes})


def create_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_teacher')
    else:
        form = TeacherForm()

    teachers = Teacher.objects.all()

    return render(request, 'students/create_teacher.html', {'form': form, 'teachers': teachers})

def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('create_teacher', pk=teacher.pk)
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'students/teacher_edit.html', {'form': form, 'teacher': teacher})

def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        teacher.delete()
        return redirect('control_panel')
    return render(request, 'students/teacher_delete.html', {'teacher': teacher})

def class_edit(request, pk):
    classe = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            return redirect('create_class', pk=classe.pk)
    else:
        form = ClassForm(instance=classe)
    return render(request, 'students/class_edit.html', {'form': form, 'classe': classe})

def class_delete(request, pk):
    classe = get_object_or_404(Class, pk=pk)
    if request.method == "POST":
        classe.delete()
        return redirect('control_panel')
    return render(request, 'students/class_delete.html', {'classe': classe})


def level_edit(request, pk):
    level = get_object_or_404(StudyLevel, pk=pk)
    if request.method == 'POST':
        form = StudyLevelForm(request.POST, instance=level)
        if form.is_valid():
            form.save()
            return redirect('create_study_level', pk=level.pk)
    else:
        form = StudyLevelForm(instance=level)
    return render(request, 'students/class_edit.html', {'form': form, 'level': level})

def level_delete(request, pk):
    level = get_object_or_404(StudyLevel, pk=pk)
    if request.method == "POST":
        level.delete()
        return redirect('control_panel')
    return render(request, 'students/level_delete.html', {'level': level})


from django.shortcuts import render, get_object_or_404
from .models import Student

from django.shortcuts import get_object_or_404, render

def student_profile(request, pk):
    student = (
        Student.objects
        .prefetch_related(
            'levels',                          # M2M
            'enrollments__enrolled_class__level',   # class -> level
            'enrollments__enrolled_class__teacher', # optional, if you want teacher
        )
        .get(pk=pk)
    )

    levels = student.levels.all()
    enrollments = (
        student.enrollments
        .select_related('enrolled_class__level', 'enrolled_class__teacher')
        .all()
    )

    return render(request, "students/student_profile.html", {
        "student": student,
        "levels": levels,
        "enrollments": enrollments,
    })

def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_profile', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_edit.html', {'form': form, 'student': student})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        return redirect('create_student')
    return render(request, 'students/student_delete.html', {'student': student})


from django.utils import timezone

def print_subscription_receipt(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if not student.sub_payed:
        messages.error(request, "This student has not paid the subscription yet.")
        return redirect('student_profile', pk=student.id)

    enrollments = student.enrollments.select_related("enrolled_class__level").all()

    context = {
        "student": student,
        "enrollments": enrollments,
        "receipt_date": timezone.now().date(),
    }
    return render(request, "students/print_subscription_receipt.html", context)
