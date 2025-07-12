import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    Form, Question, QuestionOption, GridRow, GridColumn,
    QuestionCondition
)
from .serializers import QuestionSerializer, PublicFormSerializer

User = get_user_model()


class TestSetupMixin(TestCase):
    """
    A mixin class to set up common objects for tests, including users and an API client.
    """
    def setUp(self):
        """Set up test users and an API client."""
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='password123',
            email='otheruser@example.com'
        )
        self.client = APIClient()

    def _create_form(self, user, **kwargs):
        """Helper method to create a form instance."""
        defaults = {
            'title': 'Default Test Form',
            'user': user,
        }
        defaults.update(kwargs)
        return Form.objects.create(**defaults)

    def _create_question(self, form, **kwargs):
        """Helper method to create a question instance."""
        defaults = {
            'form': form,
            'type': 'short_answer',
            'question_text': 'What is your name?',
        }
        defaults.update(kwargs)
        return Question.objects.create(**defaults)


class ModelTests(TestSetupMixin):
    """Tests for the application's models."""

    def test_form_str_representation(self):
        """Test that the Form model's __str__ method returns its title."""
        form = self._create_form(self.user, title="My Awesome Form")
        self.assertEqual(str(form), "My Awesome Form")

    def test_form_slug_auto_generation(self):
        """Test that a slug is automatically generated from the title on save."""
        form = self._create_form(self.user, title="A New Form Title")
        self.assertEqual(form.slug, "a-new-form-title")

    def test_form_unique_slug_generation(self):
        """Test that a unique slug is generated when a slug already exists."""
        form1 = self._create_form(self.user, title="Duplicate Title")
        form2 = self._create_form(self.user, title="Duplicate Title")
        self.assertEqual(form1.slug, "duplicate-title")
        self.assertEqual(form2.slug, "duplicate-title-1")

    def test_form_slug_is_not_regenerated_on_update(self):
        """Test that the slug is not changed on subsequent saves."""
        form = self._create_form(self.user, title="Initial Title")
        initial_slug = form.slug
        form.description = "Updated description"
        form.save()
        self.assertEqual(form.slug, initial_slug)

    def test_question_str_representation(self):
        """Test that the Question model's __str__ method returns its text."""
        form = self._create_form(self.user)
        question = self._create_question(form, question_text="What is your quest?")
        self.assertEqual(str(question), "What is your quest?")

    def test_question_identifier_auto_generation(self):
        """Test that an identifier is automatically generated from the question text."""
        form = self._create_form(self.user)
        question = self._create_question(form, question_text="What is your favorite color?")
        self.assertEqual(question.identifier, "what-is-your-favorite-color")

    def test_question_unique_identifier_generation(self):
        """Test that a unique identifier is generated within the scope of a form."""
        form = self._create_form(self.user)
        q1 = self._create_question(form, question_text="Same Question")
        q2 = self._create_question(form, question_text="Same Question")
        self.assertEqual(q1.identifier, "same-question")
        self.assertEqual(q2.identifier, "same-question-1")

    def test_option_and_grid_value_generation(self):
        """Test that QuestionOption, GridRow, and GridColumn generate a 'value' from 'label'."""
        form = self._create_form(self.user)
        question = self._create_question(form)

        option = QuestionOption.objects.create(question=question, label="Option One")
        self.assertEqual(option.value, "option-one")

        row = GridRow.objects.create(question=question, label="Grid Row A")
        self.assertEqual(row.value, "grid-row-a")

        col = GridColumn.objects.create(question=question, label="Grid Column 1")
        self.assertEqual(col.value, "grid-column-1")


