from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Form, Question, QuestionOption
from .forms import FormCreateForm
from .serializers import FormSchemaSerializer, QuestionSerializer, QuestionOptionSerializer
from rest_framework import generics, permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Form):
            return obj.user == request.user
        if isinstance(obj, Question):
            return obj.form.user == request.user
        if isinstance(obj, QuestionOption):
            return obj.question.form.user == request.user
        return False

class FormListView(LoginRequiredMixin, ListView):
    model = Form
    template_name = 'form_builder/form_list.html'
    context_object_name = 'forms'

    def get_queryset(self):
        return Form.objects.filter(user=self.request.user)

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
        'questions__options', 'questions__grid_rows', 'questions__grid_columns', 'questions__conditions'
    ).all()
    serializer_class = FormSchemaSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

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