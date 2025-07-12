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

class FormSchemaSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Form
        fields = [
            'id', 'title', 'description', 'slug', 'user', 'is_active',
            'deadline', 'confirmation_message', 'questions'
        ]