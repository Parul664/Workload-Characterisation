
**STEP 0 : Building the xv6 image**

Run make for xv6 which generates fs.img and xv6.img.


**STEP 1 : To configure Qemu**

`./configure --target-list="i386-softmmu,x86_64-softmmu" --enable-trace-backends=simple,dtrace,log,syslog,ftrace,nop --enable-debug-tcg --enable-gtk --enable-debug-info --enable-debug --enable-debug-stack-usage --disable-kvm --disable-xen `
`make -j4`

**STEP 2 : Generating object file for the plugin**

`cd contrib/plugins`
`make `

**STEP 3 : Running the plugin**

# To run only the plugin

`./qemu-system-x86_64 -drive file=../../xv6/fs.img,index=1,media=disk,format=raw -drive file=../../xv6/xv6.img,index=0,media=disk,format=raw -smp 1 -m 2048 -plugin ../contrib/plugins/libtracelog.so -d plugin,nochain --accel tcg,thread=single`


# To compare the plugin count obtained with the icount already present in the source code

-icount option enables counting the count of instructions, through which the softmmu/icount.c files output can be observed.

`./qemu-system-x86_64 -drive file=../../xv6/fs.img,index=1,media=disk,format=raw -drive file=../../xv6/xv6.img,index=0,media=disk,format=raw -smp 1 -m 2048 -plugin ../contrib/plugins/libtracelog.so -d plugin,nochain -icount shift=auto --accel tcg,thread=single`


# To print only the icount

`./qemu-system-x86_64 -drive file=../../xv6/fs.img,index=1,media=disk,format=raw -drive file=../../xv6/xv6.img,index=0,media=disk,format=raw -smp 1 -m 2048 -icount shift=auto`