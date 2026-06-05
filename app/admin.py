from django.contrib import admin

from .models import (
    Commerce,
    CourseAttempt,
    CustomerFeedback,
    Employee,
    Inspection,
    PestControlProvider,
    QuizQuestion,
    SanitationTask,
    SubscriptionPlan,
    TrainingCourse,
    TrainingLesson,
)


@admin.register(Commerce)
class CommerceAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'certificate_expiration', 'director_email')


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('commerce', 'inspector_name', 'created_at', 'get_score_percentage', 'evidence', 'director_feedback_at')
    list_filter = ('created_at', 'commerce')


@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('commerce', 'score', 'created_at')
    list_filter = ('score', 'created_at')


admin.site.register(TrainingCourse)
admin.site.register(TrainingLesson)
admin.site.register(QuizQuestion)
admin.site.register(CourseAttempt)
admin.site.register(SanitationTask)
admin.site.register(PestControlProvider)
admin.site.register(SubscriptionPlan)
admin.site.register(Employee)
