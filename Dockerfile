FROM python:3.7-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE TRUE
ENV PYTHONUNBUFFERED TRUE

COPY requirements.txt /qa_ai/requirements.txt

# Set working directory
WORKDIR /qa_ai

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .


CMD ["/qa_ai/entrypoint.sh"]
