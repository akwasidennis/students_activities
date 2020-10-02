from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.http import JsonResponse
from .forms import (ImageFileUploadForm, FilesForm, StudentResultForm, 
                        StudentResultForm2, UploadedFileForm, ChooseActivityForm,
                        RegisterCourseForm, SemesterForm, SelectCourseForm, StudentOtherCourseForm)
from .models import (Profile, Assignment, StudentResult, 
        UploadedFile, RegisterCourse, Semester, StudentOtherCourse, SelectCourse, ChooseActivity)
from django.contrib.auth import get_user_model
from django.views.generic import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
import datetime
import os
import random
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import datetime as dt
from encrypted_id import ekey

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

# from users.models import SelectCourse

User = get_user_model()

@login_required
def submit_assignment(request, pk, i_n):
    
    sel = SelectCourse.objects.get(pk=pk)
    s = Semester.objects.first()
    rn = random.randint(1, 900)
    date = datetime.date.today()
    o_t = StudentOtherCourse.objects.get(pk=i_n)
    if request.method == 'POST':
        form = FilesForm(request.POST or None, request.FILES or None)
        c_form = ChooseActivityForm(request.POST or None)
        if form.is_valid() and c_form.is_valid():
            obj = c_form.save(commit=False)
            submission_date = ""
            try:
                u = UploadedFile.objects.filter(course=sel.courses).first()
                submission_date = str(u.submission_date) # will come from database
            except AttributeError:
                return HttpResponseRedirect(reverse('assignment_app:submission-denied', args=(pk,i_n,)))
            curr_date = str(date)
            pdf_file = form.cleaned_data.get('file')
            obj.activity = c_form.cleaned_data.get('activity')
            _, e = os.path.splitext(str(pdf_file))
            f, _ = str(pdf_file).split(".")
            if e in ['.pdf', 'txt']:
                if not ChooseActivity.objects.filter(activity=obj.activity).filter(course=o_t.choose_course).filter(user=o_t.user).exists():
                    c_activity = ChooseActivity.objects.create(activity=obj.activity, index=o_t.user.index_number, course=o_t.choose_course, user=o_t.user)
                q_activity = ChooseActivity.objects.filter(user=o_t.user).filter(course=o_t.choose_course).get(activity=obj.activity)
                assignment = Assignment.objects.create(pdf_file=pdf_file,
                            index=o_t.user.index_number, status='submitted', header=f, q_number=rn, activity=obj.activity, file_name=pdf_file, date_submitted=timezone.now(), date_created=timezone.now(), user=o_t.user, studentothercourse=o_t, course=sel.courses, chooseactivity=q_activity)
                print(q_activity)
                return HttpResponseRedirect(reverse('assignment_app:submit-assignment', args=(sel.pk,i_n,))) #JsonResponse({'msg': 'Success', 'fpk': sel.pk, 'spk': i_n})    #
            else:
                return JsonResponse({'error': True, 'errors': 'File type('+e+') not supported'})

    else:
        print('Not ajax')
        c_form = ChooseActivityForm()
        form = FilesForm()

    ass= Assignment.objects.filter(user=o_t.user).filter(course=o_t.choose_course).order_by('-date_created')
    
    r =  StudentResult.objects.order_by('-date_graded1').filter(course=sel.courses).filter(user=o_t.user)
    query = request.GET.get('q')
    if query:
        r =  StudentResult.objects.order_by('-date_graded1').filter(course=sel.courses).filter(user=o_t.user).filter(q_number=query)
  
    context = {
        'assignment': Assignment.objects.filter(user=o_t.user).filter(course=o_t.choose_course).order_by('-date_created'),
        'assigncount': Assignment.objects.filter(user=o_t.user).filter(course=o_t.choose_course).count(),
        'u_file': UploadedFile.objects.filter(course=sel.courses).order_by('-date_created'),
        'c_file': UploadedFile.objects.all(),
        'c_form': c_form,
        'result': r,
        's': s,
        'sel': sel,
        'o_t': o_t,
     
    }

    return render(request, 'assignment/index.html', context)


def query_results(request, pk, i_n):
    o_t = StudentOtherCourse.objects.get(id=i_n)
    # sel = SelectCourse.objects.get(pk=pk)  
    r = StudentResult.objects.filter(q_number__icontains=17)
    return HttpResponseRedirect(reverse('assignment_app:submit-assignment', args=(o_t.selectcourse.pk,i_n)))



