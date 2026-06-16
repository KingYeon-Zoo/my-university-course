#define __LIBRARY__
#include <unistd.h>
#define __NR_dump_physical_mem 87
_syscall0(int, dump_physical_mem)
int main()
{
dump_physical_mem();
return 0;
}