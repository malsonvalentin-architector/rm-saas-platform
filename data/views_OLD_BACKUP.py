
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from .owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.http import JsonResponse
from django.views import View
from .forms import CreateUserForm, CreateObjForm, CreateSystemForm, CreateAtribForm, CreateDataForm, WriteDataForm
from .models import User_profile, Obj, System, Atributes, Data
from .utils.carel_req import get_carel_one_value, get_carel_all_values_json, set_carel_value
import json
from django.http import JsonResponse
# from view_breadcrumbs import UpdateBreadcrumbMixin

# Create your views here.
class UserListView(OwnerListView):
    model=User_profile
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        objects=Obj.objects.filter(user=self.request.user)
        context["objects"] = objects
        print ('objects', objects)
        return context

class UserDetailView(OwnerDetailView):
    model=User_profile
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        objects=Obj.objects.filter(user=self.kwargs['pk']).all()
        context["objects"] = objects
        print ('objects', objects)
        return context
        
class UserCreateView(CreateView):
    model=User_profile
    form_class= CreateUserForm
    def get_success_url(self):
        return reverse_lazy('obj_create', kwargs={'user_pk': self.object.pk})
    
class UserDeleteView(OwnerDeleteView):
    model=User_profile
    success_url=reverse_lazy('user_list')

class UserUpdateView(OwnerUpdateView):
    model=User_profile
    form_class=CreateUserForm
    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk':self.object.pk})

class ObjListView (ListView):
    model=Obj

class ObjCreateView(OwnerCreateView):
    model = Obj
    form_class= CreateObjForm

    def dispatch(self, request, *args, **kwargs):
        self.user=get_object_or_404(User_profile, pk=self.kwargs['user_pk'])
        print (self.user.id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self,form):
        form.instance.user=self.user
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = get_object_or_404(User_profile, pk=self.kwargs['user_pk'])
        print('initial', initial)
        return initial
    
    def get_success_url(self):
        return reverse_lazy('data:sys_create', kwargs={'obj_pk':self.object.pk, 'user_pk':self.kwargs['user_pk']})

class ObjDetailView(OwnerDetailView):
    model=Obj
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["systems"] = self.object.system_set.all()
        return context 

    
class ObjDeleteView(DeleteView):
    model=Obj
    success_url=reverse_lazy('data:user_list')

class ObjUpdateView(UpdateView):
    model=Obj
    form_class=CreateObjForm
    def get_success_url(self):
        return reverse_lazy('data:user_detail', kwargs={'user_pk':self.kwargs['user_pk']})
    
    
class SystemCreateView(CreateView):
    model=System
    form_class=CreateSystemForm
    def get_initial(self):
        initial = super().get_initial()
        initial['obj'] = get_object_or_404(Obj, pk=self.kwargs['obj_pk'])
        print('initial', initial)
        return initial
    
    def get_success_url(self):
        return reverse_lazy('data:atr_create', kwargs={'sys_pk':self.object.pk,'obj_pk':self.kwargs['obj_pk'], 'user_pk':self.kwargs['user_pk']})
    
class SystemDetailView(OwnerDetailView):
    model=System
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['objects']=Obj.objects.filter(pk=self.kwargs['obj_pk'])
        return context

class SystemUpdateView(UpdateView):
    model=System
    form_class=CreateSystemForm
    
    def get_success_url(self):
        return reverse_lazy('data:sys_detail', kwargs={'pk':self.object.pk, 'obj_pk':self.kwargs['obj_pk'], 'user_pk':self.kwargs['user_pk']})
    
class SystemDeleteView(DeleteView):
    model=System
    success_url=reverse_lazy('data:user_list')
    
    # def get_success_url(self):
    #     return reverse_lazy('sys_create', kwargs={'pk':self.object.pk, 'obj_pk':self.kwargs['obj_pk'], 'user_pk':self.kwargs['user_pk']})


