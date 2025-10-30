FROM python:3.13.3


WORKDIR /app


COPY ../req.txt .
RUN pip install --no-cache-dir -r req.txt


COPY ../app ./app


RUN mkdir -p /app/store_app/static/product_images
RUN mkdir -p /app/store_app/static/category_images

EXPOSE 8080


CMD ["uvicorn", "app.main:auction", "--host", "0.0.0.0", "--port", "8080", "--reload"]

