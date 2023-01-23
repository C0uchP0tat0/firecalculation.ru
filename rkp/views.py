from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404, render
from .models import FireLoad, FireObject, Quantity
from .forms import FireObjectForm, QuantityForm, UserForm, FireloadCreateForm
from django.contrib import messages
from django.shortcuts import redirect
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.forms import modelformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .serializers import FireObjectSerializer


"""
РАБОТА С ОБЪЕКТАМИ, РАСЧЁТ КАТЕГОРИЙ ПРОИЗВОДСТВ
"""


def get_user(request):

    user = request.user
    return user


def index(request):

    user = get_user(request=request)
    try:
        fireobjec = FireObject.objects.filter(user=user).order_by('-id')
    except TypeError:
        fireobjec = FireObject.objects.filter(user=1).order_by('-id')
    quantity = Quantity.objects.all()
    return render(request, 'index.html', {
                                        "fireobjec": fireobjec,
                                        'quantity': quantity,
                                        'user': user,
                                        })


@login_required(login_url='/login/')
def update(request, pk):

    try:
        fire_object = get_object_or_404(FireObject, pk=pk)
        obj = Quantity.objects.filter(fire_object=fire_object)
        initial = [
            {'fire_object': fire_object},
            {'fire_object': fire_object},
            {'fire_object': fire_object},
            {'fire_object': fire_object},
            {'fire_object': fire_object}
            ]
    except:
        return redirect("/")
    QuantityFormSet = modelformset_factory(
        Quantity,
        form=QuantityForm,
        fields=['fire_load', 'weight', 'fire_object'],
        extra=0,
    )

    if request.method == "POST":
        objectform = FireObjectForm(request.POST, instance=fire_object)
        quantityform = QuantityFormSet(request.POST,
                                       initial=initial,
                                       form_kwargs={'user': request.user})
        if objectform.is_valid() and quantityform.is_valid():
            objectform.save()
            quantityform.save()
            messages.success(request, ('Данные успешно обновлены!'))
            return redirect("/")
        else:
            messages.error(request, 'Error saving form')
    else:
        objectform = FireObjectForm(instance=fire_object)
        quantityform = QuantityFormSet(
            queryset=obj,
            initial=initial,
            form_kwargs={'user': request.user})
        quantityform.extra += len(initial)
        return render(request, 'update.html', {
            'objectform': objectform,
            'quantityform': quantityform,
            })


@login_required(login_url='/login/')
def delete(request, pk):

    try:
        fire_object = get_object_or_404(FireObject, pk=pk)
        fire_object.delete()
        return redirect("/")
    except FireObject.DoesNotExist:
        messages.error(request, 'FireObjec not found')


@login_required(login_url='/login/')
def object_create(request):

    if request.method == "POST":
        objectform = FireObjectForm(request.POST)
        if objectform.is_valid():
            objectform.save()
            messages.success(request, ('Объект был успешно добавлен!'))
            obj = FireObject.objects.filter(
                title=objectform.cleaned_data['title'],
                length=objectform.cleaned_data['length'],
                width=objectform.cleaned_data['width'],
                height=objectform.cleaned_data['height'],
                user=request.user, ).order_by('-id')[0]
            return redirect("rkp:fireload_add", pk=obj.id)
        else:
            messages.error(request, 'Error saving form')
    else:
        initial = {'user': request.user}
        objectform = FireObjectForm(initial=initial)

    return render(request, 'object_create.html', {
        'objectform': objectform,
        })


@receiver(post_save, sender=FireObject)
def get_id(sender, instance, **kwargs):
    return instance


@login_required(login_url='/login/')
def fireload_add(request, pk):

    obj = FireObject.objects.get(id=pk)

    QuantityFormSet = modelformset_factory(
        Quantity,
        form=QuantityForm,
        fields=['fire_load', 'weight', 'fire_object'],
        extra=0,
    )
    if request.method == "POST":
        quantityform = QuantityFormSet(
            request.POST,
            form_kwargs={'user': request.user})

        if quantityform.is_valid():
            quantityform.save()
            messages.success(
                request,
                ('Пожарная нагрузка была успешно добавлена!'))
            return redirect("/")

        else:
            messages.error(request, 'Error saving form')
    else:
        try:
            initial = [
                {'fire_object': obj},
                {'fire_object': obj},
                {'fire_object': obj},
                {'fire_object': obj}
                ]
            quantityform = QuantityFormSet(queryset=Quantity.objects.filter(
                fire_object=obj),
                                           initial=initial,
                                           form_kwargs={'user': request.user})
            quantityform.extra += len(initial)
        except:
            return redirect("/")
            # quantityform = QuantityFormSet()
    return render(request, 'fireload.html', {
        'quantityform': quantityform,
        })


"""
РЕГИСТРАЦИЯ, АУТЕНТИФИКАЦИЯ
"""


def login_view(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, 'Вы успешно вошли в свой профиль!')
            return redirect("/")
        else:
            redirect("/login/")
            userform = UserForm()
            return render(request, 'login.html', {'alert_flag': True,
                                                  "form": userform})
    else:
        userform = UserForm()
        return render(request, "login.html", {"form": userform})


def logout_view(request):

    logout(request)
    return redirect("/")


"""
РАБОТА С ОБЪЕКТАМИ ПОЖАРНОЙ НАГРУЗКИ
"""


@login_required(login_url='/login/')
def fire_load_list(request):

    user = get_user(request=request)
    fireload = FireLoad.objects.filter(user=user)
    return render(request, 'fire_load_list.html', {
                                        "fireload": fireload,
                                        })


@login_required(login_url='/login/')
def fire_load_create(request):

    if request.method == "POST":
        fireloadcreateform = FireloadCreateForm(request.POST)
        if fireloadcreateform.is_valid():
            fireloadcreateform.save()
            messages.success(request, ('Объект был успешно добавлен!'))
            return redirect("rkp:fire_load_list")
        else:
            messages.error(request, 'Error saving form')
    else:
        initial = {'user': request.user}
        fireloadcreateform = FireloadCreateForm(initial=initial)

    return render(request, 'fire_load_create.html', {
        'fireloadcreateform': fireloadcreateform,
        })


@login_required(login_url='/login/')
def fire_load_update(request, pk):
    try:
        fire_load = get_object_or_404(FireLoad, pk=pk)
    except:
        return redirect("rkp:fire_load_list")
    if request.method == "POST":
        fireloadcreateform = FireloadCreateForm(
            request.POST,
            instance=fire_load)
        if fireloadcreateform.is_valid():
            fireloadcreateform.save()
            messages.success(request, ('Объект был успешно изменён!'))
            return redirect("rkp:fire_load_list")
        else:
            messages.error(request, 'Error saving form')
    else:
        initial = {'user': request.user}
        fireloadcreateform = FireloadCreateForm(
            instance=fire_load,
            initial=initial)

    return render(request, 'fire_load_update.html', {
        'fireloadcreateform': fireloadcreateform,
        })


@login_required(login_url='/login/')
def fire_load_delete(request, pk):
    try:
        fire_load = get_object_or_404(FireLoad, pk=pk)
        fire_load.delete()
        return redirect("rkp:fire_load_list")
    except FireObject.DoesNotExist:
        messages.error(request, 'FireLoad not found')


class FireObjectView(ModelViewSet):
    queryset = FireObject.objects.all()
    serializer_class = FireObjectSerializer
