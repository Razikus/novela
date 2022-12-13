FROM python:3.11

WORKDIR /app 
RUN wget https://nodejs.org/dist/v18.12.1/node-v18.12.1-linux-x64.tar.xz && tar -xvf node-v18.12.1-linux-x64.tar.xz && mv node-v18.12.1-linux-x64 /usr/bin/nodebin && rm -rf  node-v18.12.1-linux-x64.tar.xz
ENV PATH=${PATH}:/usr/bin/nodebin/bin
RUN npm install -g mdpdf
COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt && rm -f /requirements.txt
COPY ./novela /app/novela

# Needs for mdpdf
RUN apt-get update && apt-get install curl gnupg -y \
  && curl --location --silent https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
  && apt-get update \
  && apt-get install google-chrome-stable -y --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /static

ENV STATICPREFIX=/static/
ENV STARTING_API_KEY=hehe
ENV DB_URL=immudb:3322
ENV DB_USER=immudb
ENV DB_PASS=immudb
ENV DB_NAME=defaultdb
EXPOSE 8000
CMD ["uvicorn", "novela.main:app", "--host", "0.0.0.0", "--port", "8000"]