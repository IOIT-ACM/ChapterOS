from rest_framework import serializers
from .models import Form, Section, Question, QuestionOption

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'label', 'value', 'order']

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'type', 'label', 'placeholder', 'default_value', 'order', 'is_required', 'regex_validation_rules', 'options']

class SectionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'title', 'order', 'questions']

class FormSchemaSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField()

    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'owner', 'is_active', 'deadline', 'sections']