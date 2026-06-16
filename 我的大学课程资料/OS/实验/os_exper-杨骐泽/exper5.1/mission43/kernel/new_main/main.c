#define __LIBRARY__ 
#include <stdio.h> 
#include <unistd.h> 
int main(int argc, char * argv[]) 
{ 
	int pid; 
	printf("PID:%d parent process start.\n", getpid()); 
	pid = fork(); 
	if( pid != 0 ) 
	{ 
	wait(NULL);
	printf("PID:%d parent process continue.\n", getpid()); 
	} 
	else 
	{ 
	printf("PID:%d child process start.\n", getpid()); 
	printf("PID:%d child process exit.\n", getpid()); 
	return 0; 
	} 
	printf("PID:%d parent process exit.\n", getpid()); 
	return 0; 
}
