# Variáveis
PROJECT_ID = serlares-pass-dev
REGION = southamerica-east1
IMAGE_NAME = face-api
GCR_URL = gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
DOCKERFILE = Dockerfile
SOURCE_DIR = .

# Etapas

# 1. Construir a imagem Docker
build:
	docker build -t $(GCR_URL) -f $(DOCKERFILE) $(SOURCE_DIR)

# 2. Fazer o push da imagem para o Google Container Registry
push: build
	docker push $(GCR_URL)

# 3. Implantar a imagem no Google Cloud Run
deploy: push
	gcloud run deploy $(IMAGE_NAME) \
		--image $(GCR_URL) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--timeout 300s \
		--memory 2Gi

# 4. Exibir os logs do serviço no Google Cloud Run
logs:
	gcloud run services logs read $(IMAGE_NAME) --region $(REGION)

# 5. Limpar as imagens locais do Docker
clean:
	docker rmi $(GCR_URL)

# 6. Help
help:
	@echo "Makefile para gerenciamento do deploy no Google Cloud Run"
	@echo "Comandos:"
	@echo "  make build        - Constrói a imagem Docker"
	@echo "  make push         - Faz o push da imagem para o GCR"
	@echo "  make deploy       - Realiza o deploy no Cloud Run"
	@echo "  make logs         - Exibe os logs do serviço no Cloud Run"
	@echo "  make clean        - Remove a imagem local do Docker"
	@echo "  make help         - Exibe este texto de ajuda"
