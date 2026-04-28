from django.shortcuts import render, redirect
from django import forms
from project_one import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from project_one.utils.pagination import paginate
import openpyxl
import os


def asset_list(request):
    queryset = models.Assets.objects.all()
    page_data = paginate(request, queryset, page_size=10, search_fields=['mobile'])
    return render(request, 'asset/asset_list.html', page_data)


class AssetForm(forms.ModelForm):
    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r"^1[3-9]\d{9}", "请输入正确格式的手机号")]
    )

    class Meta:
        model = models.Assets
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}

    def clean_mobile(self):
        new_mobile = self.cleaned_data['mobile']
        exists = models.Assets.objects.filter(mobile=new_mobile).exists()
        if exists:
            raise ValidationError("手机号已经存在")
        return new_mobile


def asset_add(request):
    if request.method == 'GET':
        title = "添加资产"
        form = AssetForm()
        return render(request, 'asset/asset_modify.html', {'form': form, "title": title})
    
    form = AssetForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/asset/")
    return render(request, 'asset/asset_modify.html', {'form': form})


class AssetModify(forms.ModelForm):
    price = forms.CharField(disabled=True, label="价格")

    class Meta:
        model = models.Assets
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}

    def clean_mobile(self):
        new_mobile = self.cleaned_data['mobile']
        exists = models.Assets.objects.exclude(id=self.instance.pk).filter(mobile=new_mobile).exists()
        if exists:
            raise ValidationError("手机号已经存在")
        return new_mobile


def asset_modify(request, nid):
    title = "修改数据"
    data_list = models.Assets.objects.filter(id=nid).first()
    
    if request.method == 'GET':
        form = AssetModify(instance=data_list)
        content = {"title": title, "form": form}
        return render(request, 'asset/asset_modify.html', content)
    
    form = AssetModify(data=request.POST, instance=data_list)
    if form.is_valid():
        form.save()
        return redirect("/asset/")
    return render(request, 'asset/asset_modify.html', {'form': form, "title": title})


class AssetImportForm(forms.Form):
    file = forms.FileField(
        label="Excel文件",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )


def asset_import(request):
    if request.method == 'GET':
        form = AssetImportForm()
        return render(request, 'asset/asset_import.html', {'form': form})
    
    form = AssetImportForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        ext = os.path.splitext(file.name)[1].lower()
        
        if ext not in ['.xlsx', '.xls']:
            form.add_error('file', '请上传.xlsx或.xls格式的Excel文件')
            return render(request, 'asset/asset_import.html', {'form': form})
        
        try:
            wb = openpyxl.load_workbook(file)
            ws = wb.active
            
            for row in ws.iter_rows(min_row=1, values_only=True):
                if not row or not row[0]:
                    continue
                
                mobile = str(row[0]) if row[0] else ''
                status = int(row[1]) if row[1] else 2
                times = str(row[2]) if row[2] else ''
                price = str(row[3]) if row[3] else ''
                user_id = int(row[4]) if row[4] else None
                
                if mobile:
                    exists = models.Assets.objects.filter(mobile=mobile).exists()
                    if not exists:
                        if user_id:
                            user_exists = models.Userinfo.objects.filter(id=user_id).exists()
                            if not user_exists:
                                user_id = None
                        
                        asset = models.Assets(
                            mobile=mobile,
                            status=status,
                            times=times,
                            price=price,
                            user_id=user_id
                        )
                        asset.save()
            
            return redirect("/asset/")
            
        except Exception as e:
            form.add_error('file', f'导入失败：{str(e)}')
            return render(request, 'asset/asset_import.html', {'form': form})
    
    return render(request, 'asset/asset_import.html', {'form': form})