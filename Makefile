.ONESHELL: ;
.PHONY: build build_deployment_dependencies init local_env test deploy deploy_dev deploy_qa deploy_stg deploy_prd clean

ZIP_FILE = iwin_pavlova_etl_lambda__$(shell date +'%m%d%y')_$(shell git rev-parse --short HEAD).zip
AWS_PROFILE = default
DEPLOY_ENV = dev

build: clean build_deployment_dependencies
	cd iwin_event_handler; zip -r9 ../$(ZIP_FILE) . -x "tests/*" "schema/*" "pkgs/*"
	cd iwin_event_handler/pkgs; zip -ur9 ../../$(ZIP_FILE) .
	rm -rf iwin_event_handler/pkgs

build_deployment_dependencies:
	docker build -t deployment_dependencies .
	docker create --name dummy_container -t deployment_dependencies
	docker cp dummy_container:/build/pkgs iwin_event_handler/
	docker rm -f dummy_container

init:
	pip install -r requirements.txt

test:
	py.test -s

deploy_dev:
	$(MAKE) deploy DEPLOY_ENV=dev

deploy_qa:
	$(MAKE) deploy DEPLOY_ENV=qa

deploy_stg:
	$(MAKE) deploy DEPLOY_ENV=stg

deploy_prd:
	@read -p "Are you sure you wish to deploy to Production [Y]: " YN; \
	$(MAKE) .deploy_prd_yn YN=$$YN

.deploy_prd_yn:
# not indented because Makefiles require this to be this way. IDK...
ifeq ($(YN),Y)
	$(MAKE) deploy DEPLOY_ENV=prd
else
	exit 1
endif

deploy: build
	aws lambda update-function-code \
		--profile $(AWS_PROFILE) \
		--function-name iwin-au-tms-pavlova-$(DEPLOY_ENV)20-record-queue-uploader \
		--zip-file fileb://$(ZIP_FILE)

clean:
	find . -name .pytest_cache -type d -print0 | xargs -0 rm -r --
	find . -name __pycache__ -type d -print0 | xargs -0 rm -r --
	rm -f $(wildcard iwin_pavlova_etl_lambda_*.zip)
	rm -rf iwin_event_handler/pkgs
