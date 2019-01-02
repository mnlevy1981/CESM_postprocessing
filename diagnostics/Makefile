all : develop

test : FORCE
	xmllint --schema 
	python -m unittest discover --start-directory diagnostics/test

develop : FORCE
	python setup.py $@
	pip install -e git+https://github.com/NCAR/esmlab.git@v0.0.1#egg=esmlab

install : FORCE
	python setup.py $@
	pip install -e git+https://github.com/NCAR/esmlab.git@v0.0.1#egg=esmlab

clean : 
	-rm -f *~ *.CKP *.ln *.BAK *.bak .*.bak \
		core errs \
		,* .emacs_* \
		tags TAGS \
		make.log MakeOut \
		*.tmp tmp.txt

#
# clobber - Really clean up the directory.
#
clobber : clean
	-rm -rf .Makedepend *.o *.mod *.il *.pyc
	-rm -rf *.egg-info build

#
# FORCE - Null rule to force things to happen.
#
FORCE :
