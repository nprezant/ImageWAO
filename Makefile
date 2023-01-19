
run:
	python src/main/python/main.py

tags:
	ctags -R .

clean-pycache:
	find . | grep -E "(__pycache__$)" | xargs rm -rf
