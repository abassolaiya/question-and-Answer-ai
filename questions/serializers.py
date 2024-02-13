from rest_framework import serializers
from .models import PDFDocument


class PDFDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = '__all__'


class PDFDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = ('title', 'pdf_file', 'pdf_text')


class TextSummarizationSerializer(serializers.Serializer):
    input_text = serializers.CharField(max_length=200000)
    summarized_text = serializers.CharField(required=False)


class QuestionAnswerSerializer(serializers.Serializer):
    context = serializers.CharField(max_length=200000)  # Add passage field
    question = serializers.CharField(max_length=355)
    answer = serializers.CharField(max_length=2000, required=False)
