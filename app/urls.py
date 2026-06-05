from django.urls import path

from . import views


urlpatterns = [
    path('', views.landing, name='landing'),
    path('plan/<slug:plan_slug>/', views.admin_dashboard, name='admin_dashboard'),
    path('empleado/', views.employee_view, name='employee_view'),
    path('empleado/cursos/', views.employee_courses, name='employee_courses'),
    path('empleado/cursos/<int:course_id>/', views.employee_course_detail, name='employee_course_detail'),
    path('empleado/tareas/', views.employee_tasks, name='employee_tasks'),
    path('jefe/fumigadores/', views.pest_providers, name='pest_providers'),
    path('cliente/', views.customer_view, name='customer_view'),
]
