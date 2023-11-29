########################################################################################################################
# Project installation
########################################################################################################################

install:
	pyenv virtualenv --force 3.11.6 disagreen
	pyenv local disagreen
	VIRTUAL_ENV=$$(pyenv prefix) poetry install --no-root --sync

########################################################################################################################
# Quality checks
########################################################################################################################

test:
	poetry run pytest tests --cov src --cov-report term --cov-report=html --cov-report xml --junit-xml=tests-results.xml --cov-fail-under 30

format-check:
	poetry run ruff format --check src tests

format-fix:
	poetry run ruff format src tests

lint-check:
	poetry run ruff check src tests

lint-fix:
	poetry run ruff check src tests --fix

type-check:
	poetry run mypy src

########################################################################################################################
# Local run
########################################################################################################################

start-streamlit-app:
	poetry run streamlit run "src/streamlit_app/main.py"

########################################################################################################################
# Deployment
########################################################################################################################

AWS_ACCOUNT_URL=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
ECR_REPOSITORY_NAME=disagreen
ECS_CLUSTER_NAME=disagreen
ECS_SERVICE_NAME=disagreen
IMAGE_URL=${AWS_ACCOUNT_URL}/${ECR_REPOSITORY_NAME}

ecr-login:
	aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_URL}

# Redeployment of ECS service to take into account the new image
redeploy-ecs-service:
	aws ecs update-service --cluster ${ECS_CLUSTER_NAME} --service ${ECS_SERVICE_NAME} --force-new-deployment --no-cli-pager

deploy-api-from-x86:
	make ecr-login

	# Build image
	docker build . -t api

	# Tag and push image to ecr
	docker tag api ${IMAGE_URL}:latest
	docker push ${IMAGE_URL}:latest

	make redeploy-ecs-service

# When building an image from an ARM processor (Mac M1 or M2) with the standard way (`deploy-api-from-x86`), the
# resulting image can only be run on ARM machines (which is not the case of the provisioned instance). Using `buildx`
# allows to overcome this limitation, by specifying for which platform the image is built.
deploy-api-from-arm:
	make ecr-login

	docker buildx build --platform linux/amd64 --push -t ${IMAGE_URL}:latest .
	make redeploy-ecs-service