class FormViewTests(TestSetupMixin):
    """Tests for standard Django views (non-API)."""

    def test_form_list_view_authenticated_user_sees_only_own_forms(self):
        """Test that an authenticated user sees only their own forms in the list view."""
        self.client.login(username='testuser', password='password123')
        self._create_form(self.user, title="My Form")
        self._create_form(self.other_user, title="Other's Form")

        response = self.client.get(reverse('form_builder:form_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Form")
        self.assertNotContains(response, "Other's Form")
        self.assertTemplateUsed(response, 'form_builder/form_list.html')

    def test_form_create_view_post_success(self):
        """Test successful form creation via the FormCreateView."""
        self.client.login(username='testuser', password='password123')
        form_data = {'title': 'New Test Form', 'description': 'A description.'}
        response = self.client.post(reverse('form_builder:form_create'), data=form_data)

        self.assertEqual(Form.objects.count(), 1)
        new_form = Form.objects.first()
        self.assertEqual(new_form.title, 'New Test Form')
        self.assertEqual(new_form.user, self.user)
        self.assertRedirects(response, reverse('form_builder:form_build', kwargs={'slug': new_form.slug}))

    def test_form_settings_view_permissions(self):
        """Test that only the owner can access the settings view."""
        form = self._create_form(self.user)
        
        # Owner can access
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('form_builder:form_settings', kwargs={'slug': form.slug}))
        self.assertEqual(response.status_code, 200)

        # Non-owner is forbidden
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('form_builder:form_settings', kwargs={'slug': form.slug}))
        self.assertEqual(response.status_code, 403)

    def test_form_settings_view_cannot_edit_approved_form(self):
        """Test that an approved form's settings cannot be accessed."""
        form = self._create_form(self.user, is_approved=True)
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('form_builder:form_settings', kwargs={'slug': form.slug}))
        self.assertEqual(response.status_code, 403)

    def test_form_delete_view_permissions(self):
        """Test that only the owner can delete a form."""
        form = self._create_form(self.user)
        
        # Non-owner cannot delete
        self.client.login(username='otheruser', password='password123')
        response = self.client.post(reverse('form_builder:form_delete', kwargs={'slug': form.slug}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Form.objects.filter(pk=form.pk).exists())

        # Owner can delete
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('form_builder:form_delete', kwargs={'slug': form.slug}))
        self.assertRedirects(response, reverse('form_builder:form_list'))
        self.assertFalse(Form.objects.filter(pk=form.pk).exists())

    def test_form_delete_view_cannot_delete_approved_form(self):
        """Test that an approved form cannot be deleted."""
        form = self._create_form(self.user, is_approved=True)
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('form_builder:form_delete', kwargs={'slug': form.slug}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Form.objects.filter(pk=form.pk).exists())

    def test_form_builder_view_cannot_edit_approved_form(self):
        """Test that the builder view is inaccessible for an approved form."""
        form = self._create_form(self.user, is_approved=True)
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('form_builder:form_build', kwargs={'slug': form.slug}))
        self.assertEqual(response.status_code, 403)


