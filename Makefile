# Variáveis
PROJECT_ID_DEV = serlares-pass-dev
PROJECT_ID_TEST = serlares-pass-test
PROJECT_ID_PROD = serlares-pass
REGION = southamerica-east1
IMAGE_NAME = face-api
DOCKERFILE = Dockerfile
SOURCE_DIR = .

# 1. Construir a imagem Docker
build:
	docker build -t gcr.io/$(PROJECT_ID)/$(IMAGE_NAME) -f $(DOCKERFILE) $(SOURCE_DIR)

# 2. Fazer o push da imagem para o Google Container Registry
push:
	docker push gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)

# 3. Implantar a imagem no Google Cloud Run
deploy:
	gcloud run deploy $(IMAGE_NAME) \
		--image gcr.io/$(PROJECT_ID)/$(IMAGE_NAME) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--timeout 300s \
		--memory 2Gi

deploy_dev:
	gcloud config set project $(PROJECT_ID_DEV)
	$(MAKE) PROJECT_ID=$(PROJECT_ID_DEV) build
	$(MAKE) PROJECT_ID=$(PROJECT_ID_DEV) push
	$(MAKE) PROJECT_ID=$(PROJECT_ID_DEV) deploy

deploy_test:
	gcloud config set project $(PROJECT_ID_TEST)
	$(MAKE) PROJECT_ID=$(PROJECT_ID_TEST) build
	$(MAKE) PROJECT_ID=$(PROJECT_ID_TEST) push
	$(MAKE) PROJECT_ID=$(PROJECT_ID_TEST) deploy

deploy_prod:
	gcloud config set project $(PROJECT_ID_PROD)
	$(MAKE) PROJECT_ID=$(PROJECT_ID_PROD) build
	$(MAKE) PROJECT_ID=$(PROJECT_ID_PROD) push
	$(MAKE) PROJECT_ID=$(PROJECT_ID_PROD) deploy

# 4. Exibir os logs do serviço no Google Cloud Run
logs:
	gcloud run services logs read $(IMAGE_NAME) --region $(REGION)

# 5. Limpar as imagens locais do Docker
clean:
	docker rmi gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)

# 6. Help
help:
	@echo "Makefile para gerenciamento do deploy no Google Cloud Run"
	@echo "Comandos:"
	@echo "  make build        - Constrói a imagem Docker"
	@echo "  make push         - Faz o push da imagem para o GCR"
	@echo "  make deploy_dev   - Realiza o deploy no ambiente de desenvolvimento"
	@echo "  make deploy_test  - Realiza o deploy no ambiente de teste"
	@echo "  make deploy_prod  - Realiza o deploy no ambiente de produção"
	@echo "  make logs         - Exibe os logs do serviço no Cloud Run"
	@echo "  make clean        - Remove a imagem local do Docker"
	@echo "  make help         - Exibe este texto de ajuda"
