/* 
	BETA CODE FULL OF BUGGYNESS AND FAIL
	opfind.c by Brandon "drraid" Edwards
	drraid@gmail.com
	
	Inspired by Ryan Permeh's findjmp.c 
	Written to include jmp [reg+x] (Ryan's does not!)
	Note: does not find push reg; ret; (Ryan's does!)
	I might add that later. Proabably not.
	
	Big props to Ryan, one elite mofo!

	BTW: No implied warranty. No warranty at all. Don't run this.
	It's broken and it sucks. Don't run this. 
*/


#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>


/* lame opcode structure ;/ */
struct opcodez
{
	/* opcode itself */
    char *ops;

	/* byte length of op */
    size_t len;

	/* op expects more data */
    size_t followbytes;

	/* asm mnemonic of op */
    char *description;
};


/* all the opcodes */
struct opcodez allregs[]=
{
	{"\xd0",		1, 0, "call eax"},
	{"\xd1",		1, 0, "call ecx"},
	{"\xd2",		1, 0, "call edx"},
	{"\xd3",		1, 0, "call ebx"},
	{"\xd4",		1, 0, "call esp"},
	{"\xd5",		1, 0, "call ebp"},
	{"\xd6",		1, 0, "call esi"},
	{"\xd7",		1, 0, "call edi"},
	{"\x54\x24", 	2, 1, "call [esp"},
	{"\x50", 		1, 1, "call [eax"},
	{"\x53", 		1, 1, "call [ebx"},
	{"\x51",  		1, 1, "call [ecx"},
	{"\x52",		1, 1, "call [edx"},
	{"\x55", 		1, 1, "call [ebp"},
	{"\x56", 		1, 1, "call [esi"},
	{"\x57", 		1, 1, "call [edi"},
	{"\x94\x24", 	2, 4, "call [esp"},
	{"\x90",		1, 4, "call [eax"},
	{"\x93",		1, 4, "call [ebx"},
	{"\x91",		1, 4, "call [ecx"},
	{"\x92",		1, 4, "call [edx"},
	{"\x95",		1, 4, "call [ebp"},
	{"\x96",		1, 4, "call [esi"},
	{"\x97",		1, 4, "call [edi"},
	{"\xe0",		1, 0, "jmp  eax"},
	{"\xe3",		1, 0, "jmp  ebx"},
	{"\xe1",		1, 0, "jmp  ecx"},
	{"\xe2",		1, 0, "jmp  edx"},
	{"\xe4",		1, 0, "jmp  esp"},
	{"\xe5",		1, 0, "jmp  ebp"},
	{"\xe6",		1, 0, "jmp  esi"},
	{"\xe7",		1, 0, "jmp  edi"},
	{"\x64\x24", 	2, 1, "jmp  [esp"},
	{"\x65",		1, 1, "jmp  [ebp"},
	{"\x60",		1, 1, "jmp  [eax"},
	{"\x63",		1, 1, "jmp  [ebx"},
	{"\x61",		1, 1, "jmp  [ecx"},
	{"\x62",		1, 1, "jmp  [edx"},
	{"\x67",		1, 1, "jmp  [edi"},
	{"\x66",		1, 1, "jmp  [esi"},
	{"\xa4\x24", 	2, 4, "jmp  [esp"},
	{"\xa5",		1, 4, "jmp  [ebp"},
	{"\xa0",		1, 4, "jmp  [eax"}, 
	{"\xa3",		1, 4, "jmp  [ebx"},
	{"\xa1",		1, 4, "jmp  [ecx"},
	{"\xa2",		1, 4, "jmp  [edx"},
	{"\xa7",		1, 4, "jmp  [edi"},
	{"\xa6",		1, 4, "jmp  [esi"}
};

/* generic read loop function, shitty error management */
size_t readfd(int fdin, char *buf, size_t totalbytes)
{
	size_t readbytes = 0;
	ssize_t ret = 0;

	while (readbytes < totalbytes)
	{
		/* While we have space remaining.. read data */
		ret =  read(fdin,&buf[readbytes],(totalbytes - readbytes));

		/* fail = fail */
		if (ret == -1)
		{
			readbytes = 0;
			break;
		}

		/* 0 = done */
		if(ret == 0)
		{
			break;
		}
		readbytes += ret;
	}
	return readbytes;
}

/* checkop: s is the buffer of data to compare, 
   			len is how much we can haz
			buf is output buffer 
			returns true if an op was found */
