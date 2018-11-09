all:	remap

remap:
	f2py -c --fcompiler=intelem -m remap remap.f
#	f2py -c --compiler=intel --fcompiler=intel --f77exec=/gpfs/u/apps/ch/opt/ncarcompilers/0.4.1/ifort -m remap remap.f

clean:
	rm -r *.so
