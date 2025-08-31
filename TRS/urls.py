from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # homepage
    path('tech/', views.tech, name='tech'),
    path('soft/', views.soft, name='soft'),
    path('contact/', views.contact, name='contact'),  # added trailing slash
    path('teach/', views.teacher_dashboard, name='teach'),  # trailing slash
    path('join/', views.join, name='join'),
    path('login/', views.signin, name='login'),  # lowercase
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('remove_student/', views.remove_student, name='remove_student'),
    path('undo_student/', views.undo_student, name='undo_student'),
    path('update_preference/', views.update_preference, name='update_preference'),
    path('send_mail/',views.send_mail,name='send_mail'),
    path('fpassword/', views.forgot_password, name="fpassword"),   # Step 1
    path('fotp/', views.verify_otp, name="fotp"),                 # Step 2
    path('reset_password/', views.reset_password, name="reset_password"),
]
