
FROM node:14 as builder
COPY . /app
WORKDIR /app
RUN yarn && yarn global add @quasar/cli
RUN quasar build -m spa

FROM nginx:1.21.6 as runner
COPY --from=builder /app/dist/spa /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80