def submission_denied(request, pk, i_n):
    context = {
        'cur_user': pk,   #User.objects.get(pk=pk)
        'i_n': i_n,
    }
    return render(request, 'assignment/submission_denied.html', context)


def results_denied(request, pk):
    context = {
        'c_pk': pk,
    }
    return render(request, 'assignment/results_denied.html', context)


def dashboard(request):

    if request.user.is_staff or request.user.is_superuser:
        print(type(request.user.pk))
        return HttpResponseRedirect(reverse('assignment_app:all-courses', args=(request.user.pk,)))
    return HttpResponseRedirect(reverse('assignment_app:student-dashboard'))

    user = User.objects.get(index_number=request.user.index_number)
    context = {
        'u': user
    }
    return render(request, 'assignment/dashboard.html', context)



@login_required
def del_assignment(request, pk, i_n):
    import os
    
    ass = Assignment.objects.get(pk=pk)
    o_t = StudentOtherCourse.objects.get(pk=i_n)
    # sel = SelectCourse.objects.get(pk=o_t.)
    date = datetime.date.today()
    submission_date = ''
    try:
        u = UploadedFile.objects.first()
        submission_date = str(u.submission_date)
    except AttributeError:
        return HttpResponseRedirect(reverse('assignment_app:submission-denied', args=(pk,)))
    curr_date = str(date)
    if curr_date <= submission_date:
        f_name = os.path.join(settings.MEDIA_ROOT, str(ass.pdf_file))
        ass.delete()
        os.remove(f_name)
        return HttpResponseRedirect(reverse('assignment_app:submit-assignment', args=(o_t.selectcourse.pk,i_n,)))
    return HttpResponseRedirect(reverse('assignment_app:submission-denied', args=(pk,)))


@login_required
def update_assignment(request, pk):
    ass = get_object_or_404(Assignment, pk=pk)
    form = FilesForm(request.POST or None,
                    request.FILES or None)
    return HttpResponseRedirect(reverse('assignment_app:submit-assignment'))


@login_required
def viewAssignmentPDF(request, pk):
    import os
    from django.conf import settings
    get_file = Assignment.objects.get(pk=pk)
    f_name = os.path.join(settings.MEDIA_ROOT, str(get_file.pdf_file))
    file_name, file_ext = os.path.splitext(f_name)
    if file_ext in ['.pdf', '.txt', '.py']:
        pdf = open(f_name, 'rb').read()
        return HttpResponse(pdf, content_type='application/'+file_ext[1:])


def django_image_and_file_upload_ajax(request):
    if request.method == 'POST':
       form = ImageFileUploadForm(request.POST, request.FILES)
       if form.is_valid():
           form.save()
           
           return JsonResponse({'error': False, 'message': 'Uploaded Successfully'})
       else:
           return JsonResponse({'error': True, 'errors': form.errors})
    else:
        form = ImageFileUploadForm()
        return render(request, 'assignment/upload.html', {'form': form})



def show_files(request):
    obj = Profile.objects.all()
    return render(request, 'assignment/show_files.html', {'object': obj})


