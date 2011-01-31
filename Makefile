

clean:
	-rm bmf/*.pyc *.pyc *.html bmf/*.log *.log bmf/*.sav *.sav

build:  clean
	cd ..; zip bmf.zip bmf/* bmf/bmf/*
        
