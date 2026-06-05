import csv
from datetime import timedelta

from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

from .forms import CourseCreationForm, CustomerFeedbackForm, EmployeeForm, InspectionForm, TaskCompletionForm
from .models import (
    Commerce,
    CourseAttempt,
    Employee,
    Inspection,
    PestControlProvider,
    QuizQuestion,
    SanitationTask,
    SubscriptionPlan,
    TaskEvidencePhoto,
    TrainingCourse,
    TrainingLesson,
)


def get_demo_commerce():
    commerce, _ = Commerce.objects.get_or_create(
        id=1,
        defaults={
            'name': 'EcoTrust Demo Store',
            'address': 'Av. Industria 123, Ciudad de Mexico',
            'certificate_expiration': timezone.localdate() + timedelta(days=20),
            'director_email': 'directivo@ecotrust.local',
        },
    )
    if not commerce.director_email:
        commerce.director_email = 'directivo@ecotrust.local'
        commerce.save(update_fields=['director_email'])
    updates = {}
    old_brand = 'Safe' + 'Track'
    old_domain = 'safe' + 'track'
    if old_brand in commerce.name:
        updates['name'] = commerce.name.replace(old_brand, 'EcoTrust')
    if old_domain in commerce.director_email:
        updates['director_email'] = commerce.director_email.replace(old_domain, 'ecotrust')
    if updates:
        for field, value in updates.items():
            setattr(commerce, field, value)
        commerce.save(update_fields=list(updates.keys()))
    seed_demo_platform(commerce)
    return commerce


def get_subscription_plans():
    basic, _ = SubscriptionPlan.objects.get_or_create(
        slug='basico',
        defaults={
            'name': 'Plan Basico',
            'monthly_price': 899,
            'description': 'Operacion sanitaria esencial con tareas, evidencias, feedback directivo, proveedores y vista publica.',
            'has_courses': False,
            'max_employees': 8,
        },
    )
    premium, _ = SubscriptionPlan.objects.get_or_create(
        slug='premium',
        defaults={
            'name': 'Plan Premium',
            'monthly_price': 1499,
            'description': 'Todo el plan Basico mas academia sanitaria, cuestionarios, resultados de capacitacion y creacion de cursos.',
            'has_courses': True,
            'max_employees': 30,
            'highlighted': True,
        },
    )
    return [basic, premium]


def get_plan_or_default(plan_slug):
    get_subscription_plans()
    return get_object_or_404(SubscriptionPlan, slug=plan_slug)


