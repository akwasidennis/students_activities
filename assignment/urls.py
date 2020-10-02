from django.urls import path
# from .views import UserListView
from . import views
from cruds_adminlte.urls import crud_for_model
from .forms import SelectCourseForm
from .models import SelectCourse
from django.conf import settings
from .views import GradeUpdateView, StatusUpdateView, CourseUpdateView


app_name = 'assignment_app'
urlpatterns = [
    
    path('register_course/<str:pk>/', views.register_course, name='register-course'),
    path('main_dashboard/<str:pk>/', views.main_dashboard, name='main-dashboard'),
    path('assignment/<int:pk>/<str:i_n>/', views.submit_assignment, name='submit-assignment'),
    path('assignment/delete/<str:pk>/<str:i_n>/', views.del_assignment, name='delete-assignment'),
    path('assignment/update/<str:pk>/', views.update_assignment, name='update-assignment'),
    path('assignment/view_assignment_pdf/<str:pk>/', views.viewAssignmentPDF, name='view-assignment-pdf'),
    path('download_assignment/<str:pk>/', views.download_pdf, name='download-file'),
    path('score_student_section/<str:pk>/<str:a_pk>/', views.student_result, name='score-student-section'),
    path('assignment/all_students/<str:pk>/', views.all_students, name='all-students'),
    path('assignment/dashboard/', views.dashboard, name='dashboard'),
    path('assignment/submission_denied/<str:pk>/<str:i_n>/', views.submission_denied, name='submission-denied'),
    path('assignment/score_student_section/update/<int:pk>/<str:s>/<int:o_pk>/<int:ind>/', GradeUpdateView.as_view(), name='update-grade'),
    
    path('course/update/<str:pk>/', views.update_courses, name='update-courses'),
    
    path('update/<str:pk>/', views.update_submitted, name='update-status'),
    path('view_result/<str:pk>/<str:i_n>/', views.query_results, name='view-result'),
    path('all_courses/<str:pk>/', views.all_courses, name='all-courses'),
    path('del_courses/<str:pk>/', views.del_course, name='del-course'),
    path('del_upload_file/<str:pk>/', views.del_upload_file, name='del-upload-file'),
    path('student_dashboard/', views.student_dashboard, name='student-dashboard'),
    path('del_choose_course/<str:pk>/', views.del_choose_course, name='del-choose-course'),
    path('create_pdf/', views.create_pdf, name='create-pdf'),
    path('reults_denied/<str:pk>/', views.results_denied, name='results-denied'),
    path('student_results_list/<str:c>/<int:pk>/', views.student_results_list, name='student-list'),
    path('grade_student/<int:pk>/<int:index>/', views.grade_student, name='grade-student'),

    path('pdf_view/<str:c>/', views.ViewPDF.as_view(), name="pdf-view"),
    path('pdf_download/<str:c>/', views.DownloadPDF.as_view(), name="pdf-download"),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += crud_for_model(SelectCourse, views=['all_courses'],
                    add_form=SelectCourseForm, update_form=SelectCourseForm )
