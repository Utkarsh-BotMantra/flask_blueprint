FROM python:3.6.6-alpine3.6
RUN pip install --upgrade pip
ENV TZ=Asia/Kolkata
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 
EXPOSE 5002
CMD [ "gunicorn","-b", "0.0.0.0:5002","-w","2", "app:app","--timeout","900"]