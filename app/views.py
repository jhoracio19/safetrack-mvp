from datetime import timedelta

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

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
    TrainingCourse,
    TrainingLesson,
)


def get_demo_commerce():
    commerce, _ = Commerce.objects.get_or_create(
        id=1,
        defaults={
            'name': 'SafeTrack Demo Store',
            'address': 'Av. Industria 123, Ciudad de Mexico',
            'certificate_expiration': timezone.localdate() + timedelta(days=20),
            'director_email': 'directivo@safetrack.local',
        },
    )
    if not commerce.director_email:
        commerce.director_email = 'directivo@safetrack.local'
        commerce.save(update_fields=['director_email'])
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
            'assigned_to': 'Equipo cocina',
            'due_date': timezone.localdate(),
        },
    )
    SanitationTask.objects.get_or_create(
        commerce=commerce,
        title='Evidencia de lavado de verduras',
        defaults={
            'instructions': 'Tomar foto del area de lavado limpia y registrar notas del proceso de desinfeccion.',
            'assigned_to': 'Preparacion',
            'due_date': timezone.localdate(),
        },
    )

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
            'name': 'SafeTrack Elite',
            'color': 'emerald',
            'message': 'Cumplimiento sanitario sobresaliente verificado por SafeTrack.',
        }
    if percentage >= 80:
        return {
            'name': 'SafeTrack Confiable',
            'color': 'amber',
            'message': 'Buenas practicas sanitarias con oportunidades menores de mejora.',
        }
    return {
        'name': 'SafeTrack En mejora',
        'color': 'rose',
        'message': 'El comercio requiere acciones correctivas prioritarias.',
    }


def notify_director(inspection):
    score = inspection.get_score_percentage()
    subject = f'SafeTrack: inspeccion registrada ({score:.0f}%)'
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


def landing(request):
    get_demo_commerce()
    plans = get_subscription_plans()
    return render(request, 'landing.html', {'plans': plans})


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

        if action == 'delete_employee':
            Employee.objects.filter(
                id=request.POST.get('employee_id'),
                commerce=commerce,
            ).delete()
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

    if commerce.certificate_expiration:
        certificate_expiring = commerce.certificate_expiration <= today + timedelta(days=30)

    context = {
        'commerce': commerce,
        'plan': plan,
        'certificate_expiring': certificate_expiring,
        'latest_inspection': latest_inspection,
        'latest_percentage': latest_percentage,
        'badge': get_badge_level(latest_percentage),
        'sanitary_badges': sanitary_badges,
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
        'course_saved': request.GET.get('course') == '1',
        'locked_feature': request.GET.get('locked') == '1',
    }
    return render(request, 'dashboard.html', context)


def employee_view(request):
    commerce = get_demo_commerce()

    if request.method == 'POST':
        form = InspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.commerce = commerce
            inspection.save()
            notify_director(inspection)
            return redirect(f'{reverse("employee_view")}?success=1')
    else:
        form = InspectionForm()

    checklist_fields = [
        form['surfaces_clean'],
        form['temp_correct'],
        form['pest_traps_ok'],
        form['trash_sealed'],
        form['hands_washed'],
    ]
    return render(request, 'employee.html', {
        'commerce': commerce,
        'form': form,
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
    attempts = commerce.course_attempts.order_by('-created_at')[:8]
    return render(request, 'employee_courses.html', {
        'commerce': commerce,
        'courses': courses,
        'attempts': attempts,
    })


def employee_course_detail(request, course_id):
    commerce = get_demo_commerce()
    course = get_object_or_404(
        TrainingCourse.objects.prefetch_related('lessons', 'questions'),
        id=course_id,
        is_active=True,
    )
    result = None

    if request.method == 'POST':
        employee_name = request.POST.get('employee_name', '').strip() or 'Empleado demo'
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
        'course': course,
        'result': result,
    })


def employee_tasks(request):
    commerce = get_demo_commerce()

    if request.method == 'POST':
        task = get_object_or_404(SanitationTask, id=request.POST.get('task_id'), commerce=commerce)
        form = TaskCompletionForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            completed_task = form.save(commit=False)
            completed_task.completed_at = timezone.now()
            completed_task.approved = None
            completed_task.reviewed_at = None
            completed_task.save()
            return redirect(f'{reverse("employee_tasks")}?success=1')

    return render(request, 'employee_tasks.html', {
        'commerce': commerce,
        'tasks': commerce.tasks.order_by('completed_at', 'due_date'),
        'form': TaskCompletionForm(),
        'success': request.GET.get('success') == '1',
    })


def pest_providers(request):
    get_demo_commerce()
    providers = PestControlProvider.objects.order_by('-certified', 'price_level', 'name')
    return render(request, 'pest_providers.html', {
        'providers': providers,
        'certified_count': providers.filter(certified=True).count(),
        'uncertified_count': providers.filter(certified=False).count(),
    })
