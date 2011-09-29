#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

void (*fp)(void);

void handle_error(void)
{
	printf("you're doing it wrong\n");
}

void handle200(void)
{
	printf("you're still not doing it right\n");
}

void setvalue(int x)
{
	printf("am i cute yet? %i\n", x);
	if (x == 200)
	{
		fp = handle200;	
	}
	else
	{
		fp = handle_error;
	}
}


int main(int argc, char *argv[])
{
	time_t mytime;
	int x;
	size_t bufsize = 64 * 1024;
	char *buf;

	buf = malloc(bufsize);
	
	memset(buf, 0, bufsize);
	fgets(buf, bufsize-1, stdin);
	x = atoi(buf);
	setvalue(x);
	mytime = time();
	printf("my time is %u\n", mytime);
	fp();
}