class FormAPITests(TestSetupMixin):
    """Tests for Form-related API endpoints."""

    def setUp(self):
        super().setUp()
        self.form = self._create_form(self.user)

    def test_get_form_schema_permissions(self):
        """Test permissions for the private form schema API."""
        url = reverse('form_builder:api_form_schema', kwargs={'slug': self.form.slug})

        # Unauthenticated gets 401
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Non-owner gets 403
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Owner gets 200
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.form.title)

    def test_get_public_form_schema_active_and_approved(self):
        """Test retrieving a public schema for an active, approved form."""
        self.form.is_active = True
        self.form.is_approved = True
        self.form.save()
        self._create_question(self.form)

        url = reverse('form_builder:api_public_form_schema', kwargs={'slug': self.form.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('questions', response.data)
        self.assertEqual(len(response.data['questions']), 1)
        # Check that it uses the public serializer (no 'id' field)
        self.assertNotIn('id', response.data['questions'][0])

    def test_get_public_form_schema_inactive(self):
        """Test the public schema response for an inactive form."""
        self.form.is_active = False
        self.form.is_approved = True
        self.form.save()
        url = reverse('form_builder:api_public_form_schema', kwargs={'slug': self.form.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "This form is currently not accepting responses.")

    def test_get_public_form_schema_unapproved(self):
        """Test the public schema response for an unapproved form."""
        self.form.is_active = True
        self.form.is_approved = False
        self.form.save()
        url = reverse('form_builder:api_public_form_schema', kwargs={'slug': self.form.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "This form is pending approval.")

    def test_get_public_form_schema_past_deadline(self):
        """Test the public schema response for a form past its deadline."""
        self.form.is_active = True
        self.form.is_approved = True
        self.form.deadline = timezone.now() - datetime.timedelta(days=1)
        self.form.save()
        url = reverse('form_builder:api_public_form_schema', kwargs={'slug': self.form.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "The deadline for this form has passed.")

    def test_reorder_questions_success(self):
        """Test successful reordering of questions."""
        self.client.force_authenticate(user=self.user)
        q1 = self._create_question(self.form, question_text="Q1", display_order=0)
        q2 = self._create_question(self.form, question_text="Q2", display_order=1)
        q3 = self._create_question(self.form, question_text="Q3", display_order=2)

        url = reverse('form_builder:api_reorder_questions', kwargs={'slug': self.form.slug})
        data = {'ordered_ids': [q3.id, q1.id, q2.id]}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        q1.refresh_from_db()
        q2.refresh_from_db()
        q3.refresh_from_db()

        self.assertEqual(q3.display_order, 0)
        self.assertEqual(q1.display_order, 1)
        self.assertEqual(q2.display_order, 2)

    def test_reorder_questions_invalid_data(self):
        """Test reordering with mismatched or invalid question IDs."""
        self.client.force_authenticate(user=self.user)
        q1 = self._create_question(self.form, display_order=0)
        self._create_question(self.form, display_order=1)

        url = reverse('form_builder:api_reorder_questions', kwargs={'slug': self.form.slug})
        # Missing one ID and including a non-existent one
        data = {'ordered_ids': [q1.id, 999]}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('do not match', response.data['detail'])

    def test_reorder_questions_on_approved_form_fails(self):
        """Test that reordering questions on an approved form is forbidden."""
        self.client.force_authenticate(user=self.user)
        self.form.is_approved = True
        self.form.save()
        q1 = self._create_question(self.form, display_order=0)

        url = reverse('form_builder:api_reorder_questions', kwargs={'slug': self.form.slug})
        data = {'ordered_ids': [q1.id]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class QuestionAPITests(TestSetupMixin):
    """Tests for Question-related API endpoints."""

    def setUp(self):
        super().setUp()
        self.form = self._create_form(self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_question_success(self):
        """Test successful creation of a new question."""
        url = reverse('form_builder:api_question_create')
        data = {
            'form': self.form.id,
            'type': 'paragraph',
            'question_text': 'Tell us your story.',
            'is_required': True
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 1)
        q = Question.objects.first()
        self.assertEqual(q.form, self.form)
        self.assertEqual(q.type, 'paragraph')
        self.assertTrue(q.is_required)

    def test_create_question_on_approved_form_fails(self):
        """Test that creating a question on an approved form is forbidden."""
        self.form.is_approved = True
        self.form.save()
        url = reverse('form_builder:api_question_create')
        data = {'form': self.form.id, 'type': 'short_answer', 'question_text': 'This should fail.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_question_with_nested_options(self):
        """Test updating a question and its nested options simultaneously."""
        question = self._create_question(self.form, type='multiple_choice')
        QuestionOption.objects.create(question=question, label="Old Option")

        url = reverse('form_builder:api_question_detail', kwargs={'pk': question.pk})
        data = {
            'question_text': 'Choose one of the following:',
            'options': [
                {'label': 'New Option 1'},
                {'label': 'New Option 2', 'is_other_option': True}
            ]
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        question.refresh_from_db()
        self.assertEqual(question.options.count(), 2)
        self.assertEqual(question.options.first().label, 'New Option 1')
        self.assertTrue(question.options.last().is_other_option)
        self.assertFalse(QuestionOption.objects.filter(label="Old Option").exists())

    def test_update_question_with_nested_grid(self):
        """Test updating a question and its nested grid rows/columns."""
        question = self._create_question(self.form, type='multiple_choice_grid')
        GridRow.objects.create(question=question, label="Old Row")
        GridColumn.objects.create(question=question, label="Old Col")

        url = reverse('form_builder:api_question_detail', kwargs={'pk': question.pk})
        data = {
            'grid_rows': [{'label': 'New Row'}],
            'grid_columns': [{'label': 'New Col'}]
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        question.refresh_from_db()
        self.assertEqual(question.grid_rows.count(), 1)
        self.assertEqual(question.grid_columns.count(), 1)
        self.assertEqual(question.grid_rows.first().label, 'New Row')
        self.assertEqual(question.grid_columns.first().label, 'New Col')

    def test_update_question_with_nested_conditions(self):
        """Test updating a question and its nested conditions."""
        trigger_q = self._create_question(self.form, question_text="Trigger?")
        target_q = self._create_question(self.form, question_text="Target?")

        url = reverse('form_builder:api_question_detail', kwargs={'pk': target_q.pk})
        data = {
            'conditions': [{
                'depends_on_question': trigger_q.id,
                'trigger_value': 'yes',
                'condition_type': 'show_if'
            }]
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target_q.refresh_from_db()
        self.assertEqual(target_q.conditions.count(), 1)
        condition = target_q.conditions.first()
        self.assertEqual(condition.depends_on_question, trigger_q)
        self.assertEqual(condition.trigger_value, 'yes')

    def test_delete_question_and_reorder_others(self):
        """Test that deleting a question reorders the remaining questions."""
        q1 = self._create_question(self.form, display_order=0)
        q2 = self._create_question(self.form, display_order=1)
        q3 = self._create_question(self.form, display_order=2)

        url = reverse('form_builder:api_question_detail', kwargs={'pk': q2.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Question.objects.filter(pk=q2.pk).exists())

        q3.refresh_from_db()
        self.assertEqual(q3.display_order, 1) # Check reordering
        self.assertEqual(len(response.data['questions']), 2)

    def test_delete_question_on_approved_form_fails(self):
        """Test that deleting a question on an approved form is forbidden."""
        self.form.is_approved = True
        self.form.save()
        question = self._create_question(self.form)

        url = reverse('form_builder:api_question_detail', kwargs={'pk': question.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Question.objects.filter(pk=question.pk).exists())


class SerializerTests(TestSetupMixin):
    """Tests for DRF serializers."""

    def test_question_serializer_unique_identifier_validation(self):
        """Test that the QuestionSerializer enforces unique identifiers within a form."""
        form = self._create_form(self.user)
        self._create_question(form, identifier='unique-id')

        # Mock request context for the serializer
        request = type('Request', (), {'user': self.user, 'data': {'form': form.id}})()
        context = {'request': request}

        # Test creating a new question with a duplicate identifier
        data = {
            'form': form.id,
            'type': 'short_answer',
            'question_text': 'Another question',
            'identifier': 'unique-id'
        }
        serializer = QuestionSerializer(data=data, context=context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('identifier', serializer.errors)
        self.assertIn('already in use', serializer.errors['identifier'][0])

    def test_question_serializer_to_representation_removes_empty_fields(self):
        """Test that the serializer's representation omits empty optional fields."""
        form = self._create_form(self.user)
        question = Question.objects.create(
            form=form,
            type='short_answer',
            question_text='A question',
            description_text='', # Empty
            validation_rules={}, # Empty
        )

        serializer = QuestionSerializer(instance=question)
        data = serializer.data

        self.assertNotIn('description_text', data)
        self.assertNotIn('validation_rules', data)
        self.assertNotIn('options', data)
        self.assertNotIn('grid_rows', data)
        self.assertNotIn('conditions', data)

    def test_public_form_serializer_structure(self):
        """Test that the public serializer only exposes public fields."""
        form = self._create_form(self.user)
        question = self._create_question(form)
        QuestionOption.objects.create(question=question, label="Public Option")
        form.questions.add(question)

        serializer = PublicFormSerializer(instance=form)
        data = serializer.data

        # Check form fields
        self.assertIn('title', data)
        self.assertNotIn('id', data)
        self.assertNotIn('slug', data)
        self.assertNotIn('is_active', data)

        # Check question fields
        question_data = data['questions'][0]
        self.assertIn('identifier', question_data)
        self.assertNotIn('id', question_data)
        self.assertNotIn('display_order', question_data)

        # Check option fields
        option_data = question_data['options'][0]
        self.assertIn('label', option_data)
        self.assertIn('value', option_data)
        self.assertNotIn('id', option_data)
        self.assertNotIn('display_order', option_data)