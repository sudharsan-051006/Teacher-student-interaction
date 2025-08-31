from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Teacher, Student, TeacherStudent
from django.contrib import messages
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from email.mime.base import MIMEBase
from email import encoders
from django.conf import settings
import random 
from django.contrib.auth.models import User

# ---------------------- PUBLIC VIEWS ---------------------- #

def home(request):
    return render(request, "project/project.html")

def tech(request):
    return render(request, "project/tech.html")

def soft(request):
    return render(request, "project/SoftSkill.html")

def signin(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            msg = 'Error: Invalid login credentials.'
            form = AuthenticationForm(request.POST)
            return render(request, 'project/login.html', {'form': form, 'msg': msg})
    else:
        form = AuthenticationForm()
    return render(request, 'project/login.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST['username']  # user’s email
        ass = str(random.randint(1000, 9999))  # OTP as string

        # Store OTP in session for later verification
        request.session['otp'] = ass
        request.session['username'] = username  

        # Setup SMTP
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            subject = "Your OTP for Password Reset"
            body = f"Your OTP is {ass}"
            message = f"Subject: {subject}\n\n{body}"

            s.sendmail(settings.EMAIL_HOST_USER, username, message)
            s.quit()

            messages.success(request, "OTP sent to your email.")
            return redirect('fotp')  # create another page for OTP input

        except Exception as e:
            messages.error(request, f"Error sending email: {str(e)}")

    return render(request, 'project/forgot_password.html')



def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        saved_otp = request.session.get('otp')
        username = request.session.get('username')

        if entered_otp == saved_otp:
            messages.success(request, "OTP Verified. Now reset your password.")
            return redirect('reset_password')  # take user to reset password form
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, 'project/otp.html')

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        username = request.session.get('username')  # from OTP step

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('reset_password')

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully! Please login.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found")

    return render(request, 'project/reset_password.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            return redirect('/')
        else:
            return render(request, 'project/sign.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'project/sign.html', {'form': form})


def signout(request):
    logout(request)
    return redirect('/login')


# ---------------------- TEACHER VIEWS ---------------------- #

@login_required(login_url="login")
def join(request):
    message, status = None, None

    # Check if logged-in user is already a teacher
    if Teacher.objects.filter(tgmail=request.user.username).exists():
        message = "You are already registered as a teacher."
        status = "error"
        return render(request, "project/join.html", {"msg": message, "status": status})

    if request.method == "POST":
        name = request.POST.get("name")
        prefer = request.POST.get("tprefer")
        sex = request.POST.get("gender")
        Totalfee = request.POST.get("Totalfee")
        Fee = request.POST.get("fee")
        duration = request.POST.get("Ttime")
        timings = request.POST.get("ttimings")

        # Check if all fields are filled
        if all([name, prefer, Totalfee, Fee, duration, timings]):

            # Check if the 'prefer' already exists
            if Teacher.objects.filter(tprefer=prefer).exists():
                message = f"The preference '{prefer}' is already taken. Please choose a different one."
                status = "error"
            else:
                # Create Teacher record
                Teacher.objects.create(
                    tname=name,
                    tprefer=prefer,
                    tgmail=request.user.username,
                    ttimings=timings,
                    gender=sex,
                    tTotalfee=Totalfee,
                    ttime=duration,
                    tfee=Fee,
                )
                message = "Registration successful!"
                status = "success"
        else:
            message = "Please fill in all fields."
            status = "error"

    return render(request, "project/join.html", {"msg": message, "status": status})

@login_required(login_url="login")
def teacher_dashboard(request):
    teacher_email = request.user.username
    try:
        teacher = Teacher.objects.get(tgmail=teacher_email)
    except Teacher.DoesNotExist:
        messages.error(request, "You are not registered as a teacher yet.")
        return redirect('/join')

    # Teacher preference
    teacher_pref = teacher.tprefer

    # Get all matching students (from Student table)
    matching_students = Student.objects.filter(sprefer=teacher_pref)

    # Add new matches to TeacherStudent
    for student in matching_students:
        TeacherStudent.objects.get_or_create(
            tname=teacher.tname,
            sgmail=student.sgmail,
            defaults={
                'sname': student.sname,
                'sprefer': student.sprefer,
                'stimings': student.stimings,
                'removed': False
            }
        )

    # Fetch only students matching current teacher preference
    teacher_students = TeacherStudent.objects.filter(
        tname=teacher.tname,
        sprefer=teacher_pref
    )

    rows = [
        [s.sname, s.sprefer, s.sgmail, s.stimings, s.removed]
        for s in teacher_students
    ]

    return render(request, "project/teachview.html", {
        "teacher_pref": teacher_pref,
        "rows": rows
    })



@login_required(login_url="login")
def update_preference(request):
    if request.method == "POST":
        new_prefer = request.POST.get("tprefer")
        if new_prefer:
            try:
                # Update only the teacher's preference
                teacher = Teacher.objects.get(tgmail=request.user.username)
                teacher.tprefer = new_prefer
                teacher.save()

                messages.success(request, "Preference updated successfully!")

            except Teacher.DoesNotExist:
                messages.error(request, "Teacher not found.")
        else:
            messages.error(request, "Please select a valid preference.")
    return redirect("teach")

@login_required(login_url="login")
def send_mail(request):
    if request.method == "POST":
        teacher_email = request.user.username
        message_text = request.POST.get("message")
        uploaded_file = request.FILES.get("attachment")  # optional

        try:
            # Get logged-in teacher instance
            teacher = Teacher.objects.get(tgmail=teacher_email)

            # Registered students (not removed)
            registered_students = TeacherStudent.objects.filter(
                tname=teacher.tname,
                removed=False
            ).values_list('sgmail', flat=True)

            if not registered_students:
                messages.warning(request, "No registered students to send mail to.")
                return redirect("teach")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = ",".join(registered_students)
            msg['Subject'] = "Message from your Teacher"

            # Attach text
            msg.attach(MIMEText(message_text, 'plain'))

            # Attach file if uploaded
            if uploaded_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(uploaded_file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{uploaded_file.name}"'
                )
                msg.attach(part)

            # Send email via SMTP
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.sendmail(msg['From'], registered_students, msg.as_string())
            smtp.quit()

            messages.success(request, "Mail sent successfully!")

        except Teacher.DoesNotExist:
            messages.error(request, "Teacher not found.")
        except Exception as e:
            messages.error(request, f"Error sending mail: {str(e)}")

    return redirect("teach")


@login_required(login_url="login")
def remove_student(request):
    if request.method == "POST":
        email = request.POST.get("email")
        students = TeacherStudent.objects.filter(sgmail=email)
        if students.exists():
            students.update(removed=True)  # mark all matching students as removed
            messages.success(request, f"{students.count()} student(s) removed.")
        else:
            messages.error(request, "Student not found.")
    return redirect('teach')



@login_required(login_url="login")
def undo_student(request):
    if request.method == "POST":
        email = request.POST.get("email")
        students = TeacherStudent.objects.filter(sgmail=email)
        if students.exists():
            students.update(removed=False)  # update all matching rows
            messages.success(request, f"{students.count()} student(s) restored.")
        else:
            messages.error(request, "Student not found.")
    return redirect('teach')

# ---------------------- STUDENT CONTACT FORM ---------------------- #

@csrf_exempt
def contact(request):
    message, status = None, None

    if request.method == "POST":
        name = request.POST.get("name")
        prefer = request.POST.get("prefer")
        gmail = request.POST.get("gmail")
        timings = request.POST.get("timings")

        if name and prefer and gmail and timings:
            Student.objects.create(
                sname=name,
                sprefer=prefer,
                sgmail=gmail,
                stimings=timings
            )
            message = "✅ Form submitted successfully!"
            status = "success"
        else:
            message = "⚠️ Please fill all fields."
            status = "error"

    table_data = Teacher.objects.all()
    return render(request, "project/contact.html", {
        "table_data": table_data,
        "message": message,
        "status": status
    })