@login_required
@staff_member_required
def student_result(request, pk, a_pk, model_class=StudentResult, form_class=StudentResultForm):
    # user = User.objects.get(pk=pk)
    o_c1 = StudentOtherCourse.objects.get(pk=pk)

    ass = Assignment.objects.get(pk=a_pk)
    print(ass.date_submitted-ass.date_created)
    # sel = SelectCourse.objects.get(pk=pk)
    o_c = StudentOtherCourse.objects.filter(user=o_c1.user).filter(choose_course=o_c1.choose_course)
    # sel = SelectCourse.objects.filter(courses=user.course).first()

    # try:
    #     # u = User.objects.get(pk=pk)
    #     a = Assignment.objects.filter(index=o_c1.user.index_number).first()
    # except ObjectDoesNotExist:
    #     print('does not exist')
    #     # return HttpResponseRedirect(reverse('assignment_app:score-student-section', args=(pk,)))
    if request.method == 'POST':
        form = StudentResultForm(o_c1, ass, request.user, request.POST)
        if form.is_valid:
            obj = form.save(commit=False)
            # obj.title = form.cleaned_data.get('title')
            obj.scored = form.cleaned_data.get('scored')
            obj.total = form.cleaned_data.get('total')
            obj.marker = form.cleaned_data.get('marker')
            res = StudentResult.objects.create(q_number=ass.q_number, title=ass.activity, status='graded', scored=obj.scored,
                 total=obj.total, course=o_c1.choose_course, marker=obj.marker, date_graded=timezone.now(), date_graded1=timezone.now(),
                 user=o_c1.user, assignment=ass, studentothercourse=o_c1)


            # form.instance.user = o_c1.user
            # form.instance.studentothercourse = o_c1
            # form.instance.assignment = ass
            # update status in assignment
            # obj.status = form.cleaned_data.get('status')
            # obj.q_number = form.cleaned_data.get('q_number')
            # assign = Assignment.objects.filter(user=o_c1.user).filter(course=o_c1.choose_course)
            # q_num_list = [a1.q_number for a1 in assign]
            # a2 = Assignment.objects.filter(q_number=obj.q_number).first()
            # if obj.course != o_c1.choose_course:  #   :
            #     return HttpResponseRedirect(reverse('assignment_app:results-denied', args=(pk, a_pk,)))
            
            a = Assignment.objects.filter(index=ass.index).filter(q_number=ass.q_number).update(status='graded')
            
            # form.save()
            return HttpResponseRedirect(reverse('assignment_app:grade-student', args=(o_c1.selectcourse.pk, o_c1.user.index_number,)))
    else:
        form = StudentResultForm(o_c1, ass, request.user)

    

    s_a = Assignment.objects.order_by('-date_created').filter(course=o_c1.choose_course).filter(user=o_c1.user)
    context = {
        'form': form,
        'ass': s_a,
        'u': o_c1.user,
        'sel': o_c,
        'o_c1': o_c1,
    }
    return render(request, 'assignment/studentresult_update_form.html', context)


@login_required
@staff_member_required
def all_students(request, pk):
    all_staff = User.objects.filter(is_staff=True)
    list_all_staff = [s.index_number for s in all_staff]
    user = User.objects.exclude(index_number__in=list_all_staff)
    sel = SelectCourse.objects.get(pk=pk)
    a = Assignment.objects.filter(course=sel.courses)
    
    o_c = StudentOtherCourse.objects.exclude(user__in=list_all_staff).filter(choose_course=sel.courses) #exclude(user__in=all_staff).
    ie_users = User.objects.exclude(index_number__in=list_all_staff).filter(course=sel.courses)  # #filter(course=s_c.courses)
    query = request.GET.get('q')
    if query:
        o_c = StudentOtherCourse.objects.exclude(user__in=list_all_staff).filter(choose_course=sel.courses).filter(user__index_number=query) #exclude(user__in=all_staff).
    if request.method == 'POST':
        form = UploadedFileForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            file = form.cleaned_data.get('pdf_file')
            print(file)
            date_to_subm = form.cleaned_data.get('submission_date')
            info = form.cleaned_data.get('attach_info')
            date = datetime.date.today()
            # if UploadedFile.objects.count() > 0:
            #     u = UploadedFile.objects.first()
            #     u.pdf_file = file
            #     u.date_created = date
            #     u.submission_date = date_to_subm
            #     u.save()
            #     return HttpResponseRedirect(reverse('assignment_app:all-students', args=(pk,)))
            # else:
            f = UploadedFile.objects.create(pdf_file=file, file_name=file, date_created=timezone.now(), course=sel.courses, submission_date=date_to_subm, attach_info=info, user=request.user, selectcourse=sel)

            return HttpResponseRedirect(reverse('assignment_app:all-students', args=(pk,)))
    else:
        form = UploadedFileForm()


    context = {
        'form': form,
        'all_students': user,
        # 'ra_users': ra_users,
        'ie_users': ie_users,
        'semester': Semester.objects.first(),
        'a': a,
        'sel': sel,
        'o_c': o_c,
        'pk': pk,
        'u_file': UploadedFile.objects.order_by('-date_created').filter(course=sel.courses),
    }
    return render(request, 'assignment/all_students.html', context)



def del_upload_file(request, pk):
    u = UploadedFile.objects.get(pk=pk)
    u.delete()
    return HttpResponseRedirect(reverse('assignment_app:all-students', args=(u.selectcourse.pk,)))



