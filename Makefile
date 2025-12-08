# Variáveis essenciais
PROJECT_ID_DEV := serlares-pass-dev
PROJECT_ID_TEST := serlares-pass-test
PROJECT_ID_PROD := serlares-pass
REGION := southamerica-east1
IMAGE_NAME := face-api
DOCKERFILE := Dockerfile
SOURCE_DIR := .

# Configuração do Artifact Registry
REPOSITORY_NAME := docker-repo
AR_HOSTNAME := $(REGION)-docker.pkg.dev
FULL_IMAGE_PATH := $(AR_HOSTNAME)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME)

# Configurações do Cloud Run
SERVICE_ACCOUNT := cloud-run-sa@$(PROJECT_ID).iam.gserviceaccount.com
MEMORY := 2Gi
CPU := 1
TIMEOUT := 300s
MAX_INSTANCES := 5
CONCURRENCY := 80

# 1. Configuração inicial do ambiente
setup-ar:
	@echo "Configurando Artifact Registry..."
	gcloud services enable artifactregistry.googleapis.com --project=$(PROJECT_ID)
	gcloud artifacts repositories create $(REPOSITORY_NAME) \
		--repository-format=docker \
		--location=$(REGION) \
		--description="Repositório Docker para $(IMAGE_NAME)" \
		--project=$(PROJECT_ID)
	gcloud auth configure-docker $(AR_HOSTNAME)

# 2. Autenticação Docker
auth:
	@echo "Autenticando no Artifact Registry..."
	gcloud auth configure-docker $(AR_HOSTNAME)

# 3. Construção da imagem Docker
build:
	@echo "️Construindo imagem Docker..."
	docker build \
		-t $(FULL_IMAGE_PATH) \
		-f $(DOCKERFILE) \
		$(SOURCE_DIR)

# 4. Push para o Artifact Registry
push:
	@echo "Enviando imagem para o Artifact Registry..."
	docker push $(FULL_IMAGE_PATH)

# 5. Deploy no Cloud Run
deploy:
	@echo "Realizando deploy no Cloud Run... $(PROJECT_ID)"
	gcloud run deploy $(IMAGE_NAME) \
		--image $(FULL_IMAGE_PATH) \
		--platform managed \
		--region $(REGION) \
		--service-account $(SERVICE_ACCOUNT) \
		--memory $(MEMORY) \
		--cpu $(CPU) \
		--timeout $(TIMEOUT) \
		--max-instances $(MAX_INSTANCES) \
		--concurrency $(CONCURRENCY) \
		--allow-unauthenticated \
		--project=$(PROJECT_ID)

# 6. Deploys específicos por ambiente
deploy_dev:
	@echo "Iniciando deploy no ambiente DEV..."
	$(MAKE) PROJECT_ID=$(PROJECT_ID_DEV) auth build push deploy

deploy_test:
	@echo "Iniciando deploy no ambiente TEST..."
	$(MAKE) PROJECT_ID=$(PROJECT_ID_TEST) auth build push deploy

deploy_prod:
	@echo "Iniciando deploy no ambiente PROD..."
	$(MAKE) PROJECT_ID=$(PROJECT_ID_PROD) auth build push deploy

# 7. Visualização de logs
logs:
	@echo "📜 Exibindo logs do serviço..."
	gcloud run services logs read $(IMAGE_NAME) \
		--region $(REGION) \
		--project=$(PROJECT_ID)

# 8. Limpeza de recursos
clean:
	@echo "🧹 Removendo imagem local..."
	docker rmi $(FULL_IMAGE_PATH) || true

purge:
	@echo "Removendo todos os recursos..."
	gcloud run services delete $(IMAGE_NAME) \
		--region $(REGION) \
		--platform managed \
		--quiet \
		--project=$(PROJECT_ID)
	gcloud artifacts repositories delete $(REPOSITORY_NAME) \
		--location=$(REGION) \
		--quiet \
		--project=$(PROJECT_ID)

# 9. Ajuda
help:
	@echo "Makefile para Gerenciamento de Deploy no Google Cloud"
	@echo ""
	@echo "Configuração:"
	@echo "  make setup-ar      Configura o Artifact Registry (executar primeiro)"
	@echo ""
	@echo "Comandos Básicos:"
	@echo "  make build         Constrói a imagem Docker"
	@echo "  make push          Envia a imagem para o Artifact Registry"
	@echo "  make deploy        Realiza o deploy no Cloud Run"
	@echo ""
	@echo "Deploys por Ambiente:"
	@echo "  make deploy_dev    Deploy no ambiente de Desenvolvimento"
	@echo "  make deploy_test   Deploy no ambiente de Teste"
	@echo "  make deploy_prod   Deploy no ambiente de Produção"
	@echo ""
	@echo "Monitoramento:"
	@echo "  make logs          Exibe os logs do serviço"
	@echo ""
	@echo "Limpeza:"
	@echo "  make clean         Remove a imagem Docker local"
	@echo "  make purge         Remove TODOS os recursos (cuidado!)"
	@echo ""
	@echo "Ajuda:"
	@echo "  make help          Exibe esta mensagem"