class AtribCreateView(CreateView):
    model = Atributes
    form_class=CreateAtribForm

    def get_initial(self):
        initial = super().get_initial()
        initial['sys'] = get_object_or_404(System, pk=self.kwargs['sys_pk'])
        return initial
    
    def get_success_url(self):
        return reverse_lazy('data:sys_detail', kwargs={'user_pk':self.kwargs['user_pk'],'obj_pk':self.kwargs['obj_pk'], 'pk':self.kwargs['sys_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['systems'] = get_object_or_404 (System, pk=self.kwargs['sys_pk'])
        return context
    
class AtributeDetailView(DetailView):
    model = Atributes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print (self.object.sys.ipaddr, self.object.carel_reg)
        if self.object.write==True:
            context['form'] = WriteDataForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = WriteDataForm(request.POST)
        if form.is_valid():
            set_carel_value(self.object.sys.ipaddr, self.object.carel_reg, form.cleaned_data['value'])
            return redirect(self.request.path)  # обновляем страницу
        else:
            print('Form is not valid:', form.errors)
            # Если форма не валидна, возвращаем на ту же страницу с ошибками
        context = self.get_context_data()
        context['form'] = form  # вернуть с ошибками
        return self.render_to_response(context)

class AtributeListView(ListView):
    model = Atributes
    template_name = 'data/atribute_list.html'


class AtribUpdateView(UpdateView):
    model = Atributes
    form_class=CreateAtribForm

    def get_success_url(self):
        return reverse_lazy('data:atr_detail', kwargs={'pk':self.object.pk, 'sys_pk':self.kwargs['sys_pk'], 'obj_pk':self.kwargs['obj_pk'], 'user_pk':self.kwargs['user_pk']})

class AtibuteDeleteView(DeleteView):
    model = Atributes
    success_url=reverse_lazy('data:atr_create')
    
    def get_success_url(self):
        return reverse_lazy('data:sys_detail', kwargs={'pk':self.kwargs['sys_pk'],'obj_pk':self.kwargs['obj_pk'], 'user_pk':self.kwargs['user_pk']})    

class CreateDataView(CreateView):
    model = Data
    form_class = CreateDataForm

    def get_initial(self):
        initial= super().get_initial()
        sys_atrib=get_object_or_404(Atributes, pk=self.kwargs['atr_pk'])
        values=get_carel_one_value(sys_atrib.sys.ipaddr, sys_atrib.carel_reg)
        initial['value'] = values
        # Устанавливаем значение по умолчанию для поля, если related_pk передан 
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передаем pk связанного объекта в форму
        kwargs['atr_pk'] = self.kwargs.get('atr_pk')  # 'atr_pk' из URL
        return kwargs

    def get_success_url(self):
        return reverse_lazy('atr_detail', kwargs={'pk':self.kwargs['atr_pk'], 'sys_pk':self.kwargs['sys_pk'], 'obj_pk':self.kwargs['obj_pk'], 'user_pk':self.kwargs['user_pk']})
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Ошибка валидации формы'})
        # Получаем объект Atributes по atr_pk
        if form.is_valid():
            self.object=form.save(commit=False)
            self.object.save()
        return JsonResponse({'status': 'success', 'message': 'Объект создан!', 'data_id': self.object.id})

def data_plot_view(request, *args, **kwargs):
    path_kwargs = request.resolver_match.kwargs
    sys_pk = path_kwargs.get('sys_pk')
    obj_pk = path_kwargs.get('obj_pk')
    user_pk = path_kwargs.get('user_pk')

    if sys_pk or obj_pk or user_pk:
        print('data_plot_view: фильтрация по фильтрам', sys_pk, obj_pk, user_pk)
        data_qs = Data.objects.all()
        if sys_pk:
            data_qs = data_qs.filter(name__sys__pk=sys_pk)
        if obj_pk:
            data_qs = data_qs.filter(name__sys__obj__pk=obj_pk)
        if user_pk:
            data_qs = data_qs.filter(name__sys__obj__user__pk=user_pk)
        data_qs = data_qs.order_by('-date')[:1000][::-1]
    else:
        print('data_plot_view: фильтры не заданы, ничего не показываем')
        data_qs = Data.objects.none()
    series = {}
    for d in data_qs:
        name = str(d.name)
        if name not in series:
            series[name] = {'dates': [], 'values': []}
        if d.date:
            series[name]['dates'].append(d.date.strftime('%Y-%m-%d %H:%M:%S'))
            series[name]['values'].append(d.value)
    start = request.GET.get('start')
    end = request.GET.get('end')
    unit = request.GET.get('unit', 'hour')
    print('start', start, 'end', end, 'unit', unit)
    series_json = json.dumps(series)
    return render(request, 'data/data_plot_user.html', {
        'series': series_json,
        'sys_pk': sys_pk,
        'obj_pk': obj_pk,
        'user_pk': user_pk,
    })


def data_plot_json(request, *args, **kwargs):
    # Получаем параметры фильтрации из GET или path_kwargs
    path_kwargs = request.resolver_match.kwargs if hasattr(request, 'resolver_match') and request.resolver_match else {}
    sys_pk = path_kwargs.get('sys_pk')
    user_pk = path_kwargs.get('user_pk')
    obj_pk = path_kwargs.get('obj_pk')
    series = {}
    # Базовый queryset
    if sys_pk or obj_pk or user_pk:
        data_qs = Data.objects.all()
        if sys_pk:
            data_qs = data_qs.filter(name__sys__pk=sys_pk)
        if obj_pk:
            data_qs = data_qs.filter(name__sys__obj__pk=obj_pk)
        if user_pk:
            data_qs = data_qs.filter(name__sys__obj__user__pk=user_pk)
        data_qs = data_qs.order_by('-date')[:1000][::-1]
    else:
        data_qs = Data.objects.all().order_by('-date')[:2000][::-1]
    for d in data_qs:
        name = str(d.name)
        if name not in series:
            series[name] = {'dates': [], 'values': []}
        series[name]['dates'].append(d.date.strftime('%Y-%m-%d %H:%M:%S'))
        series[name]['values'].append(d.value)
    return JsonResponse(series)

def get_all_carel_vars(request, *args, **kwargs):
    path_kwargs = request.resolver_match.kwargs

    if request.method == 'GET':
        sys_pk = path_kwargs.get('sys_pk')
        # if not sys_pk:
        #     return JsonResponse({'error': 'sys_pk (ID системы) обязателен'}, status=400)
        # try:
        system = System.objects.get(pk=sys_pk)
        # except System.DoesNotExist:
        #     return JsonResponse({'error': 'Система не найдена'}, status=404)
        try:
            data = get_carel_all_values_json(system.ipaddr)
            print ('get all values from IP',system.ipaddr, (data['vars'][0].keys()))
            l=[]
            # for i in data['vars']:
            #     l.append(i['name'], i['desc'])
            #     print (l)
            return JsonResponse({'data':  data['vars']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=405)