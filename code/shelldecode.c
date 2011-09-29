/*
 * SHELLCODE DECODER v0.0.0.0.0.0.0.0.0.0.0a
 * shellcode decoder: basically a _very_ simple disassembler
 * requires libdisasm to do heavy lifting
 * written by Brandon "drraid" Edwards, drraid@gmail.com
 * 
 * 
 * objdump won't observe a file without PE/Elf headers.. or 
 * if it does I was too frustrated to look up how to do it ...
 * so I wrote shelldecode.c ...
 * ..something which has likely been implemented 1000 times 
 * by everybody else in the world - I needed one and couldn't
 * find one on Google in 2 seconds...and since I knew using the 
 * disasm library would be simple, I wrote it ;].
 * 
 * requires: libdisasm, http://bastard.sourceforge.net/libdisasm.html
 *
 * compile: gcc shelldecode.c -o shelldecode -ldisasm
 * usage: ./shelldecode <file of raw binary>
 * 
 * serious props to drb of nops'r us
 * 
 * and as always, love for my crew SophSec 
 * 
*/

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <libdis.h>


int main(int argc, char *argv[])
{
	char line[128];
	struct stat sbuf;
	char *input = NULL;
	char *buf = NULL;
	FILE *fd = NULL;
	int ret = 0;
	int offset = 0;
	int size = 0;
	x86_insn_t x86dis;

	printf("\n[*] simple x86 shellcode disassembler\n");
	printf("[*] trivially implemented thanks 2 libdisasm!\n");
	printf("[*] written by drraid@gmail.com\n");

	input = argv[1];

	if (!argv[1])
	{
		printf("[*] usage: %s <shellcode as binary.file>\n", argv[0]);
		ret = 1;
		goto die;
	}

	memset((char *)&sbuf, 0, sizeof(sbuf));

	if (stat(input, &sbuf) == -1)
	{
		printf("[!] unable to stat %s!\n", input);
		ret = 1;
		goto die;
	}	

	buf = malloc(sbuf.st_size);

	if (!buf)
	{
		printf("[!] failed to allocate %u bytes!\n", sbuf.st_size);
		ret = 1;
		goto die;
	}

	fd = fopen(input, "r");

	if (!fd)
	{
		printf("[!] unable to open %s\n", input);
		ret = 1;
		goto die;
	}

	if (fread(buf, 1, sbuf.st_size, fd) != sbuf.st_size)
	{
		printf("[!] failed to read in %u bytes!\n", sbuf.st_size);
		ret = 1;
		goto die;
	}
	
	fclose(fd);	
	fd = NULL;

	printf("\n");

	x86_init(opt_none, NULL, NULL);

	while (offset < sbuf.st_size)
	{
		size = x86_disasm(buf, sbuf.st_size, 0, offset, &x86dis);

		if (!size)
		{
			printf("[!] invalid op at %i!\n", offset);
			break;
		}
		
		memset(line, 0, sizeof(line));
		x86_format_insn(&x86dis, line, sizeof(line), intel_syntax);	
		printf("%08X: %s\n", offset, line);
		offset += size;
	}

	x86_cleanup();

die:
	printf("\n");
	if (buf)
	{
		free(buf);
	}
	if (fd)
	{
		fclose(fd);
	}
		
	return ret;
}

