LEX = flex
YACC = bison -y

DEFINE += -DDEADLOCK_ABORT=1

INCPATH = -I. -Iarbiters -Iallocators -Irouters -Inetworks -Ipower
CPPFLAGS += -Wall $(INCPATH) $(DEFINE)
CPPFLAGS += -O3 -std=c++11
LFLAGS +=

PROG := booksim
BOOKSIM_DRIVER := booksim_driver
LIBDYN := libbooksim.so
LIBSTA := libbooksim.a

# simulator source files
CPP_SRCS = $(wildcard *.cpp) $(wildcard */*.cpp) $(wildcard */*/*.cpp) $(wildcard */*/*/*.cpp)
CPP_OBJS = $(CPP_SRCS:.cpp=.o)
CPP_DEPS = $(CPP_SRCS:.cpp=.d)

LEX_SRCS = lex.yy.c
LEX_OBJS = lex.yy.o

YACC_SRCS = y.tab.c
YACC_HDRS = y.tab.h
YACC_OBJS = y.tab.o

NETRACE_SRCS = netrace/netrace.c
NETRACE_HDRS = netrace/netrace.h
NETRACE_OBJS = netrace/netrace.o

OBJS := $(CPP_OBJS) $(LEX_OBJS) $(YACC_OBJS) $(NETRACE_OBJS)

MAIN_OBJS = $(filter-out main.o booksim_driver.o booksim_wrapper.o, $(OBJS))
BOOKSIM_DRIVER_OBJS = booksim_driver.o $(filter-out main.o booksim_driver.o, $(OBJS))

.PHONY: all clean lib_static

# Ensure lib_static builds before booksim
all: lib_static $(PROG) $(BOOKSIM_DRIVER)

# Booksim binary depends on the static library
$(PROG): main.o $(MAIN_OBJS) $(LIBSTA)
	$(CXX) $(LFLAGS) main.o $(MAIN_OBJS) -L. -lbooksim -o $(PROG)

# Booksim driver depends on the static library
$(BOOKSIM_DRIVER): $(BOOKSIM_DRIVER_OBJS) $(LIBSTA)
	$(CXX) $(CPPFLAGS) -o $(BOOKSIM_DRIVER) $(BOOKSIM_DRIVER_OBJS) -L. -lbooksim

$(LEX_SRCS): config.l
	$(LEX) $<

$(YACC_SRCS) $(YACC_HDRS): config.y
	$(YACC) -d $<

$(LEX_OBJS): $(LEX_SRCS) $(YACC_HDRS)
	$(CC) $(CPPFLAGS) -c $< -o $@

$(YACC_OBJS): $(YACC_SRCS)
	$(CC) $(CPPFLAGS) -c $< -o $@

$(NETRACE_OBJS): $(NETRACE_SRCS) $(NETRACE_HDRS)
	$(CC) $(CPPFLAGS) -c $< -o $@

%.o: %.cpp
	$(CXX) $(CPPFLAGS) -MMD -c $< -o $@

# Rule to build libbooksim.a
lib_static: $(OBJS)
	ar rvs $(LIBSTA) $(filter-out main.o booksim_driver.o, $(OBJS))

# Shared library option (optional)
lib: $(OBJS)
	$(CXX) -shared $(LFLAGS) $(filter-out main.o booksim_driver.o, $(OBJS)) -o $(LIBDYN)

clean:
	rm -f $(YACC_SRCS) $(YACC_HDRS)
	rm -f $(LEX_SRCS)
	rm -f $(CPP_DEPS)
	rm -f $(OBJS)
	rm -f $(PROG)
	rm -f $(LIBDYN)
	rm -f $(LIBSTA)
	rm -f $(BOOKSIM_DRIVER) $(BOOKSIM_DRIVER_OBJS) main.o
	rm -f booksim_wrapper.o

distclean: clean
	rm -f *~ */*~ */*/*~
	rm -f *.o */*.o */*/*.o
	rm -f *.d */*.d */*/*.d

-include $(CPP_DEPS)
