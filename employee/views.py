from django.contrib import messages
from django.core import serializers
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from employee.forms import EmployeeForm
from employee.models import Employee
from datetime import datetime
import redis

redis_host = "localhost"
redis_port = 6379
redis_password = ""


def add(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('/show')
            except:
                pass
    else:
        form = EmployeeForm()
    return render(request, 'index.html', {'form': form})


def show(request):
    search_box_text = request.GET.get('searchbox', '')

    employees = Employee.objects.filter(Q(ename__icontains=search_box_text))

    paginator = Paginator(employees, 3)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
    timestamp_retrieval_from_redis = r.get("timestamp")

    print(timestamp_retrieval_from_redis)

    if employees:
        return render(request, 'show.html',
                      {'page_obj': page_obj, 'searchbox': search_box_text, 'timestamp': timestamp_retrieval_from_redis})
    else:
        messages.error(request, 'No Result Found...')


def edit(request, id):
    employee = Employee.objects.get(id=id)
    return render(request, 'edit.html', {'employee': employee})


def update(request, id):
    employee = Employee.objects.get(id=id)
    form = EmployeeForm(request.POST, instance=employee)
    if form.is_valid():
        form.save()

        timestamp = str(datetime.now())

        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)
        r.set("timestamp", timestamp)

        print("Python : " + timestamp)

        return redirect("/show")
    return render(request, 'edit.html', {'employee': employee})


def destroy(request, id):
    employee = Employee.objects.get(id=id)
    employee.delete()
    return redirect("/show")


def employee(request):
    empl_name = request.GET.get('name', None)
    if empl_name is not None:
        fields = ['ename', 'eemail', 'econtact']
        fetching_employee = Employee.objects.filter(ename=empl_name).values(*fields)
        emp_list = list(fetching_employee)
    return JsonResponse({'status': 'success', 'data': emp_list}, safe=False)


def allemployee(request):
    fields = ['ename', 'eemail', 'econtact']

    all_users = Employee.objects.all().values(*fields)
    user_list = list(all_users)
    return JsonResponse({'status': 'success', 'data': user_list}, safe=False)
