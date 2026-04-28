from django.shortcuts import render, redirect
from project_one import models
from django import forms
from project_one.utils.pagination import paginate


def user_list(request):
    queryset = models.Userinfo.objects.all()
    page_data = paginate(request, queryset, page_size=10, search_fields=['name'])
    return render(request, "user/user_list.html", page_data)


def user_add(request):
    if request.method == "GET":
        content = {
            "gender_choice": models.Userinfo.gender_choice,
            "depart_list": models.Department.objects.all()
        }
        return render(request, "user/user_add.html", content)
    
    name = request.POST.get("name")
    age = request.POST.get("age")
    salary = request.POST.get("asset")
    gender = request.POST.get("gender")
    dtime = request.POST.get("dtime")
    depart = request.POST.get("depart")
    
    models.Userinfo.objects.create(name=name, age=age, gender=gender, salary=salary, create_time=dtime,
                                   depart_id=depart)
    return redirect("/user/")


def user_del(request, nid):
    models.Userinfo.objects.filter(id=nid).delete()
    return redirect("/user/")


class UserModelForm(forms.ModelForm):
    name = forms.CharField(min_length=2, label="姓名")
    
    class Meta:
        model = models.Userinfo
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}


def user_add_modelform(request):
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "user/user_modelform.html", {"form": form})
    
    form = UserModelForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("/user/")
    return render(request, "user/user_modelform.html", {"form": form})


def user_modify(request, nid):
    obj = models.Userinfo.objects.filter(id=nid).first()
    if request.method == "GET":
        form = UserModelForm(instance=obj)
        return render(request, "user/user_modelform.html", {"form": form})
    
    form = UserModelForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("/user/")
    return render(request, "user/user_modelform.html", {"form": form})