def seed_demo_platform(commerce):
    get_subscription_plans()
    Employee.objects.get_or_create(
        commerce=commerce,
        name='Mariana Lopez',
        defaults={'role': 'Encargada de cocina', 'area': 'Refrigeracion'},
    )
    Employee.objects.get_or_create(
        commerce=commerce,
        name='Luis Hernandez',
        defaults={'role': 'Auxiliar de preparacion', 'area': 'Frutas y verduras'},
    )
    Employee.objects.get_or_create(
        commerce=commerce,
        name='Ana Martinez',
        defaults={'role': 'Supervisora de turno', 'area': 'Piso operativo'},
    )
    cold_course, _ = TrainingCourse.objects.get_or_create(
        title='Manejo seguro de refrigeracion',
        defaults={
            'description': 'Aprende a separar alimentos, validar temperaturas y prevenir contaminacion cruzada.',
            'estimated_minutes': 12,
        },
    )
    TrainingLesson.objects.get_or_create(
        course=cold_course,
        order=1,
        defaults={
            'title': 'Orden correcto dentro del refrigerador',
            'content': 'Los alimentos listos para consumo van arriba. Carnes, pollo y pescado crudos deben ir abajo en recipientes cerrados para evitar goteos.',
        },
    )
    TrainingLesson.objects.get_or_create(
        course=cold_course,
        order=2,
        defaults={
            'title': 'Temperatura y evidencia',
            'content': 'Registra temperatura visible y toma evidencia cuando cierres una tarea. La zona segura depende del producto, pero el control continuo reduce riesgos.',
        },
    )
    QuizQuestion.objects.get_or_create(
        course=cold_course,
        question='Donde deben colocarse carnes crudas para evitar contaminacion cruzada?',
        defaults={
            'option_a': 'En la parte superior',
            'option_b': 'En la parte inferior, cerradas y separadas',
            'option_c': 'Junto a alimentos listos para servir',
            'correct_option': 'B',
        },
    )
    QuizQuestion.objects.get_or_create(
        course=cold_course,
        question='Que evidencia ayuda a validar una tarea de refrigeracion?',
        defaults={
            'option_a': 'Foto del acomodo y temperatura',
            'option_b': 'Solo un comentario verbal',
            'option_c': 'Ninguna evidencia',
            'correct_option': 'A',
        },
    )

    produce_course, _ = TrainingCourse.objects.get_or_create(
        title='Lavado y desinfeccion de frutas y verduras',
        defaults={
            'description': 'Buenas practicas para limpiar, desinfectar y almacenar vegetales antes de preparar alimentos.',
            'estimated_minutes': 8,
        },
    )
    TrainingLesson.objects.get_or_create(
        course=produce_course,
        order=1,
        defaults={
            'title': 'Separar, lavar y desinfectar',
            'content': 'Retira residuos visibles, lava con agua potable y aplica el desinfectante autorizado siguiendo concentracion y tiempo de contacto.',
        },
    )
    QuizQuestion.objects.get_or_create(
        course=produce_course,
        question='Que se debe hacer antes de desinfectar verduras?',
        defaults={
            'option_a': 'Retirar residuos visibles y lavar',
            'option_b': 'Guardarlas directo en refrigerador',
            'option_c': 'Mezclarlas con carne cruda',
            'correct_option': 'A',
        },
    )

    SanitationTask.objects.get_or_create(
        commerce=commerce,
        title='Fotografiar acomodo del refrigerador',
        defaults={
            'instructions': 'Validar que carnes crudas esten abajo, alimentos listos arriba y recipientes cerrados.',
            'assigned_to': 'Mariana Lopez',
            'due_date': timezone.localdate(),
        },
    )
    SanitationTask.objects.get_or_create(
        commerce=commerce,
        title='Evidencia de lavado de verduras',
        defaults={
            'instructions': 'Tomar foto del area de lavado limpia y registrar notas del proceso de desinfeccion.',
            'assigned_to': 'Luis Hernandez',
            'due_date': timezone.localdate(),
        },
    )
    SanitationTask.objects.filter(
        commerce=commerce,
        title='Fotografiar acomodo del refrigerador',
        assigned_to='Equipo cocina',
    ).update(assigned_to='Mariana Lopez')
    SanitationTask.objects.filter(
        commerce=commerce,
        title='Evidencia de lavado de verduras',
        assigned_to='Preparacion',
    ).update(assigned_to='Luis Hernandez')

    PestControlProvider.objects.get_or_create(
        name='BioControl Certificado MX',
        defaults={
            'phone': '55 1000 2200',
            'service_area': 'CDMX Centro y Norte',
            'certified': True,
            'certification_expiration': timezone.localdate() + timedelta(days=180),
            'price_level': 'premium',
            'latitude': 19.432608,
            'longitude': -99.133209,
            'notes': 'Proveedor certificado para calendario semestral requerido.',
        },
    )
    PestControlProvider.objects.get_or_create(
        name='Fumiga Express Local',
        defaults={
            'phone': '55 3200 1188',
            'service_area': 'CDMX y area metropolitana',
            'certified': False,
            'price_level': 'economico',
            'latitude': 19.405000,
            'longitude': -99.160000,
            'notes': 'Opcion economica para fumigaciones adicionales no certificadas.',
        },
    )


