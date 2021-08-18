libworm.so: worm.c
	gcc -c worm.c -l curses -fPIC
	gcc -shared -o libworm.so worm.o -l curses
	rm worm.o
