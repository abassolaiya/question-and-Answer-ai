from .models import QuestionAnswer
import fitz
from transformers import BertTokenizer, BertForQuestionAnswering, pipeline
import re
from PyPDF2 import PdfReader
from io import BytesIO
from .serializers import PDFDocumentUploadSerializer
import os
import torch
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PDFDocument
from .serializers import PDFDocumentUploadSerializer, QuestionAnswerSerializer, PDFDocumentSerializer, TextSummarizationSerializer
from django.shortcuts import render

import logging

qa_model = pipeline("question-answering")
max_len = 384
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForQuestionAnswering.from_pretrained(
    'bert-base-uncased').to(device=device)


class PDFDocumentUploadAPIView(APIView):
    queryset = PDFDocument.objects.all()
    serializer_class = PDFDocumentSerializer

    def post(self, request):
        try:
            uploaded_file = request.FILES.get('pdf_file')
            if not uploaded_file:
                return Response({"error": "PDF file not provided."}, status=status.HTTP_400_BAD_REQUEST)

            pdf_text = self.extract_text_from_pdf(uploaded_file)
            if not pdf_text:
                return Response({"error": "Failed to extract text from the PDF file."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = PDFDocumentUploadSerializer(
                data={'pdf_file': uploaded_file, 'pdf_text': pdf_text})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error occurred during file upload: {e}")
            return Response({"error": "An error occurred during file upload."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def extract_text_from_pdf(self, pdf_file):
        pdf_file.seek(0)  # Ensure the file pointer is at the beginning

        text = ''
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)

            page_text = page.get_text()

            page_text = re.sub(r'\n', ' ', page_text)
            page_text = re.sub(r'\s+', ' ', page_text)

            text += page_text.strip()

        doc.close()

        return text


class TextSummarizationAPIView(APIView):
    serializer_class = TextSummarizationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            input_text = serializer.validated_data.get('input_text')

            # Check if input text length is less than or equal to 1024 characters
            if len(input_text) <= 1024:
                summarizer = pipeline("summarization")
                summarized_text = summarizer(
                    input_text, max_length=200, min_length=30, do_sample=False)[0]['summary_text']
            else:
                # Split the input text into chunks of maximum length 1020 characters
                chunk_size = 1020
                chunks = [input_text[i:i + chunk_size]
                          for i in range(0, len(input_text), chunk_size)]
                summarized_chunks = []

                # Summarize each chunk individually
                summarizer = pipeline("summarization")
                for chunk in chunks:
                    summarized_chunk = summarizer(
                        chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
                    summarized_chunks.append(summarized_chunk)

                # Combine the summarized chunks into a single text
                summarized_text = " ".join(summarized_chunks)

            response_data = {'input_text': input_text,
                             'summarized_text': summarized_text}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionAnswerAPIView(APIView):
    serializer_class = QuestionAnswerSerializer
    qa_model = pipeline("question-answering")

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data.get('question')
            context = serializer.validated_data.get('context')

            if question and context:
                qa_response = qa_model(question=question, context=context)
                answer = qa_response['answer']
                # Create and save the instance of QuestionAnswer model
                instance = QuestionAnswer.objects.create(
                    question=question, context=context, answer=answer)
                # Serialize the instance and return the data
                serialized_instance = self.serializer_class(instance)
                return Response(serialized_instance.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Question or context not provided.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def normalize_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def train_model(self):
        model_file_path = os.path.join(os.path.dirname(
            __file__), 'models', 'model_after_validation.pth')

        model = BertForQuestionAnswering.from_pretrained(
            'bert-base-uncased').to(device=device)
        model.load_state_dict(torch.load(model_file_path))

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        epochs = 1
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)

        for epoch in range(1, epochs + 1):
            print("Training epoch ", str(epoch))
            model.train()
            tr_loss = 0
            nb_tr_steps = 0

            for step, batch in enumerate(train_dataloader):
                batch = tuple(t.to(device) for t in batch)
                inputs = {
                    'input_ids': batch[0],
                    'attention_mask': batch[1],
                    'token_type_ids': batch[2],
                    'start_positions': batch[3],
                    'end_positions': batch[4]
                }
                optimizer.zero_grad()
                outputs = model(**inputs)
                loss = outputs[0]
                loss.backward()
                optimizer.step()
                tr_loss += loss.item()
                nb_tr_steps += 1

            print(f"\nTraining loss={tr_loss / nb_tr_steps:.4f}")

    def generate_answer(self, text, question):
        normalized_text = self.normalize_text(text)
        normalized_question = self.normalize_text(question)

        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')

        inputs = tokenizer(normalized_question, normalized_text,
                           return_tensors='pt', max_length=512, truncation=True)
        input_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']

        with torch.no_grad():
            start_logits, end_logits = model(
                input_ids=input_ids, attention_mask=attention_mask)

        all_tokens = tokenizer.convert_ids_to_tokens(
            input_ids.squeeze().tolist())
        answer_tokens = all_tokens[torch.argmax(
            start_logits): torch.argmax(end_logits) + 1]
        answer = tokenizer.convert_tokens_to_string(answer_tokens)

        return answer


def home(request):
    return render(request, 'home.html')