def get_badge_level(percentage):
    if percentage is None:
        return {
            'name': 'Pendiente de verificacion',
            'color': 'slate',
            'message': 'Este comercio aun no publica una inspeccion sanitaria reciente.',
        }
    if percentage >= 95:
        return {
            'name': 'EcoTrust Elite',
            'color': 'emerald',
            'message': 'Cumplimiento sanitario sobresaliente verificado por EcoTrust.',
        }
    if percentage >= 80:
        return {
            'name': 'EcoTrust Confiable',
            'color': 'amber',
            'message': 'Buenas practicas sanitarias con oportunidades menores de mejora.',
        }
    return {
        'name': 'EcoTrust En mejora',
        'color': 'rose',
        'message': 'El comercio requiere acciones correctivas prioritarias.',
    }


def notify_director(inspection):
    score = inspection.get_score_percentage()
    subject = f'EcoTrust: inspeccion registrada ({score:.0f}%)'
    message = (
        f'Comercio: {inspection.commerce.name}\n'
        f'Responsable: {inspection.inspector_name}\n'
        f'Indice sanitario: {score:.0f}%\n'
        f'Evidencia cargada: {"si" if inspection.evidence else "no"}\n\n'
        'Revise el panel directivo para confirmar cumplimiento de normas sanitarias.'
    )
    send_mail(
        subject,
        message,
        None,
        [inspection.commerce.director_email],
        fail_silently=True,
    )


def landing_page(request):
    get_subscription_plans()
    plans = SubscriptionPlan.objects.all().order_by('monthly_price')
    return render(request, 'landing.html', {
        'plans': plans,
        'role': 'public',
    })


def login_view(request):
    commerce = get_demo_commerce()
    employees = Employee.objects.filter(commerce=commerce, is_active=True).order_by('name')

    if request.method == 'POST':
        selected_role = request.POST.get('role')
        request.session['role'] = selected_role
        if selected_role == 'admin':
            request.session.pop('employee_name', None)
            return redirect('admin_dashboard', plan_slug='premium')
        if selected_role == 'employee':
            employee_name = request.POST.get('employee_name', '').strip() or request.session.get('employee_name', '')
            if not employee_name:
                first_employee = employees.first()
                employee_name = first_employee.name if first_employee else 'Empleado demo'
            if employee_name:
                request.session['employee_name'] = employee_name
                return redirect(f'{reverse("employee_view")}?{urlencode({"responsable": employee_name})}')

    return render(request, 'login.html', {
        'role': 'public',
        'employees': employees,
    })


def role_select(request, plan_slug):
    get_demo_commerce()
    plan = get_plan_or_default(plan_slug)
    return render(request, 'role_select.html', {
        'plan': plan,
        'role': 'public',
    })


