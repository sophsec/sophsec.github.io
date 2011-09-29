/* 
	servHttpFile: a bullshit piece of lame sauce i wrote
	for some pen test or something. It prints the request it received, 
	and then prompts the the user to accept (aka serve the file) or deny 
	with a 404. Useful for staging media/browser exploits.

	It should have been written in perl/python/ruby to save time, 
	but this way I can troll Postmodern by wasting my time on it. 

	some days i'm Trebek, some days i'm Connery.

	No warranty implied, promised or made in anyway. 
	This code is shit and will turn your toaster into Satan.
	Do not run this code. 

	written by Brandon "drraid" Edwards
	drraid@gmail.com

*/


#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netdb.h>


/* generic http 200 response buffer */
char http200[]=
"HTTP/1.1 200 OK\r\n"
"Server: Apache\r\n"
/* should really code in support for content-type. */
/* lol but then again i should really just use python + some library */
"Content-Length: %i\r\n"
"\r\n";

/* 404 reponse buffer */
char http404[]=
"HTTP/1.1 404 Not Found\r\n"
"Server: Apache\r\n"
"\r\n";

/* blah blah trivial socket write loop. 100th implementation. */
int loopwrite(int sd, char *buf, ssize_t len)
{
	ssize_t writelen = 0;
	ssize_t lenwrote = 0;

	while (writelen < len)
	{
		lenwrote = write(sd, buf, len - writelen);

		if (lenwrote == -1)
		{
			printf("unable to write()\n");
			return -1;
		}

		writelen += lenwrote;	
	}

	return 0;
}

/* LoL Hi Karla. This is my Main function. Marry me? */
int main(int argc, char *argv[])
{
	char *filename = NULL;
	int fd = 0;
	struct stat statbuf;
	char inbuf[1024];
	char *outbuf;

	int tr = 1;
	int sd = 0;
	int hostsd = 0;
	short port = htons(80);
	struct sockaddr_in localin;
	struct sockaddr_in remotein;
	size_t socklen = sizeof(remotein);
	ssize_t readlen = 0;
	
	if (!argv[1])
	{
		printf("servHttpFile v007\n");
		printf("usage: %s <file> [port]\n", argv[0]);	
		exit(1);
	}

	if (argv[2])
	{
		port = htons(atoi(argv[2]));
		if (!port)
		{
			printf("invalid port %s\n", argv[2]);
			exit(1);
		}
		printf("using port %s\n", argv[2]);
	}
	else
	{
		printf("using default port 80\n");
	}	

	filename = argv[1];		

	fd = open(filename, O_RDONLY);

	if (fd == -1)
	{
		printf("unable to open %s\n", filename);	
		exit(2);
	}

	if (fstat(fd, &statbuf) == -1) 
	{
		printf("unable to fstat()\n");
		exit(2);
	}

	sd = socket(AF_INET, SOCK_STREAM, 0);	


	if (sd == -1)
	{
		printf("unable to get socket!\n");
		close(fd);	
		exit(2);
	}

	if (setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &tr, sizeof(tr)) == -1)
	{
		printf("unable to setsockopt()\n");
		close(sd);
		close(fd);
		exit(2);
	}	 

	memset((char *)&localin, 0, sizeof(localin));	
	memset((char *)&remotein, 0, sizeof(remotein));

	localin.sin_port = port;
	localin.sin_addr.s_addr = INADDR_ANY;
	localin.sin_family = AF_INET;

	if (-1 == bind(sd, (struct sockaddr *)&localin, sizeof(localin)))
	{
		printf("unable to bind()\n");
		close(fd);	
		close(sd);	
		exit(2);
	}

	if (-1 == listen(sd, 5))
	{
		/* lol its like a girlfriend but different */
		printf("unable to listen()\n");
		close(fd);	
		close(sd);	
		exit(2);
	}

	while (1)
	{
		hostsd = accept(sd, (struct sockaddr *)&remotein, &socklen);

		if (hostsd == -1)
		{
			printf("unable to accept()\n");
			close(fd);	
			close(sd);	
			exit(2);
		}

		printf("connection received from %s\n", inet_ntoa(remotein.sin_addr));
		
		memset(inbuf, 0, sizeof(inbuf));
		readlen = read(hostsd, inbuf, sizeof(inbuf)-1);
		
		if ((readlen == -1) || (readlen == 0))
		{
			printf("nothing read from remote host!\n");
			close(hostsd);
			continue;
		}

		printf("request:\n%s\n", inbuf);
		
		memset(inbuf, 0, sizeof(inbuf));	
		printf("accept? Y/n: ");
		fgets(inbuf, sizeof(inbuf)-1, stdin);

		if (tolower(inbuf[0]) == 'n')
		{
			loopwrite(hostsd, http404, (ssize_t )strlen(http404));
			close(hostsd);
			continue;
		}
		
		
		memset(inbuf, 0, sizeof(inbuf));
		snprintf(inbuf, sizeof(inbuf)-1, http200, statbuf.st_size);
		if (-1 == loopwrite(hostsd, inbuf, (ssize_t )strlen(inbuf)))
		{
			close(hostsd);
			close(sd);
			close(fd);
			exit(2);
		}

		memset(inbuf, 0, sizeof(inbuf));
		lseek(fd, 0, SEEK_SET);
		while (readlen = read(fd, inbuf, sizeof(inbuf)))
		{
			if (readlen == -1)
			{
				printf("unable to read()\n");
				close(hostsd);
				close(sd);
				close(fd);
				exit(2);
			}
			if (-1 == loopwrite(hostsd, inbuf, readlen))
			{
				close(hostsd);
				close(sd);
				close(fd);
				exit(2);
			}	
		}
		close(hostsd);
	}
}

