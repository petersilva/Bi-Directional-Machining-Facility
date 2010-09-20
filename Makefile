

clean:
	-rm bmf/*.pyc *.pyc *.html

build:  clean
	cd ..; zip bmf.zip bmf/* bmf/bmf/*
        
