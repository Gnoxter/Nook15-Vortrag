.PHONY: all clean 

all: folien.pdf

clean:
	rm -f folien.pdf
	rm -f protokoll.pdf
	rm -f *.log
	rm -f *.aux
	rm -f *.pos
	rm -f *.toc
	rm -f *.nav
	rm -f *.out
	rm -f *.snm


protokoll.pdf: protokoll.svg
	inkscape protokoll.svg --export-pdf=protokoll.pdf


folien.pdf: folien.tex protokoll.pdf
	pdflatex folien.tex
	pdflatex folien.tex

