FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY tests ./tests
COPY notebooks ./notebooks
ENV PYTHONPATH=/app
CMD ["python", "-m", "src.experiments.run_benchmark", "--help"]
