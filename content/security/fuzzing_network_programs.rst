Tips for fuzzing network programs with AFL
##########################################

:date: 2017-05-07 15:00 +0530
:slug: afl-and-network-programs
:tags: AFL, fuzzing, preeny, security
:author: copyninja
:summary: Post provide tips on how to successfully fuzz network programs with
          AFL (American Fuzzy Lop)

Fuzzing is method of producing random malformed inputs for a software and
observe the software behavior. If a software crashes then there is a bug and it
can have security implications. Fuzzing has gained a lot of interest now a days,
especially with automated tools like American Fuzzy Lop (AFL) which can easily
help you to fuzz the program and record inputs which causes crash in the
software.

American Fuzzy Lop is a file based fuzzer which feeds input to program via
standard input. Using it with network program like server's or clients is not
possible in the original state. There is a `version
<https://github.com/jdbirdwell/afl>`_ of AFL with patches to allow it fuzz
network programs, but this patch is not merged upstream and I do not know if it
ever makes into upstream or not. Also the above repository contains version 1.9
which is older compared to currently released versions.

There is another method for fuzzing network program using AFL with help of
*LD_PRELOAD* tricks. `preeny <https://github.com/zardus/preeny>`_  is a project
which provides library which when used with LD_PRELOAD can desocket the network
program and make it read from *stdin*.

There is this best tutorial from `LoLWare
<https://lolware.net/2015/04/28/nginx-fuzzing.html>`_ which talks about fuzzing
Nginx with *preeny* and AFL. There is a best AFL workflow by `Foxglove Security
<https://foxglovesecurity.com/2016/03/15/fuzzing-workflows-a-fuzz-job-from-start-to-finish/>`_
which gives start to finish details about how to use AFL and its companion tool
to do fuzzing. So I'm not going to talk about any steps of fuzzing in this post
instead I'm going to list down my observations on changes that needs to be done
to get clean fuzzing with AFL and preeny.

1. desock.so provided by preeny works only with *read* and *write* (or rather
   other system call does not work with stdin) system calls and hence you need
   to make sure you replace any reference to *send*, *sendto*, *recv* and
   *recvfrom* with *read* and *write* system calls respectively. Without this
   change program will not read input provided by AFL on standard input.

2. If your network program is using forking or threading model make sure to
   remove all those and make it plain simple program which receives request and
   sends out response. Basically you are testing the ability of program to
   handle malformed input so we need very minimum logic to make program do what
   it is supposed to do when AFL runs it.

3. If you are using infinite loop like all normal programs replace the infinite
   loop with below mentioned AFL macro and use *afl-clang-fast* to compile it.
   This speeds up the testing as AFL will run the job `n` times before
   discarding the current fork and doing a fresh fork. After all fork is costly
   affair.


.. code-block:: c

   while(__AFL_LOOP(1000)) { // Change 1000 with iteration count
                // your logic here
   }

With above modification I could fuzz a server program talking binary protocol
and another one talking textual protocol. In both case I used *Wireshark*
capture to get the packet extract raw content and feed it as input to AFL.

I was successful in finding crashes which are exploitable in case of textual
protocol program than in binary protocol case. In case of binary protocol AFL
could not easily find new paths which probably is because of bad inputs I
provided. I will continue to do more experiment with binary protocol case and
provide my findings as new updates here.

If you have anything more to add do share with me :-). Happy fuzzing!.