def admin_dashboard(request, plan_slug='premium'):
    commerce = get_demo_commerce()
    plan = get_plan_or_default(plan_slug)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_employee':
            employee_form = EmployeeForm(request.POST)
            if employee_form.is_valid():
                employee = employee_form.save(commit=False)
                employee.commerce = commerce
                employee.save()
            return redirect(f'{reverse("admin_dashboard", args=[plan.slug])}?employees=1')

        if action == 'add_task':
            title = request.POST.get('title', '').strip()
            instructions = request.POST.get('instructions', '').strip()
            assigned_to = request.POST.get('assigned_to', '').strip()
            if title and instructions and assigned_to:
                SanitationTask.objects.create(
                    commerce_id=1,
                    title=title,
                    instructions=instructions,
                    assigned_to=assigned_to,
                    due_date=timezone.localdate(),
                )
            return redirect(f'{reverse("admin_dashboard", args=[plan.slug])}?task=1')

        if action == 'delete_employee':
            Employee.objects.filter(
                id=request.POST.get('employee_id'),
                commerce=commerce,
            ).delete()
            return redirect(f'{reverse("admin_dashboard", args=[plan.slug])}?employees=1')

        if action == 'update_employee':
            employee = Employee.objects.filter(
                id=request.POST.get('employee_id'),
                commerce=commerce,
            ).first()
            if employee:
                previous_name = employee.name
                employee.name = request.POST.get('name', '').strip() or employee.name
                employee.role = request.POST.get('role', '').strip() or employee.role
                employee.area = request.POST.get('area', '').strip() or employee.area
                employee.is_active = request.POST.get('is_active') == 'on'
                employee.save(update_fields=['name', 'role', 'area', 'is_active'])
                if previous_name != employee.name:
                    SanitationTask.objects.filter(
                        commerce=commerce,
                        assigned_to=previous_name,
                    ).update(assigned_to=employee.name)
                    Inspection.objects.filter(
                        commerce=commerce,
                        inspector_name=previous_name,
                    ).update(inspector_name=employee.name)
                    CourseAttempt.objects.filter(
                        commerce=commerce,
                        employee_name=previous_name,
                    ).update(employee_name=employee.name)
            return redirect(f'{reverse("admin_dashboard", args=[plan.slug])}?employees=1')

        if action == 'add_course':
            if not plan.has_courses:
                return redirect(f'{reverse("admin_dashboard", args=[plan.slug])}?locked=1')
            course_form = CourseCreationForm(request.POST)
            if course_form.is_valid():
                course = TrainingCourse.objects.create(
                    title=course_form.cleaned_data['title'],
                    description=course_form.cleaned_data['description'],
                    estimated_minutes=10,
                )
                TrainingLesson.objects.create(
                    course=course,
                    title=course_form.cleaned_data['lesson_title'],
                    content=course_form.cleaned_data['lesson_content'],
                    order=1,
                )
                QuizQuestion.objects.create(
                    course=course,
                    question=course_form.cleaned_data['question'],
                    option_a=course_form.cleaned_data['option_a'],
                    option_b=course_form.cleaned_data['option_b'],
                    option_c=course_form.cleaned_data['option_c'],
                    correct_option=course_form.cleaned_data['correct_option'],
                )
            return redirect(f'{reverse("admin_dashboard", args=[plan.slug])}?course=1')

        if action == 'task_feedback':
            task_id = request.POST.get('task_id')
            task = SanitationTask.objects.filter(id=task_id, commerce=commerce).first()
            if task:
                task.manager_feedback = request.POST.get('manager_feedback', '').strip()
                task.approved = request.POST.get('approved') == 'true'
                task.reviewed_at = timezone.now()
                task.save(update_fields=['manager_feedback', 'approved', 'reviewed_at'])
            return redirect(f'{reverse("admin_dashboard", args=[plan.slug])}?feedback=1')

        inspection_id = request.POST.get('inspection_id')
        if inspection_id:
            Inspection.objects.filter(id=inspection_id, commerce=commerce).update(
                director_feedback=request.POST.get('director_feedback', '').strip(),
                director_feedback_at=timezone.now(),
            )
        return redirect(f'{reverse("admin_dashboard", args=[plan.slug])}?feedback=1')

    today = timezone.localdate()
    certificate_expiring = False
    latest_inspection = commerce.inspections.order_by('-created_at').first()
    latest_percentage = latest_inspection.get_score_percentage() if latest_inspection else None
    sanitary_badges = latest_inspection.sanitary_badges() if latest_inspection else []
    task_queryset = SanitationTask.objects.filter(commerce=commerce)
    task_metrics = task_queryset.aggregate(
        total_pendientes=Count('id', filter=Q(completed_at__isnull=True)),
        total_en_revision=Count('id', filter=Q(completed_at__isnull=False, approved__isnull=True)),
        total_aprobadas=Count('id', filter=Q(approved=True)),
    )

    if commerce.certificate_expiration:
        certificate_expiring = commerce.certificate_expiration <= today + timedelta(days=30)

    context = {
        'commerce': commerce,
        'plan': plan,
        'role': 'admin',
        'certificate_expiring': certificate_expiring,
        'latest_inspection': latest_inspection,
        'latest_percentage': latest_percentage,
        'badge': get_badge_level(latest_percentage),
        'sanitary_badges': sanitary_badges,
        'total_actividades': task_queryset.count(),
        'total_pendientes': task_metrics['total_pendientes'],
        'total_en_revision': task_metrics['total_en_revision'],
        'total_aprobadas': task_metrics['total_aprobadas'],
        'inspections': commerce.inspections.order_by('-created_at')[:10],
        'tasks': commerce.tasks.order_by('-completed_at', 'due_date')[:10],
        'course_attempts': commerce.course_attempts.order_by('-created_at')[:8],
        'courses': TrainingCourse.objects.filter(is_active=True).order_by('-id')[:8],
        'employees': commerce.employees.order_by('-is_active', 'name'),
        'employee_form': EmployeeForm(),
        'course_form': CourseCreationForm(),
        'certified_providers': PestControlProvider.objects.filter(certified=True).count(),
        'feedbacks': commerce.feedbacks.order_by('-created_at')[:10],
        'feedback_saved': request.GET.get('feedback') == '1',
        'employees_saved': request.GET.get('employees') == '1',
        'task_saved': request.GET.get('task') == '1',
        'course_saved': request.GET.get('course') == '1',
        'locked_feature': request.GET.get('locked') == '1',
    }
    return render(request, 'dashboard.html', context)


