PROJNAME = lucaslehmer

ROOT = $(PROJNAME)

CC = g++

DEBUG =

OPT = -O3 -finline-limit=10000000

CPPFLAGS = $(DEBUG) $(OPT) -fPIC -frecord-gcc-switches -I/usr/include/python2.7

LDFLAGS1 = -shared -fPIC $(DEBUG) $(OPT) -lgmpxx -lgmp

LDFLAGS = -shared -fPIC $(DEBUG) $(OPT) -L. -l$(ROOT)py -lgmpxx -lgmp

LINK_TARGET = $(ROOT).so

BINDSRC = $(ROOT)py_bind.cpp

OBJ =  \
	$(ROOT)py.o

BINDOBJ = \
	$(ROOT)py_bind.o

CSHLIB = 	lib$(ROOT)py.so

REBUILDABLES = $(BINDSRC) $(CSHLIB) $(OBJ) $(BINDOBJ) $(LINK_TARGET)
#REBUILDABLES = $(CSHLIB) $(OBJ) $(BINDOBJ) $(LINK_TARGET)

all : $(LINK_TARGET)
	@echo Build done

# $@ expands to the rule's target, in this case "test_me.exe".
# $^ expands to the rule's dependencies
$(LINK_TARGET) : $(BINDOBJ) 
	g++ -o $@ $(LDFLAGS) $<

# Dependency Rules are often used to capture header file dependencies.
$(ROOT).o : $(ROOT)py.h

$(BINDOBJ) : $(BINDSRC) $(CSHLIB) 
	g++ $(CPPFLAGS) -c -o $@ $<

$(CSHLIB) : $(ROOT)py.o
	g++ $(LDFLAGS1) -o $@ $<

# The rule's command uses some built-in Make Macros:
# $@ for the pattern-matched target
# $< for the pattern-matched dependency
$(OBJ) : $(ROOT)py.cpp
	g++ $(CPPFLAGS) -c -o $@ $<

$(BINDSRC) : 
	PYTHONPATH=$(PYTHONPATH):./ python $(ROOT)Bind.py > $@

# Alternatively to manually capturing dependencies, several automated
# dependency generators exist.  Here is one possibility (commented out)...
# %.dep : %.cpp
#   g++ -M $(FLAGS) $< > $@
# include $(OBJS:.o=.dep)

clean :
	rm -f $(REBUILDABLES)
	@echo Clean done
