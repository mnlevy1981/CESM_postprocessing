all : develop

test : FORCE
	python -c "import esmlab; print esmlab.__version__"

develop : install

# NOTE: need to cd to esmlab dir first before setup because
# the Makefile to build and install in the virtualenv is
# different from the distibution Makefile.

install : FORCE
	cd esmlab; python setup.py install

#
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
	-rm -f .Makedepend *.o *.mod *.il *.pyc
	-rm -rf esmlab/*.egg-info 
	-rm -rf esmlab/build

#
# FORCE - Null rule to force things to happen.
#
FORCE :
