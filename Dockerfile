# pulling from official python image: docs.docker.com/language/python/build-images/
FROM python:3.12-slim

WORKDIR /app

# copying dependencies and installing
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# moving the rest of our files
COPY . .

# setting path for src imports
ENV PYTHONPATH=/app

# using python execution as our default
CMD ["python3", "-m", "src.main"]
