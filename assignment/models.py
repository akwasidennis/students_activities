from django.db import models
from .utils import Utils
from django.urls import reverse
from django.db import OperationalError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
# from hashid_field import HashidAutoField
import uuid
import os
import random
from binascii import hexlify
# from users.models import SelectCourse

User = get_user_model()

def _createId():
    return random.randint(1, 10000000)    #hexlify(os.urandom(16))

SEMESTER = (
        ('', 'select semester'),
        ('semester one', 'SEMESTER ONE'),
        ('semester two', 'SEMESTER TWO'),
    )
class Semester(models.Model):
    sem = models.CharField("semester", max_length=100, choices=SEMESTER)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    photo = models.ImageField(upload_to="images/")
    attachment = models.FileField(upload_to="attachments/")
    phone = models.CharField(max_length=10)



class RegisterCourse(models.Model):
    CLASS_CHOICES = (
                ('', 'Select class'),
                ('Math1', 'Math 1'),
                ('Math2', 'Math 2'),
                ('Math3', 'Math 3'),
                ('Math4', 'Math 4'),
                )

    COURSE_CHOICES = (
                ('', 'Select a course'),
                ('Integral Equations', 'Integral Equations'),
                ('Real Functions', 'Real Functions'),
                )

    course = models.CharField(choices=COURSE_CHOICES, max_length=100)
    class_or_level = models.CharField(choices=CLASS_CHOICES, max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('assignment_app:submit-assignment', kwargs={'pk': self.user.pk})
    

    def __str__(self):
        return f'{self.user.index_number} {self.course} ({self.class_or_level})'


COLOR_CHOICES = (
                ('', 'Select back color'),
                ('green', 'green'),
                ('blue', 'blue'),
                ('red', 'red'),
                ('burlywood', 'burlywood'),
                ('darkkhaki', 'darkkhaki'),
                ('darkslateblue', 'darkslateblue'),
                ('deeppink', 'deeppink'),
                ('fuchsia', 'fuchsia'),
                ('gold', 'gold'),
                ('indigo', 'indigo'),
                )

class SelectCourse(models.Model):
    # # # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.CharField(max_length=200, primary_key=True, default=_createId)
    courses = models.CharField(_('Course name'), max_length=200)
    choose_back_color = models.CharField(_('Course background'), default='black', max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    sem = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.courses} -----> {self.choose_back_color}'


class StudentOtherCourse(models.Model):
    # # # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.CharField(max_length=200, primary_key=True, default=_createId)
    choose_course = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selectcourse = models.ForeignKey(SelectCourse, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.choose_course




STATUS = (
        ('graded', 'graded'),
        ('ungraded', 'ungraded'),
    )


class UploadedFile(models.Model):
    # # # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.CharField(max_length=200, primary_key=True, default=_createId)
    pdf_file = models.FileField(upload_to="activity/")
    file_name = models.CharField(max_length=200)
    date_created = models.DateTimeField(default=Utils.get_date_time)
    course = models.CharField(max_length=200)
    submission_date = models.DateField(default=Utils.get_date_time)
    attach_info = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selectcourse = models.ForeignKey(SelectCourse, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'


class ChooseActivity(models.Model):
    activity = models.CharField(max_length=200)
    index = models.CharField(max_length=200)
    course = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.activity


class Assignment(models.Model):
    # # # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.CharField(max_length=200, primary_key=True, default=_createId)
    pdf_file = models.FileField(upload_to="activity/")
    index = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    header = models.CharField(max_length=50, choices=STATUS)
    q_number = models.IntegerField()
    activity = models.CharField(max_length=200)
    file_name = models.CharField(max_length=200)
    date_submitted = models.DateTimeField(default=Utils.get_date_time)
    date_created = models.DateTimeField(default=Utils.get_date_time)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    studentothercourse = models.ForeignKey(StudentOtherCourse, on_delete=models.CASCADE)
    # uploadedfile = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    course = models.CharField(max_length=200)
    chooseactivity = models.ForeignKey(ChooseActivity, on_delete=models.CASCADE)

    class Meta:
        # sort by "the date" in descending order unless
        # overridden in the query with order_by()
        ordering = ['-date_submitted']

    def get_absolute_url(self):
        return reverse('assignment_app:submit-assignment', kwargs={'pk': self.pk})
    

    def __str__(self):
        return f'{self.activity}'

    def encoded_id(self):
        import base64
        return base64.b64encode(str(self.user_id))

    def decode_id(self, id):
        import base64
        return base64.b64decode(id)

    @property
    def by_activity(self):
        return self.activity


TITLE = (
            ('', 'select activity'),
            ('Assignments', 'Assignments'),
            ('Exercises', 'Exercises'),
            ('Quizzes', 'Quizzes'),
            ('Trial Works', 'Trial Works')
    )

class StudentResult(models.Model):
    

    STATUS = (
            ('', 'select status'),
            ('graded', 'graded'),
            ('not graded', 'not graded'),
    )
    # # # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.CharField(max_length=200, primary_key=True, default=_createId)
    q_number = models.IntegerField()
    title = models.CharField(max_length=50, choices=TITLE)
    status = models.CharField(max_length=50, choices=STATUS)
    scored = models.FloatField("score")
    total = models.FloatField()
    course = models.CharField(max_length=200)
    marker = models.CharField(max_length=200)
    date_graded = models.DateField(default=Utils.get_date)
    date_graded1 = models.DateTimeField(default=Utils.get_date_time)    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    studentothercourse = models.ForeignKey(StudentOtherCourse, on_delete=models.CASCADE)


    class Meta:
        # sort by "the date" in descending order unless
        # overridden in the query with order_by()
        ordering = ['title']


    def __str__(self):
        return f'{self.title}'

    @property
    def get_percentage(self):
        p = (self.scored / self.total) * 100
        return p

    def get_absolute_url(self):
        return reverse('assignment_app:grade-student', kwargs={'pk': self.studentothercourse.selectcourse.id, 'index':self.studentothercourse.user.index_number})





       
# SELECT_COURSE = [(c.courses, c.courses) for c in SelectCourse.objects.all()]  

SELECT_COURSE = [('Integral Equations', 'Integral Equations'),
                ('Real Ananlysis', 'Real Analysis'),
                ('Optimization', 'Optimization')]




