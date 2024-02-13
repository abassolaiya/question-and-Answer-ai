from django.urls import path
from .views import (
    PDFDocumentListCreateAPIView,
    PDFDocumentRetrieveUpdateDestroyAPIView,
    PDFDocumentUploadAPIView,
    QuestionAnswerAPIView,
    TextSummarizationAPIView,
)
from .views import home

urlpatterns = [
    path('', home, name='home'),
    # Endpoint for listing and creating PDF documents
    path('pdf/', PDFDocumentListCreateAPIView.as_view(), name='pdf-list-create'),

    # Endpoint for retrieving, updating, and deleting a specific PDF document
    path('pdf/<int:pk>/',
         PDFDocumentRetrieveUpdateDestroyAPIView.as_view(), name='pdf-detail'),

    # Endpoint for uploading a PDF document
    path('pdf/upload/', PDFDocumentUploadAPIView.as_view(), name='pdf-upload'),

    # Endpoint for question answering
    path('qa/', QuestionAnswerAPIView.as_view(), name='question-answer'),

    # Endpoint for text summarization
    path('summarize/', TextSummarizationAPIView.as_view(),
         name='text-summarization'),
]