def download_pdf(request, pk):
    import os
    from django.conf import settings
    get_file = UploadedFile.objects.filter(pk=pk).first()
    f_name = os.path.join(settings.MEDIA_ROOT, str(get_file.pdf_file))
    file_name, file_ext = os.path.splitext(f_name)
    if file_ext in ['.pdf', '.txt', '.py']:
        pdf = open(f_name, 'rb').read()
        return HttpResponse(pdf, content_type='application/'+file_ext[1:])


class GradeUpdateView(UpdateView):
    model = StudentResult
    fields = ['scored', 'total', 'marker']

    template_name_suffix = '_update_form'
    def form_valid(self, form, *args, **kwargs):
        print(self.kwargs['s'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False


def main_dashboard(request, pk):
    cur_user = User.objects.get(pk=pk)
    context = {
        'cur_user': cur_user,
    }
    return render(request, 'assignment/main_dashboard.html', context)


def register_course(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        form = RegisterCourseForm(request.POST)
        if form.is_valid():
            form.instance.user = user
            form.save()
            return HttpResponseRedirect(reverse('assignment_app:all-students'))
    else:
        form = RegisterCourseForm(instance=user)
    context = {
        'form': form,
    }
    return render(request, 'assignment/assignment_update_form.html', context)


@staff_member_required
def update_submitted(request, pk):
    a1 = Assignment.objects.get(pk=pk)
    a = Assignment.objects.filter(index=a1).update(status='graded')
    return HttpResponseRedirect(reverse('assignment_app:score-student-section', args=(pk,)))


class StatusUpdateView(UpdateView):
    model = Assignment
    fields = ['status']

    template_name_suffix = '_update_form'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False


class CourseUpdateView(UpdateView):
    model = SelectCourse
    fields = ['courses']

    template_name_suffix = '_update_form'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False

    
def update_courses(request, pk):
    s = SelectCourse.objects.get(pk=pk)
    sem = Semester.objects.first()
    std = StudentOtherCourse.objects.filter(choose_course=s.courses)
    
    c_form = SelectCourseForm(request.POST or None, instance=s)
    if c_form.is_valid():
        c_form['courses'].required = False
        obj = c_form.cleaned_data.get('courses')
        obj1 = c_form.cleaned_data.get('choose_back_color')
        a = SelectCourse.objects.filter(pk=pk).update(courses=obj)
        a1 = SelectCourse.objects.filter(pk=pk).update(choose_back_color=obj1)
        for st in std:
            st.choose_course = obj
            st.save()
        return HttpResponseRedirect(reverse('assignment_app:all-courses', args=(pk,)))
    context = {
        'c_form': c_form,
        's': s,
    }
    return render(request, 'assignment/selectcourse_update_form.html', context)


def all_courses(request, pk):
    s = SelectCourse.objects.order_by('-date_created').all()
    # change background color

    # create course
    if request.method == 'POST':
        c_form = SelectCourseForm(request.POST)
        if c_form.is_valid():
            semester = Semester.objects.first()
            c_form.instance.semester = semester
            c_form.instance.user = request.user
            obj = c_form.save(commit=False)
            obj.courses = c_form.cleaned_data.get('courses')
            obj.choose_back_color = c_form.cleaned_data.get('choose_back_color')
            SelectCourse.objects.create(courses=obj.courses, choose_back_color=obj.choose_back_color, 
            sem=semester.sem, user=request.user, semester=semester)
                
            return HttpResponseRedirect(reverse('assignment_app:all-courses', args=(pk,)))
    else:
        c_form = SelectCourseForm()

    #  set semester
    if request.method == 'POST':
        s_form = SemesterForm(request.POST)
        if s_form.is_valid():
            obj = s_form.save(commit=False)
            obj.sem = s_form.cleaned_data.get('sem')
            if Semester.objects.count() == 0:
                s_form.save()
            else:
                s = Semester.objects.first()
                s.sem = obj.sem
                s.save()
            return HttpResponseRedirect(reverse('assignment_app:all-courses', args=(pk,)))
    else:
        
        s_form = SemesterForm()

    context = {
        'sel': s,
        # 'o_c': o_c,
        # 'o_c1': o_c1,
        's_form': s_form,
        'c_form': c_form,
        'semester': Semester.objects.first(), 
        'sem': Semester.objects.all(),   
        }
    return render(request, 'assignment/all_courses.html', context)



def del_course(request, pk):
    # print(pk)
    # u = User.objects.get(pk=request.user.pk)
    # s = StudentOtherCourse.objects.filter(pk=pk)
    s = SelectCourse.objects.get(pk=pk)
    s.delete()
    return HttpResponseRedirect(reverse('assignment_app:all-courses', args=(s.user.pk,)))

def student_dashboard(request, model_class=StudentOtherCourse, form_class=StudentOtherCourseForm):
    user = User.objects.get(pk=request.user.pk)
    s = Semester.objects.first()
    if request.method == 'POST':
        o_form = StudentOtherCourseForm(request.user, request.POST)
        if o_form.is_valid():
            fm = o_form.save(commit=False)
            fm.choose_course = o_form.cleaned_data.get('choose_course')
            s = SelectCourse.objects.get(courses=fm.choose_course)
            o_form.instance.selectcourse = s
            o_form.instance.user = request.user
            o_form.save()
            return HttpResponseRedirect(reverse('assignment_app:student-dashboard'))
    else:
        o_form = StudentOtherCourseForm(request.user)

    o_course = StudentOtherCourse.objects.filter(user=request.user)
    
    context = {
        'o_form': o_form,
        'o_course': o_course,
        's': s,
    }
    return render(request, 'assignment/student_dashboard.html', context)

def del_choose_course(request, pk):
    o = StudentOtherCourse.objects.get(pk=pk)
    o.delete()
    return HttpResponseRedirect(reverse('assignment_app:student-dashboard'))


def student_results_list(request, c, pk):
    # o_c1 = StudentOtherCourse.objects.get(pk=pk)

    o_c1 = SelectCourse.objects.get(pk=pk)
    all_staff = User.objects.filter(is_staff=True)
    list_all_staff = [s.index_number for s in all_staff]
    user = User.objects.exclude(index_number__in=list_all_staff)
    st = StudentOtherCourse.objects.filter(choose_course=c)
    query = request.GET.get('q')
    if query:
        st = StudentOtherCourse.objects.filter(choose_course=c).filter(user__index_number=query)
    context = {
        'result': StudentResult.objects.filter(course=c),
        'users': user,
        'st': st,
        'c': c,
        'o_c1': o_c1,
    }
    return render(request, 'assignment/std_results_list.html', context )



def grade_student(request, pk, index):
    
    sel = SelectCourse.objects.get(pk=pk)
    u = User.objects.get(index_number=index)
    context = {
        'uploads': UploadedFile.objects.all(),
        'ass': Assignment.objects.filter(course=sel.courses).filter(index=index),
        'c_act': ChooseActivity.objects.order_by('activity').filter(course=sel.courses).filter(index=index).filter(user=u),
        'sel': sel,
        
    }
    return render(request, 'assignment/grade_student.html', context )



# ----------------PDF-------------------------------------

def create_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer) 
    p.drawString(100, 100, str(request.user))
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="firstpdf.pdf")


def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None


datas = {
    'result': StudentResult.objects.all(),
	}

#Opens up page as PDF
class ViewPDF(View):
	def get(self, request, *args, **kwargs):
        
        # st = StudentOtherCourse.objects.filter(choose_course=c)
		pdf = render_to_pdf('assignment/pdf_template.html', {'st':StudentOtherCourse.objects.filter(choose_course=self.kwargs['c']),
        'semester': Semester.objects.first(), 'c':self.kwargs['c']})
		return HttpResponse(pdf, content_type='application/pdf')


#Automatically downloads to PDF file
class DownloadPDF(View):
	def get(self, request, *args, **kwargs):
		pdf = render_to_pdf('assignment/pdf_template.html', {'st':StudentOtherCourse.objects.filter(choose_course=self.kwargs['c']), 'sts':StudentOtherCourse.objects.filter(choose_course=self.kwargs['c']).first(),
         'semester': Semester.objects.first(), 'c':self.kwargs['c'], 'cur_date': timezone.now()})
		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "students_results_%s.pdf" %(self.kwargs['c'].replace(' ', '_'))
		content = "attachment; filename='%s'" %(filename)
		response['Content-Disposition'] = content
		return response



# --------------------------------------------------
