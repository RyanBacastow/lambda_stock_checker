.ONESHELL: ;
.PHONY: build build_deployment_dependencies init local_env test deploy deploy_dev deploy_qa deploy_stg deploy_prd clean

ZIP_FILE = custom_stock_watcher__$(shell date +'%m%d%y')_$(shell git rev-parse --short HEAD).zip
AWS_PROFILE = personal
DEPLOY_ENV = prd

build: clean build_deployment_dependencies
	cd custom_stock_watcher_handler; zip -r9 ../$(ZIP_FILE) . -x "tests/*" "schema/*" "pkgs/*"
	cd custom_stock_watcher_handler/pkgs; zip -ur9 ../../$(ZIP_FILE) .
	rm -rf custom_stock_watcher_handler/pkgs

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
		--function-name $(AWS_STOCK_CHECKER_LAMBDA_NAME) \
		--zip-file fileb://$(ZIP_FILE)

clean:
	find . -name .pytest_cache -type d -print0 | xargs -0 rm -r --
	find . -name __pycache__ -type d -print0 | xargs -0 rm -r --
	rm -f $(wildcard custom_stock_watcher_*.zip)
	rm -rf custom_stock_watcher_handler/pkgs
