FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Windows editors can save start.sh with CRLF line endings, which breaks it on Linux.
RUN sed -i "s/\r$//" start.sh

CMD ["sh", "start.sh"]