def export_admin_report(request):
    commerce = get_demo_commerce()
    today = timezone.localdate()
    filename = f'ecotrust-reporte-{today:%Y-%m-%d}.csv'
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['EcoTrust - Reporte general'])
    writer.writerow(['Comercio', commerce.name])
    writer.writerow(['Direccion', commerce.address])
    writer.writerow(['Fecha de exportacion', timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')])
    writer.writerow([])

    writer.writerow(['ACTIVIDADES SANITARIAS'])
    writer.writerow([
        'ID',
        'Titulo',
        'Responsable',
        'Instrucciones',
        'Estado',
        'Fecha limite',
        'Completada en',
        'Aprobada',
        'Fotos evidencia',
        'Notas empleado',
        'Feedback jefe',
    ])
    for task in commerce.tasks.order_by('-completed_at', 'due_date', 'assigned_to'):
        if task.approved is True:
            status = 'Aprobada'
        elif task.approved is False:
            status = 'No aprobada'
        elif task.completed_at:
            status = 'En revision'
        else:
            status = 'Pendiente'
        writer.writerow([
            task.id,
            task.title,
            task.assigned_to,
            task.instructions,
            status,
            task.due_date or '',
            timezone.localtime(task.completed_at).strftime('%Y-%m-%d %H:%M') if task.completed_at else '',
            'Si' if task.approved is True else 'No' if task.approved is False else 'Pendiente',
            task.evidence_photos.count(),
            task.employee_notes,
            task.manager_feedback,
        ])
    writer.writerow([])

    writer.writerow(['INSPECCIONES'])
    writer.writerow([
        'ID',
        'Responsable',
        'Fecha',
        'Indice sanitario',
        'Superficies limpias',
        'Temperatura correcta',
        'Control de plagas',
        'Basura sellada',
        'Lavado de manos',
        'Feedback directivo',
    ])
    for inspection in commerce.inspections.order_by('-created_at'):
        writer.writerow([
            inspection.id,
            inspection.inspector_name,
            timezone.localtime(inspection.created_at).strftime('%Y-%m-%d %H:%M'),
            f'{inspection.get_score_percentage():.0f}%',
            'Si' if inspection.surfaces_clean else 'No',
            'Si' if inspection.temp_correct else 'No',
            'Si' if inspection.pest_traps_ok else 'No',
            'Si' if inspection.trash_sealed else 'No',
            'Si' if inspection.hands_washed else 'No',
            inspection.director_feedback,
        ])
    writer.writerow([])

    writer.writerow(['RESULTADOS DE CAPACITACION'])
    writer.writerow(['ID', 'Usuario', 'Curso', 'Score', 'Aprobo', 'Fecha'])
    for attempt in commerce.course_attempts.select_related('course').order_by('-created_at'):
        writer.writerow([
            attempt.id,
            attempt.employee_name,
            attempt.course.title,
            f'{attempt.score}%',
            'Si' if attempt.passed else 'No',
            timezone.localtime(attempt.created_at).strftime('%Y-%m-%d %H:%M'),
        ])
    writer.writerow([])

    writer.writerow(['FEEDBACK DE CLIENTES'])
    writer.writerow(['ID', 'Fecha', 'Calificacion', 'Comentario'])
    for feedback in commerce.feedbacks.order_by('-created_at'):
        writer.writerow([
            feedback.id,
            timezone.localtime(feedback.created_at).strftime('%Y-%m-%d %H:%M'),
            feedback.score,
            feedback.comment,
        ])

    return response


def employee_view(request):
    commerce = get_demo_commerce()
    employees = Employee.objects.filter(commerce=commerce, is_active=True).order_by('name')
    selected_employee = request.GET.get('responsable', '').strip() or request.session.get('employee_name', '')

    if request.method == 'POST':
        form = InspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.commerce = commerce
            inspection.save()
            request.session['employee_name'] = inspection.inspector_name
            notify_director(inspection)
            redirect_url = f'{reverse("employee_view")}?success=1'
            if inspection.inspector_name:
                redirect_url += f'&{urlencode({"responsable": inspection.inspector_name})}'
            return redirect(redirect_url)
    else:
        form = InspectionForm()

    employee_tasks = SanitationTask.objects.none()
    employee_inspections = Inspection.objects.none()
    employee_task_metrics = {
        'assigned': 0,
        'pending': 0,
        'in_review': 0,
        'approved': 0,
    }
    if selected_employee:
        employee_tasks = commerce.tasks.filter(assigned_to=selected_employee).order_by('completed_at', 'due_date')[:6]
        employee_inspections = commerce.inspections.filter(inspector_name=selected_employee).order_by('-created_at')[:5]
        employee_task_queryset = commerce.tasks.filter(assigned_to=selected_employee)
        employee_task_metrics = {
            'assigned': employee_task_queryset.count(),
            'pending': employee_task_queryset.filter(completed_at__isnull=True).count(),
            'in_review': employee_task_queryset.filter(completed_at__isnull=False, approved__isnull=True).count(),
            'approved': employee_task_queryset.filter(approved=True).count(),
        }

    checklist_fields = [
        form['surfaces_clean'],
        form['temp_correct'],
        form['pest_traps_ok'],
        form['trash_sealed'],
        form['hands_washed'],
    ]
    return render(request, 'employee.html', {
        'commerce': commerce,
        'role': 'employee',
        'form': form,
        'employees': employees,
        'selected_employee': selected_employee,
        'employee_tasks': employee_tasks,
        'employee_inspections': employee_inspections,
        'employee_task_metrics': employee_task_metrics,
        'checklist_fields': checklist_fields,
        'success': request.GET.get('success') == '1',
    })


def customer_view(request):
    commerce = get_demo_commerce()
    latest_inspection = commerce.inspections.order_by('-created_at').first()
    sanitation_percentage = latest_inspection.get_score_percentage() if latest_inspection else None
    badge = get_badge_level(sanitation_percentage)
    sanitary_badges = latest_inspection.sanitary_badges() if latest_inspection else []

    if request.method == 'POST':
        form = CustomerFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.commerce = commerce
            feedback.save()
            return redirect(f'{reverse("customer_view")}?success=1')
    else:
        form = CustomerFeedbackForm()

    return render(request, 'customer.html', {
        'commerce': commerce,
        'role': 'customer',
        'form': form,
        'latest_inspection': latest_inspection,
        'sanitation_percentage': sanitation_percentage,
        'badge': badge,
        'sanitary_badges': sanitary_badges,
        'success': request.GET.get('success') == '1',
    })


def employee_courses(request):
    commerce = get_demo_commerce()
    courses = TrainingCourse.objects.filter(is_active=True).prefetch_related('lessons', 'questions')
    selected_employee = request.session.get('employee_name', '')
    attempts = commerce.course_attempts.order_by('-created_at')
    if selected_employee:
        attempts = attempts.filter(employee_name=selected_employee)
    return render(request, 'employee_courses.html', {
        'commerce': commerce,
        'role': 'employee',
        'selected_employee': selected_employee,
        'courses': courses,
        'attempts': attempts[:8],
    })


def employee_course_detail(request, course_id):
    commerce = get_demo_commerce()
    course = get_object_or_404(
        TrainingCourse.objects.prefetch_related('lessons', 'questions'),
        id=course_id,
        is_active=True,
    )
    result = None
    selected_employee = request.session.get('employee_name', '').strip()

    if request.method == 'POST':
        employee_name = request.POST.get('employee_name', '').strip() or selected_employee or 'Empleado demo'
        request.session['employee_name'] = employee_name
        questions = list(course.questions.all())
        correct = 0
        for question in questions:
            if request.POST.get(f'question_{question.id}') == question.correct_option:
                correct += 1
        score = int((correct / len(questions)) * 100) if questions else 0
        result = CourseAttempt.objects.create(
            commerce=commerce,
            course=course,
            employee_name=employee_name,
            score=score,
            passed=score >= 80,
        )

    return render(request, 'employee_course_detail.html', {
        'commerce': commerce,
        'role': 'employee',
        'course': course,
        'result': result,
        'selected_employee': employee_name if result else selected_employee,
    })


def employee_tasks(request):
    commerce = get_demo_commerce()
    employees = Employee.objects.filter(commerce=commerce, is_active=True).order_by('name')
    selected_employee = request.GET.get('responsable', '').strip() or request.session.get('employee_name', '')

    if request.method == 'POST':
        selected_employee = request.POST.get('responsable', '').strip() or request.session.get('employee_name', '')
        if selected_employee:
            request.session['employee_name'] = selected_employee
        task_filters = {
            'id': request.POST.get('task_id'),
            'commerce': commerce,
        }
        if selected_employee:
            task_filters['assigned_to'] = selected_employee
        task = get_object_or_404(SanitationTask, **task_filters)
        form = TaskCompletionForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            completed_task = form.save(commit=False)
            uploaded_photos = request.FILES.getlist('evidence_photos')
            if uploaded_photos and not completed_task.evidence:
                completed_task.evidence = uploaded_photos[0]
            completed_task.completed_at = timezone.now()
            completed_task.approved = None
            completed_task.reviewed_at = None
            completed_task.save()
            for photo in uploaded_photos:
                TaskEvidencePhoto.objects.create(task=completed_task, image=photo)
            redirect_url = f'{reverse("employee_tasks")}?success=1'
            if selected_employee:
                redirect_url += f'&{urlencode({"responsable": selected_employee})}'
            return redirect(redirect_url)

    tasks = SanitationTask.objects.none()
    if selected_employee:
        tasks = commerce.tasks.filter(assigned_to=selected_employee).order_by('completed_at', 'due_date')

    return render(request, 'employee_tasks.html', {
        'commerce': commerce,
        'role': 'employee',
        'employees': employees,
        'selected_employee': selected_employee,
        'tasks': tasks,
        'has_manager_feedback': tasks.exclude(manager_feedback='').exists(),
        'form': TaskCompletionForm(),
        'success': request.GET.get('success') == '1',
    })


def pest_providers(request):
    get_demo_commerce()
    plan = get_plan_or_default('premium')
    providers = PestControlProvider.objects.order_by('-certified', 'price_level', 'name')
    return render(request, 'pest_providers.html', {
        'role': 'admin',
        'plan': plan,
        'providers': providers,
        'certified_count': providers.filter(certified=True).count(),
        'uncertified_count': providers.filter(certified=False).count(),
    })
