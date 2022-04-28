#!/bin/bash

ITERATIONS=$1
ITERATIONS_STRING=$( printf '%d' $ITERATIONS )
C_FILE_NAME="./userCodeTest_$ITERATIONS.c"
C_COMMON_FILE="./userCodeTest.c"
rm $C_COMMON_FILE
if [ -f $C_FILE_NAME ] ; then
    echo "Copying from existing file"
    cp "$C_FILE_NAME" "$C_COMMON_FILE"
    exit 1
else
    echo "Creating new file ..."
    touch $C_FILE_NAME
fi



echo -e "#include \"types.h\"
#include \"stat.h\"
#include \"user.h\"\n
void addNops(void);\n
int main(){" > $C_FILE_NAME

echo "
    __asm__(
        \"movl   \$0x1,%edx\\n\"
        \"movl   \$0x3,%eax\\n\"" >> $C_FILE_NAME

i=0
while [ $i -lt $ITERATIONS ]
do
    echo "        \"add    %edx,%eax\\n\"
        \"add    %eax,%edx\\n\"" >> $C_FILE_NAME
    i=`expr $i + 1` 
done

echo -e "   );\n    addNops();\n    exit(); \n}\n" >> $C_FILE_NAME

echo "void addNops(){" >> $C_FILE_NAME

i=0
while [ $i -lt 997 ]
do 
    echo "  asm(\"nop\");" >> $C_FILE_NAME
    i=`expr $i + 1` 
done

echo "}" >> $C_FILE_NAME

cp "$C_FILE_NAME" "$C_COMMON_FILE"

