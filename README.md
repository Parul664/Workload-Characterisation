
**This repository is part of B.Tech. Project.**

## Branches

**Master**

- Contains the codes for perf data generation and plot from cpu2006 benchmark, building and running the codes. 
- Codes for noise reduction in the data and phase detection.
- Contains the basic plugin tracelog for just producing dump of instructions of the application running on guest OS.


**xv6**

- Changes to the Operating system including insertion of marker instruction(nops here) on receiving -XOXO argument in exec system call.
- Plugin Tracelog modified to recognise these marker instructions and start the tracing. It would also take argument instruction interval of the application execution to print traces for.


**linux**

- Changes to the Operating System including insertion of marker instruction(int 100) on receiving -XOXO argument in exec system call.
- Changes to Qemu to handle this interrupt with interrupt no. 100.
- Plugin Tracelog modified to recognise these marker instructions and start the tracing. It would also take argument instruction interval of the application execution to print traces for.


**STEP 0 : Building the xv6 image**

Run make for xv6 which generates fs.img and xv6.img.


**STEP 1 : To configure Qemu**

`./configure --target-list="i386-softmmu,x86_64-softmmu" --enable-trace-backends=simple,dtrace,log,syslog,ftrace,nop --enable-debug-tcg --enable-gtk --enable-debug-info --enable-debug --enable-debug-stack-usage --disable-kvm --disable-xen `
`make -j4`

**STEP 2 : Generating object file for the plugin**

`cd contrib/plugins`
`make `

**STEP 3 : Running the plugin**

## To run only the plugin

`./qemu-system-x86_64 -drive file=../../xv6/fs.img,index=1,media=disk,format=raw -drive file=../../xv6/xv6.img,index=0,media=disk,format=raw -smp 1 -m 2048 -plugin ../contrib/plugins/libtracelog.so -d plugin,nochain --accel tcg,thread=single`


## To compare the plugin count obtained with the icount already present in the source code

-icount option enables counting the count of instructions, through which the softmmu/icount.c files output can be observed.

`./qemu-system-x86_64 -drive file=../../xv6/fs.img,index=1,media=disk,format=raw -drive file=../../xv6/xv6.img,index=0,media=disk,format=raw -smp 1 -m 2048 -plugin ../contrib/plugins/libtracelog.so -d plugin,nochain -icount shift=auto --accel tcg,thread=single`


## To print only the icount

`./qemu-system-x86_64 -drive file=../../xv6/fs.img,index=1,media=disk,format=raw -drive file=../../xv6/xv6.img,index=0,media=disk,format=raw -smp 1 -m 2048 -icount shift=auto`