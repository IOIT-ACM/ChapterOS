from rest_framework import serializers
from .models import Form, Question, QuestionOption, GridRow, GridColumn, QuestionCondition

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'label', 'value', 'display_order', 'is_other_option']

class GridRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = GridRow
        fields = ['id', 'label', 'value', 'display_order']

class GridColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = GridColumn
        fields = ['id', 'label', 'value', 'display_order']

class QuestionConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCondition
        fields = ['id', 'depends_on_question', 'trigger_value', 'condition_type']

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    grid_rows = GridRowSerializer(many=True, read_only=True)
    grid_columns = GridColumnSerializer(many=True, read_only=True)
    conditions = QuestionConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'type', 'identifier', 'question_text', 'description_text',
            'display_order', 'is_required', 'validation_rules', 'question_config',
            'options', 'grid_rows', 'grid_columns', 'conditions'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if not data.get('description_text'):
            data.pop('description_text', None)
        if not data.get('validation_rules'):
            data.pop('validation_rules', None)
        if not data.get('question_config'):
            data.pop('question_config', None)
        if not data.get('options'):
            data.pop('options', None)
        if not data.get('grid_rows'):
            data.pop('grid_rows', None)
        if not data.get('grid_columns'):
            data.pop('grid_columns', None)
        if not data.get('conditions'):
            data.pop('conditions', None)

        return data

    def validate(self, data):
        identifier = data.get('identifier')
        if not identifier:
            return data

        if self.instance:
            form = self.instance.form
        else:
            request = self.context.get('request')
            if not request:
                return super().validate(data)
            
            form_id = request.data.get('form')
            if not form_id:
                raise serializers.ValidationError({'form': 'Form ID is required.'})
            
            try:
                form = Form.objects.get(pk=form_id)
                if form.user != request.user:
                    raise serializers.ValidationError("Permission denied for this form.")
            except Form.DoesNotExist:
                raise serializers.ValidationError({'form': 'Invalid form specified.'})

        queryset = Question.objects.filter(form=form, identifier__iexact=identifier)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                'identifier': f'The identifier "{identifier}" is already in use on this form. Please choose a unique one.'
            })

        return data

class FormSchemaSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = [
            'title', 'description',
            'deadline', 'confirmation_message', 'questions'
        ]


class PublicQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['label', 'value', 'is_other_option']

class PublicGridRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = GridRow
        fields = ['label', 'value']

class PublicGridColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = GridColumn
        fields = ['label', 'value']

class PublicQuestionConditionSerializer(serializers.ModelSerializer):
    depends_on_question = serializers.SlugRelatedField(
        slug_field='identifier',
        read_only=True
    )

    class Meta:
        model = QuestionCondition
        fields = ['depends_on_question', 'trigger_value', 'condition_type']

class PublicQuestionSerializer(serializers.ModelSerializer):
    options = PublicQuestionOptionSerializer(many=True, read_only=True)
    grid_rows = PublicGridRowSerializer(many=True, read_only=True)
    grid_columns = PublicGridColumnSerializer(many=True, read_only=True)
    conditions = PublicQuestionConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'identifier', 'type', 'question_text', 'description_text',
            'is_required', 'validation_rules', 'question_config',
            'options', 'grid_rows', 'grid_columns', 'conditions'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if not data.get('description_text'):
            data.pop('description_text', None)
        if not data.get('validation_rules'):
            data.pop('validation_rules', None)
        if not data.get('question_config'):
            data.pop('question_config', None)
        if not data.get('options'):
            data.pop('options', None)
        if not data.get('grid_rows'):
            data.pop('grid_rows', None)
        if not data.get('grid_columns'):
            data.pop('grid_columns', None)
        if not data.get('conditions'):
            data.pop('conditions', None)

        return data

class PublicFormSerializer(serializers.ModelSerializer):
    questions = PublicQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = [
            'title', 'description', 'deadline', 'confirmation_message', 'questions'
        ]