int checkop(char *s, size_t len, char *buf)
{
	/* loop variable */
	size_t loop;

	/* max loop count */
	size_t max;

	/* 8bit value used by op */
	char byte;

	/* 32bit value used by op */
	int byte4;

	/* get our loop size */
	max = sizeof(allregs) / sizeof(allregs[0]);

	/* for each set of ops */
	for (loop = 0; loop < max; ++loop)
	{
		/* make sure there is enough data for this op */
		if (len < allregs[loop].len + allregs[loop].followbytes)
		{
			continue;
		}

		/* compare the ops for the len */
		if (0 == memcmp(s, allregs[loop].ops, allregs[loop].len))
		{
			/* check if the op uses the next 32 bits */
			if (allregs[loop].followbytes > 1)
			{
				memcpy((char *)&byte4, (s + allregs[loop].len), 4);
			}
			/* or if the op uses the next 8 bits */
			else if (allregs[loop].followbytes == 1)
			{
				/* get the byte */
				byte = *(s+allregs[loop].len);
				byte4 = byte;
			}
			
			/* lol sprintf for the insecurity win! */
			if (allregs[loop].followbytes)
			{
				sprintf(buf, "%s%s%i]",
						allregs[loop].description,
						byte4 < 0 ? "" : "+",
						byte4);
			}
			else
			{
				sprintf(buf, "%s", allregs[loop].description);
			}
			return 1;
		}
	}
	return 0;
}


/* 
	my computer science teacher said she will track me
	down and beat me senseless if i ever publish code
	without commenting every variable.
	i still have nightmares about it. 
*/
int main(int argc, char *argv[])
{
	/* buffer for reading in data */
	char buf[1024];
	
	/* "peek" buffer for edge cases */
	char peek[16];

	/* output string buffer */
	char out[128];

	/* byteff */
	char byteff = 0xff;

	/* file path to binary */
	char *path = NULL;

	/* file descriptor */
	int fd = 0;

	/* len we read in */
	size_t len = 0;

	/* how much we are peeking at */
	size_t peeklen = 0;
	
	/* offset is bad name.. 
	its really how many bytes total we've read */
	size_t offset = 0;

	/* lol this one *should* be named offset
	this is the offset in the file descriptor
	we use to restore the fd after peeking */
	off_t storedloc = 0;

	/* total count of opcodes found */
	size_t total = 0;

	/* array index loop variable for buf[] */
	size_t i = 0;

	/* used as a boolean truth for checkop() */
	int opfound = 0;



	/* the requisite tacky ascii art intro screen */
	printf("\n");
	printf("               ___ __           __ \n");
	printf(" .-----.-----.'  _|__|.-----.--|  |\n");
	printf(" |  _  |  _  |   _|  ||     |  _  |\n");
	printf(" |_____|   __|__| |__||__|__|_____|\n");
	printf("       |__|                        \n");
	printf("\n");
	printf("inspired by Ryan Permeh's findjmp\n");
	printf("finds both op reg && op reg[+-var]\n");
	printf("written by drraid@gmail.com\n\n");


	/* MOAR COMMENTZ PLZ! */
	path = argv[1];

	if (!path)
	{
		printf("usage: %s <path-to-binary>\n\n", argv[0]);
		exit(1);
	}

	printf("checking file: %s\n", path);

	/* open the file */
	fd = open(path, O_RDONLY);

	if (fd == -1)
	{
		printf("! failed to open %s\n", path);
		exit(1);
	}

	printf("* checking for %u different jmp/call ops\n\n", sizeof(allregs)/sizeof(allregs[0]));

	memset(buf, 0, sizeof(buf));
	
	offset = 0;
	len = 0;

	/* main loop */
	while ((len = readfd(fd, buf, sizeof(buf))))
	{
		/* for each byte in the buffer.. */
		for (i = 0; i < len; ++i)
		{
			/* if that byte == 0xff */
			if (buf[i] == byteff)
			{
				/*  check for edgecase: if ops begin at end of buffer 
					7 should really be dynamically determined..
					it represents the largest oplen + followbyte combo 
					7+1 since current byte is ff, we want next 7 bytes */
				/* the len == sizeof(buf) is to check if there is likely 
					more data in the file, since it should only be less
					than sizeof(buf) if the read for sizeof(buf) was short.. */
				if (i + 8 >= len && (len == sizeof(buf)))
				{
					/* peek: read and lseek back */
					memcpy(peek, &buf[i+1], len - i - 1);	
	
					/* store our current fd offset */	
					storedloc = lseek(fd, 0, SEEK_CUR);

					if (storedloc == (off_t)-1)
					{
						/* somebody gonna getta hurta realla bad */
						printf("! something's busted\n");
						close(fd);
						exit(1);
					}

					/* peek! */
					peeklen = readfd(fd, &peek[len - i - 1], sizeof(peek) - (len - i - 1));
	
					/* check for ops */
					if ((opfound = checkop(peek, (peeklen + (len - i - 1)), out)))
					{
						++total;
						printf("[@%08x] %s\n", offset + i, out);
					}	
					/* set the fd back to its old offset */
					lseek(fd, storedloc, SEEK_SET);
					continue;
				}
				/* check for ops */
				if ((opfound = checkop(&buf[i+1], (len - i - 1), out)))
				{
					++total;
					printf("[@%08x] %s\n", offset + i, out);
				}
			}	
		}
		offset += len;
		memset(buf, 0, sizeof(buf));
	}
	close(fd);
	printf("\n* %s:\n\t%u bytes\n\t%u opcode locations\n", path, offset, total);
	exit(0);
}


