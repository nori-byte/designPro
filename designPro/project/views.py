from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .forms import RegistrationForm, CustomAuthenticationForm


def index(request):
    requests = DesignRequest.objects.filter(status='complete')[:4]
    num_added = DesignRequest.objects.filter(status__exact='in-progress').count()
    context = {'requests': requests,
               'num_added': num_added
               }
    return render(request, 'index.html', context)



# Вход
class UserLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('profile')


# Регистрация
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


# Профиль пользователя
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_info'] = {
            'username': self.request.user.username,
            'email': self.request.user.email,
            'date_joined': self.request.user.date_joined.strftime("%d.%m.%Y"),
            'is_staff': self.request.user.is_staff
        }
        return context


# Выход
def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('index')


from .models import DesignRequest, Category
from .forms import DesignRequestForm


# Создание заявки
@login_required
def create_request(request):
    if request.method == 'POST':
        form = DesignRequestForm(request.POST, request.FILES )
        if form.is_valid():
            design_request = form.save(commit=False)
            design_request.customer = request.user
            design_request.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('my_requests')
    else:
        form = DesignRequestForm()
    return render(request, 'create_request.html', {'form': form})



# Просмотр своих заявок
@login_required
def my_requests(request):
    requests = DesignRequest.objects.filter(customer=request.user).order_by('-created_at')
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        requests = requests.filter(status=status_filter)
    return render(request, 'my_requests.html', {'requests': requests})

@login_required
def delete_request(request, pk):
    design_request = get_object_or_404(DesignRequest, pk=pk, customer=request.user)
    if design_request.status in ['complete', 'in-progress']:
        messages.error(request, 'Нельзя удалить заявку, которая уже принята в работу или выполнена.')
        return redirect('my_requests')

    if request.method == 'POST':
        design_request.delete()
        messages.success(request, 'Заявка успешно удалена.')
        return redirect('my_requests')
    return render(request, "delete_request.html", {'request': design_request})

# Детали заявки
@login_required
def request_detail(request, pk):
    design_request = DesignRequest.objects.get(pk=pk, customer=request.user)
    return render(request, 'detail_requests.html', {'request': design_request})

#личный кабинет администратора
class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Доступ запрещен')
            return redirect('main_page')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = DesignRequest.objects.all().order_by('-created_at')
        context['categories'] = Category.objects.all()
        return context


@login_required
def change_request_status(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('main_page')

    design_request = get_object_or_404(DesignRequest, pk=pk)

    if design_request.status != 'new':
        messages.error(request, 'Нельзя изменить статус заявки, которая уже обрабатывается или выполнена')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_comment = request.POST.get('admin_comment')
        design_image = request.FILES.get('design_image')

        if new_status == 'in-progress' and not admin_comment:
            messages.error(request, 'Для принятия в работу необходим комментарий')
            return render(request, 'change_status.html', {'request_obj': design_request})

        if new_status == 'complete' and not design_image:
            messages.error(request, 'Для выполнения заявки необходимо изображение дизайна')
            return render(request, 'change_status.html', {'request_obj': design_request})

        design_request.status = new_status
        if admin_comment:
            design_request.admin_comment = admin_comment
        if design_image:
            design_request.design_image = design_image
        design_request.save()

        messages.success(request, f'Статус заявки изменен на "{design_request.get_status_display()}"')
        return redirect('admin_dashboard')

    return render(request, 'change_status.html', {'request_obj': design_request})


@login_required
def add_category(request):
    if not request.user.is_staff:
        return redirect('main_page')

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.get_or_create(name=name)
            messages.success(request, 'Категория добавлена')
        return redirect('admin_dashboard')

    return redirect('admin_dashboard')


@login_required
def delete_category(request, pk):
    if not request.user.is_staff:
        return redirect('main_page')

    try:
        category = Category.objects.get(pk=pk)
        category.delete()
        messages.success(request, 'Категория удалена')
    except Category.DoesNotExist:
        messages.error(request, 'Категория не найдена')

    return redirect('admin_dashboard')


