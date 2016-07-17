PROJNAME = lucaslehmer

ROOT = $(PROJNAME)

CC = g++

DEBUG =

OPT = -O3

CPPFLAGS = $(DEBUG) $(OPT) -fPIC -frecord-gcc-switches -I/usr/include/python2.7

LDFLAGS1 = -shared -fPIC $(DEBUG) $(OPT) -rdynamic -Wl,-rpath -Wl,$(PWD) -Wl,-rpath -Wl,/usr/lib/x86_64-linux-gnu -lgmpxx -lgmp

LDFLAGS = -shared -fPIC $(DEBUG) $(OPT) -rdynamic -Wl,-rpath -Wl,$(PWD) -Wl,-rpath -Wl,/usr/lib/x86_64-linux-gnu -L. -l$(ROOT)py -lgmpxx -lgmp

LINK_TARGET = $(ROOT).so

BINDSRC = $(ROOT)py_bind.cpp

OBJ =  \
	$(ROOT)py.o

BINDOBJ = \
	$(ROOT)py_bind.o

CSHLIB = \
	lib$(ROOT)py.so

REBUILDABLES = $(BINDSRC) $(CSHLIB) $(OBJ) $(BINDOBJ) $(LINK_TARGET)

all : $(LINK_TARGET)
	@echo Build done

$(LINK_TARGET) : $(BINDOBJ) $(OBJ)
	g++ -o $@ $< $(LDFLAGS)

$(ROOT).o : $(ROOT)py.h

$(BINDOBJ) : $(BINDSRC) $(CSHLIB) 
	g++ $(CPPFLAGS) -c -o $@ $<

$(CSHLIB) : $(ROOT)py.o
	g++ $(LDFLAGS1) -o $@ $<

$(OBJ) : $(ROOT)py.cpp
	g++ $(CPPFLAGS) -c -o $@ $<

$(BINDSRC) : 
	PYTHONPATH=$(PYTHONPATH):./ python $(ROOT)Bind.py > $@

clean :
	rm -f $(REBUILDABLES)
	@echo Clean done
