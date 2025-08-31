from django.db import models

class Teacher(models.Model):
    tname = models.CharField(max_length=100)
    tprefer = models.CharField(max_length=100)
    tgmail = models.EmailField()
    ttimings = models.CharField(max_length=50)
    gender = models.CharField(max_length=20)
    tTotalfee = models.CharField(max_length=20)
    tfee = models.CharField(max_length=20)
    ttime = models.CharField(max_length=20)

    class Meta:
        db_table = "teacher"    # existing DB table
        managed = False         # Django won’t create/alter


class Student(models.Model):
    # id = None
    sname = models.CharField(max_length=100)
    sprefer = models.CharField(max_length=100)
    sgmail = models.EmailField(primary_key=True)
    stimings = models.CharField(max_length=50)

    class Meta:
        db_table = "student"    
        managed = False


class TeacherStudent(models.Model):  
    sgmail = models.EmailField(unique=True)
    tname = models.CharField(max_length=100, primary_key=True)
    sname = models.CharField(max_length=100, null=True, blank=True)
    sprefer = models.CharField(max_length=100, null=True, blank=True)
    # sgmail = models.EmailField(unique=True)
    stimings = models.CharField(max_length=30, null=True, blank=True)
    removed = models.BooleanField(default=False)

    class Meta:
        db_table = "teacherstudent"   
        managed = False
