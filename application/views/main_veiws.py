from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import date, timedelta
from ..models import Application
from ..forms import ApplicationForm
from notifications.utils import create_notification

class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'application/application_form.html'
    success_url = reverse_lazy('application:application_list')

    def form_valid(self, form):
        form.instance.applicant = self.request.user
        messages.success(self.request, '申請を送信しました。')
        response = super().form_valid(form)

        create_notification(
            sender=self.request.user,
            recipient=self.request.user.department.manager,
            message=f'{self.request.user.full_name}さんが{self.object.get_application_type_display()}の申請をしました。',
            link_name='application:manager_application_detail',
            pk=self.object.pk,
        )
        return response

class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'application/application_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = Application.objects.filter(applicant=self.request.user).order_by('-start_datetime')
        self.start_date_param = self.request.GET.get('start_date')
        self.end_date_param = self.request.GET.get('end_date')
        self.app_type = self.request.GET.get('application_type', 'all')
        self.status = self.request.GET.get('status', 'all')

        if self.start_date_param:
            try:
                start_date_obj = date.fromisoformat(self.start_date_param)
                queryset = queryset.filter(start_datetime__gte=start_date_obj)
            except ValueError:
                pass
        
        if self.end_date_param:
            try:
                end_date_obj = date.fromisoformat(self.end_date_param)
                next_date = end_date_obj + timedelta(days=1)
                queryset = queryset.filter(start_datetime__lt=next_date)
            except ValueError:
                pass
        
        if self.app_type and self.app_type != 'all':
            queryset = queryset.filter(application_type=self.app_type)
        
        if self.status and self.status != 'all':
            queryset = queryset.filter(status=self.status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['start_date_filter_value'] = self.start_date_param if self.start_date_param else ''
        context['end_date_filter_value'] = self.end_date_param if self.end_date_param else ''
        context['app_type_filter_value'] = self.app_type if self.app_type else ''
        context['status_filter_value'] = self.status if self.status else ''

        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['current_filters_query'] = f'&{query_params.urlencode()}' if query_params else ''
        
        return context
    
class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'application/application_detail.html'

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user).select_related('applicant')

class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'application/application_form.html'
    success_url = reverse_lazy('application:application_list')

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        if obj.status in ['approved', 'pending_hr']:
            messages.warning(self.request, '承認済、または一次承認済のため編集できません。')
            return redirect('application:application_list')
        return obj

class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'application/application_delete.html'
    success_url = reverse_lazy('application:application_list')

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user).select_related('applicant')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        if obj.status in ['approved', 'pending_hr']:
            messages.warning(self.request, '承認済、または一次承認済のため削除できません。')
            return redirect('application:application_list')
        return obj