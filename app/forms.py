from django import forms

from .models import CustomerFeedback, Employee, Inspection, SanitationTask, TrainingCourse


CHECKBOX_CLASSES = (
    'h-6 w-6 rounded border-slate-300 text-emerald-600 '
    'focus:ring-emerald-500'
)


class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = [
            'inspector',
            'surfaces_clean',
            'temp_correct',
            'pest_traps_ok',
            'trash_sealed',
            'hands_washed',
            'evidence',
        ]
        labels = {
            'inspector': 'Nombre del responsable',
            'surfaces_clean': 'Superficies limpias',
            'temp_correct': 'Temperatura correcta',
            'pest_traps_ok': 'Trampas de plagas en buen estado',
            'trash_sealed': 'Basura sellada correctamente',
            'hands_washed': 'Lavado de manos cumplido',
            'evidence': 'Evidencia fotografica',
        }
        widgets = {
            'inspector': forms.Select(attrs={
                'class': (
                    'w-full rounded-lg border border-slate-300 bg-white px-4 py-3 '
                    'text-base text-slate-900 shadow-sm focus:border-emerald-500 '
                    'focus:outline-none focus:ring-2 focus:ring-emerald-200'
                ),
            }),
            'surfaces_clean': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'temp_correct': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'pest_traps_ok': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'trash_sealed': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'hands_washed': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'evidence': forms.ClearableFileInput(attrs={
                'class': (
                    'block w-full rounded-lg border border-dashed border-slate-300 bg-slate-50 '
                    'px-4 py-4 text-sm text-slate-700 file:mr-4 file:rounded-lg file:border-0 '
                    'file:bg-slate-900 file:px-4 file:py-2 file:text-sm file:font-bold file:text-white '
                    'hover:bg-slate-100'
                ),
                'accept': 'image/*',
            }),
        }

    def __init__(self, *args, **kwargs):
        commerce = kwargs.pop('commerce', None)
        super().__init__(*args, **kwargs)
        if commerce:
            self.fields['inspector'].queryset = commerce.employees.filter(is_active=True)


class CustomerFeedbackForm(forms.ModelForm):
    class Meta:
        model = CustomerFeedback
        fields = ['score', 'comment']
        labels = {
            'score': 'Calificacion',
            'comment': 'Comentario',
        }
        widgets = {
            'score': forms.Select(
                choices=[
                    (5, '★★★★★ Excelente'),
                    (4, '★★★★☆ Bueno'),
                    (3, '★★★☆☆ Regular'),
                    (2, '★★☆☆☆ Malo'),
                    (1, '★☆☆☆☆ Muy malo'),
                ],
                attrs={
                    'class': (
                        'w-full rounded-lg border border-slate-300 bg-white px-4 py-3 '
                        'text-base text-slate-900 shadow-sm focus:border-emerald-500 '
                        'focus:outline-none focus:ring-2 focus:ring-emerald-200'
                    ),
                },
            ),
            'comment': forms.Textarea(attrs={
                'class': (
                    'w-full rounded-lg border border-slate-300 bg-white px-4 py-3 '
                    'text-base text-slate-900 shadow-sm focus:border-emerald-500 '
                    'focus:outline-none focus:ring-2 focus:ring-emerald-200'
                ),
                'rows': 4,
                'placeholder': 'Cuéntanos cómo fue tu experiencia',
            }),
        }


class TaskCompletionForm(forms.ModelForm):
    class Meta:
        model = SanitationTask
        fields = ['employee_notes', 'evidence']
        labels = {
            'employee_notes': 'Notas del empleado',
            'evidence': 'Foto de evidencia',
        }
        widgets = {
            'employee_notes': forms.Textarea(attrs={
                'class': (
                    'w-full rounded-lg border border-slate-300 bg-white px-4 py-3 '
                    'text-base text-slate-900 shadow-sm focus:border-emerald-500 '
                    'focus:outline-none focus:ring-2 focus:ring-emerald-200'
                ),
                'rows': 3,
                'placeholder': 'Ej. Se sanitizo refrigerador superior y se separaron carnes de verduras.',
            }),
            'evidence': forms.ClearableFileInput(attrs={
                'class': (
                    'block w-full rounded-lg border border-dashed border-slate-300 bg-slate-50 '
                    'px-4 py-4 text-sm text-slate-700 file:mr-4 file:rounded-lg file:border-0 '
                    'file:bg-slate-900 file:px-4 file:py-2 file:text-sm file:font-bold file:text-white '
                    'hover:bg-slate-100'
                ),
                'accept': 'image/*',
            }),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'role', 'area']
        labels = {
            'name': 'Nombre',
            'role': 'Puesto',
            'area': 'Area',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
                'placeholder': 'Ej. Mariana Lopez',
            }),
            'role': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
                'placeholder': 'Ej. Encargada de cocina',
            }),
            'area': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
                'placeholder': 'Ej. Refrigeracion',
            }),
        }


class CourseCreationForm(forms.Form):
    title = forms.CharField(
        label='Titulo del curso',
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
            'placeholder': 'Ej. Manejo de alimentos listos para consumo',
        }),
    )
    description = forms.CharField(
        label='Descripcion',
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
            'rows': 3,
        }),
    )
    lesson_title = forms.CharField(
        label='Titulo de la leccion',
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
        }),
    )
    video_url = forms.URLField(
        label='URL del Video (YouTube/Vimeo)',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
            'placeholder': 'Ej. https://www.youtube.com/watch?v=...',
        }),
    )
    lesson_content = forms.CharField(
        label='Contenido interactivo',
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
            'rows': 4,
            'placeholder': 'Incluye instrucciones, pasos y situaciones que el empleado debe resolver.',
        }),
    )
    question = forms.CharField(
        label='Pregunta de validacion',
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
        }),
    )
    option_a = forms.CharField(label='Opcion A')
    option_b = forms.CharField(label='Opcion B')
    option_c = forms.CharField(label='Opcion C')
    correct_option = forms.ChoiceField(
        label='Respuesta correcta',
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C')],
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ['option_a', 'option_b', 'option_c']:
            self.fields[name].widget.attrs.update({
                'class': 'w-full rounded-lg border border-slate-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200',
            })
