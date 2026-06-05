from django.db import models
from django.utils import timezone


class Commerce(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    certificate_expiration = models.DateField(null=True, blank=True)
    director_email = models.EmailField(default='directivo@safetrack.local')

    def __str__(self):
        return self.name


class SubscriptionPlan(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    monthly_price = models.PositiveIntegerField()
    description = models.TextField()
    has_courses = models.BooleanField(default=False)
    max_employees = models.PositiveIntegerField(default=10)
    highlighted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Employee(models.Model):
    commerce = models.ForeignKey(Commerce, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=80, default='Empleado')
    area = models.CharField(max_length=80, default='Cocina')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Inspection(models.Model):
    commerce = models.ForeignKey(Commerce, on_delete=models.CASCADE, related_name='inspections')
    inspector_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    surfaces_clean = models.BooleanField(default=False)
    temp_correct = models.BooleanField(default=False)
    pest_traps_ok = models.BooleanField(default=False)
    trash_sealed = models.BooleanField(default=False)
    hands_washed = models.BooleanField(default=False)
    evidence = models.FileField(upload_to='inspection_evidence/', null=True, blank=True)
    director_feedback = models.TextField(blank=True)
    director_feedback_at = models.DateTimeField(null=True, blank=True)

    SANITARY_RULES = [
        ('surfaces_clean', 'Superficies limpias', 'Ambiente higienizado'),
        ('temp_correct', 'Temperatura correcta', 'Cadena fria segura'),
        ('pest_traps_ok', 'Control de plagas', 'Prevencion activa'),
        ('trash_sealed', 'Residuos sellados', 'Manejo responsable'),
        ('hands_washed', 'Lavado de manos', 'Higiene del personal'),
    ]

    def get_score_percentage(self):
        score = sum([
            self.surfaces_clean,
            self.temp_correct,
            self.pest_traps_ok,
            self.trash_sealed,
            self.hands_washed,
        ])
        return (score / 5) * 100

    def is_compliant(self):
        return self.get_score_percentage() == 100

    def sanitary_badges(self):
        return [
            {
                'field': field,
                'label': label,
                'title': title,
                'earned': getattr(self, field),
            }
            for field, label, title in self.SANITARY_RULES
        ]

    def __str__(self):
        return f'{self.commerce.name} - {self.created_at:%Y-%m-%d}'


class CustomerFeedback(models.Model):
    commerce = models.ForeignKey(Commerce, on_delete=models.CASCADE, related_name='feedbacks')
    score = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.commerce.name} - {self.score}/5'


class TrainingCourse(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField()
    estimated_minutes = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class TrainingLesson(models.Model):
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=140)
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class QuizQuestion(models.Model):
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=240)
    option_a = models.CharField(max_length=160)
    option_b = models.CharField(max_length=160)
    option_c = models.CharField(max_length=160)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C')],
    )

    def __str__(self):
        return self.question


class CourseAttempt(models.Model):
    commerce = models.ForeignKey(Commerce, on_delete=models.CASCADE, related_name='course_attempts')
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='attempts')
    employee_name = models.CharField(max_length=100)
    score = models.PositiveIntegerField()
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.employee_name} - {self.course.title} ({self.score}%)'


class SanitationTask(models.Model):
    commerce = models.ForeignKey(Commerce, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=140)
    instructions = models.TextField()
    assigned_to = models.CharField(max_length=100)
    due_date = models.DateField(null=True, blank=True)
    employee_notes = models.TextField(blank=True)
    evidence = models.FileField(upload_to='task_evidence/', null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    manager_feedback = models.TextField(blank=True)
    approved = models.BooleanField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def is_completed(self):
        return self.completed_at is not None

    def __str__(self):
        return self.title


class PestControlProvider(models.Model):
    name = models.CharField(max_length=140)
    phone = models.CharField(max_length=40)
    service_area = models.CharField(max_length=140)
    certified = models.BooleanField(default=True)
    certification_expiration = models.DateField(null=True, blank=True)
    price_level = models.CharField(
        max_length=20,
        choices=[
            ('economico', 'Economico'),
            ('medio', 'Medio'),
            ('premium', 'Premium'),
        ],
        default='medio',
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=19.432608)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=-99.133209)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
