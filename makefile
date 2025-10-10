.PHONY: install run test
install:
	@echo "# 1. Crie um ambiente virtual "
	python -m venv venv && \
	source venv/bin/activate
	@echo "# 2. Instale as dependências" 
	(pip install --upgrade pip)
	(pip install -r requirements.txt)


run:
	source venv/bin/activate
	export $(cat env.dev | xargs) 
	uvicorn main:app --reload


test:
	@echo "# 1. Crie um ambiente virtual "
	@echo "# 2. Instale as dependências"
