from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Form, Section, Question, QuestionOption
from .forms import FormCreateForm
from .serializers import FormSchemaSerializer, SectionSerializer, QuestionSerializer, QuestionOptionSerializer
from rest_framework import generics, permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Form):
            return obj.owner == request.user
        if isinstance(obj, Section):
            return obj.form.owner == request.user
        if isinstance(obj, Question):
            return obj.section.form.owner == request.user
        if isinstance(obj, QuestionOption):
            return obj.question.section.form.owner == request.user
        return False

class FormListView(LoginRequiredMixin, ListView):
    model = Form
    template_name = 'form_builder/form_list.html'
    context_object_name = 'forms'

    def get_queryset(self):
        return Form.objects.filter(owner=self.request.user)

class FormCreateView(LoginRequiredMixin, CreateView):
    model = Form
    form_class = FormCreateForm
    template_name = 'form_builder/form_create.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Form '{form.instance.title}' created. You can now build it.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('form_builder:form_build', kwargs={'pk': self.object.pk})

class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        if isinstance(obj, Form):
            return self.request.user == obj.owner
        return False

class FormDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Form
    template_name = 'form_builder/form_confirm_delete.html'
    success_url = reverse_lazy('form_builder:form_list')

    def form_valid(self, form):
        messages.success(self.request, f"Form '{self.object.title}' has been deleted.")
        return super().form_valid(form)

@login_required
def form_builder_view(request, pk):
    form = get_object_or_404(Form, pk=pk, owner=request.user)
    if request.method == 'POST':
        form.title = request.POST.get('title', form.title)
        form.description = request.POST.get('description', form.description)
        form.save()
        messages.success(request, "Form details updated successfully.")
        return redirect('form_builder:form_build', pk=form.pk)
        
    form_schema = FormSchemaSerializer(form).data
    context = {
        'form': form,
        'form_schema_json': form_schema
    }
    return render(request, 'form_builder/form_builder.html', context)

class FormSchemaAPIView(generics.RetrieveAPIView):
    queryset = Form.objects.prefetch_related('sections__questions__options').all()
    serializer_class = FormSchemaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

class SectionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        form_id = self.request.query_params.get('form_id')
        if form_id:
            return Section.objects.filter(form_id=form_id, form__owner=self.request.user)
        return Section.objects.none()

    def perform_create(self, serializer):
        form = get_object_or_404(Form, pk=self.request.data.get('form'), owner=self.request.user)
        serializer.save(form=form)

class SectionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

class QuestionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        section_id = self.request.query_params.get('section_id')
        if section_id:
            return Question.objects.filter(section_id=section_id, section__form__owner=self.request.user)
        return Question.objects.none()

    def perform_create(self, serializer):
        section = get_object_or_404(Section, pk=self.request.data.get('section'), form__owner=self.request.user)
        serializer.save(section=section)

class QuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

class QuestionOptionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        question_id = self.request.query_params.get('question_id')
        if question_id:
            return QuestionOption.objects.filter(question_id=question_id, question__section__form__owner=self.request.user)
        return QuestionOption.objects.none()

    def perform_create(self, serializer):
        question = get_object_or_404(Question, pk=self.request.data.get('question'), section__form__owner=self.request.user)
        serializer.save(question=question)

class QuestionOptionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]