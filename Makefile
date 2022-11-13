
run:
	python src/main/python/imagewao.py

tags:
	ctags -R .

clean-pycache:
	find . | grep -E "(__pycache__$)" | xargs rm -rf
