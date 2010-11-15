

clean:
	-rm bmf/*.pyc *.pyc *.html bmf/*.log *.log

build:  clean
	cd ..; zip bmf.zip bmf/* bmf/bmf/*
        
