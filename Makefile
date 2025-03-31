# Makefile для motivation_bot (второй бот)

PROJECT_NAME = motivation_bot
IMAGE_NAME = saa/motivation_bot  # Замените на свой образ
ENV_FILE = .env
DOCKERFILE = Dockerfile

run:
 docker run -it -d --env-file $(ENV_FILE) --restart=unless-stopped --name $(PROJECT_NAME) $(IMAGE_NAME)

stop:
 docker stop $(PROJECT_NAME)

attach:
 docker attach $(PROJECT_NAME)

dell:
 docker rm $(PROJECT_NAME)

build:
 docker build -t $(IMAGE_NAME) -f $(DOCKERFILE) .
