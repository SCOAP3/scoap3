FROM node:18 as client-builder

ARG APP_UI=/ui

WORKDIR ${APP_UI}
COPY ./ui/package.json ${APP_UI}
RUN yarn install
COPY ./ui ${APP_UI}

RUN yarn build
