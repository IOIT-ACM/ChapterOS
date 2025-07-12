from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from .models import Form, Question, QuestionOption, GridRow, GridColumn, QuestionCondition
from .forms import FormCreateForm, FormSettingsForm
from .serializers import (
    FormSchemaSerializer, QuestionSerializer, QuestionOptionSerializer,
    PublicFormSerializer
)
from rest_framework import generics, permissions, status
from rest_framework.response import Response

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Form):
            return obj.user == request.user
        if isinstance(obj, Question):
            return obj.form.user == request.user
        if isinstance(obj, QuestionOption):
            return obj.question.form.user == request.user
        if isinstance(obj, GridRow):
            return obj.question.form.user == request.user
        if isinstance(obj, GridColumn):
            return obj.question.form.user == request.user
        if isinstance(obj, QuestionCondition):
            return obj.question.form.user == request.user
        return False

class FormListView(LoginRequiredMixin, ListView):
    model = Form
    template_name = 'form_builder/form_list.html'
    context_object_name = 'forms'

    def get_queryset(self):
        return Form.objects.filter(user=self.request.user).prefetch_related('questions', 'submissions')

class FormCreateView(LoginRequiredMixin, CreateView):
    model = Form
    form_class = FormCreateForm
    template_name = 'form_builder/form_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"Form '{form.instance.title}' created. You can now build it.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('form_builder:form_build', kwargs={'slug': self.object.slug})

class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.user

class FormSettingsView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Form
    form_class = FormSettingsForm
    template_name = 'form_builder/form_settings.html'
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        return reverse('form_builder:form_settings', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        messages.success(self.request, "Form settings updated successfully.")
        return super().form_valid(form)

class FormDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Form
    template_name = 'form_builder/form_confirm_delete.html'
    success_url = reverse_lazy('form_builder:form_list')
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        messages.success(self.request, f"Form '{self.object.title}' has been deleted.")
        return super().form_valid(form)

@login_required
def form_builder_view(request, slug):
    form = get_object_or_404(Form, slug=slug, user=request.user)
    if request.method == 'POST':
        form.title = request.POST.get('title', form.title)
        form.description = request.POST.get('description', form.description)
        form.save()
        messages.success(request, "Form details updated successfully.")
        return redirect('form_builder:form_build', slug=form.slug)

    form_schema = FormSchemaSerializer(form).data
    context = {
        'form': form,
        'form_schema_json': form_schema
    }
    return render(request, 'form_builder/form_builder.html', context)

class FormSchemaAPIView(generics.RetrieveAPIView):
    queryset = Form.objects.prefetch_related(
        'questions__options', 'questions__grid_rows', 'questions__grid_columns',
        'questions__conditions__depends_on_question'
    ).all()
    serializer_class = FormSchemaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'slug'

class PublicFormSchemaAPIView(generics.RetrieveAPIView):
    queryset = Form.objects.prefetch_related(
        'questions__options', 'questions__grid_rows', 'questions__grid_columns',
        'questions__conditions__depends_on_question'
    ).all()
    serializer_class = PublicFormSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.is_approved:
            data = {
                'title': instance.title,
                'description': instance.description,
                'message': "This form is pending approval."
            }
            return Response(data, status=status.HTTP_200_OK)

        if not instance.is_active:
            data = {
                'title': instance.title,
                'description': instance.description,
                'message': "This form is currently not accepting responses."
            }
            return Response(data, status=status.HTTP_200_OK)

        if instance.deadline and timezone.now() > instance.deadline:
            data = {
                'title': instance.title,
                'description': instance.description,
                'message': "The deadline for this form has passed."
            }
            return Response(data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class QuestionCreateAPIView(generics.CreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        form = get_object_or_404(Form, pk=self.request.data.get('form'), user=self.request.user)
        serializer.save(form=form)

class QuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        options_data = request.data.pop('options', None)
        grid_rows_data = request.data.pop('grid_rows', None)
        grid_columns_data = request.data.pop('grid_columns', None)
        conditions_data = request.data.pop('conditions', None)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if options_data is not None:
            instance.options.all().delete()
            for i, option_data in enumerate(options_data):
                option_data.pop('id', None)
                option_data.pop('display_order', None)
                QuestionOption.objects.create(question=instance, display_order=i, **option_data)

        if grid_rows_data is not None:
            instance.grid_rows.all().delete()
            for i, row_data in enumerate(grid_rows_data):
                row_data.pop('id', None)
                row_data.pop('display_order', None)
                GridRow.objects.create(question=instance, display_order=i, **row_data)

        if grid_columns_data is not None:
            instance.grid_columns.all().delete()
            for i, col_data in enumerate(grid_columns_data):
                col_data.pop('id', None)
                col_data.pop('display_order', None)
                GridColumn.objects.create(question=instance, display_order=i, **col_data)

        if conditions_data is not None:
            instance.conditions.all().delete()
            for condition_data in conditions_data:
                condition_data.pop('id', None)
                depends_on_question_id = condition_data.pop('depends_on_question', None)
                if not depends_on_question_id:
                    continue
                
                try:
                    depends_on_question = Question.objects.get(pk=depends_on_question_id, form=instance.form)
                    QuestionCondition.objects.create(
                        question=instance,
                        depends_on_question=depends_on_question,
                        **condition_data
                    )
                except Question.DoesNotExist:
                    pass

        updated_form = Form.objects.prefetch_related(
            'questions__options', 'questions__grid_rows', 'questions__grid_columns', 'questions__conditions__depends_on_question'
        ).get(pk=instance.form.pk)
        
        return Response(FormSchemaSerializer(updated_form).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        form = instance.form
        deleted_order = instance.display_order

        with transaction.atomic():
            # The perform_destroy method calls instance.delete(), which triggers
            # all on_delete=CASCADE relations.
            self.perform_destroy(instance)

            # Re-sequence the display_order of remaining questions to prevent gaps.
            Question.objects.filter(
                form=form, 
                display_order__gt=deleted_order
            ).update(display_order=F('display_order') - 1)

        # Fetch the entire form again to return the updated schema, which is
        # what the frontend expects after any modification.
        updated_form = Form.objects.prefetch_related(
            'questions__options', 'questions__grid_rows', 'questions__grid_columns', 'questions__conditions__depends_on_question'
        ).get(pk=form.pk)
        
        return Response(FormSchemaSerializer(updated_form).data, status=status.HTTP_200_OK)


class QuestionOptionCreateAPIView(generics.CreateAPIView):
    serializer_class = QuestionOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        question = get_object_or_404(Question, pk=self.request.data.get('question'), form__user=self.request.user)
        serializer.save(question=question)

class QuestionOptionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]