#define __LIBRARY__
#include "linuxapp.h"

#include<sys/wait.h>
#include<linux/sched.h>
#include<time.h>
void cpuio_bound( int last, int cpu_time, int io_time )
{
struct tms start_time, current_time;
clock_t utime, stime;
int sleep_time;
while( last>0 )
{
times( &start_time );
do
{
times( &current_time );
utime=current_time.tms_utime-start_time.tms_utime;
stime=current_time.tms_stime-start_time.tms_stime;
}while( ( ( utime+stime )/HZ )< cpu_time );
last-=cpu_time;
if( last<=0 )
break;
sleep_time=0;
while( sleep_time<io_time )
{
sleep( 1 );
sleep_time++;
}
last-=sleep_time;
}
}

int main( int argc, char * argv[] )
{
pid_t p1, p2, p3, p4;
if( ( p1=fork() )==0 )
{ printf( "in child1\n" ); cpuio_bound( 5, 2, 2 );}
else if( ( p2=fork() )==0 )
{ printf( "in child2\n" ); cpuio_bound( 5, 4, 0 );}
else if( ( p3=fork() )==0 )
{ printf( "in child3\n" ); cpuio_bound( 5, 0, 4 );}
else if( ( p4=fork() )==0 )
{ printf( "in child4\n" ); cpuio_bound( 4, 2, 2 );}
else
{
printf( "========This is parent process=======\n" );
printf( "pid=%d\n", getpid() );
printf( "pid1=%d\n", p1 );
printf( "pid2=%d\n", p2 );
printf( "pid3=%d\n", p3 );
printf( "pid4=%d\n", p4 );
}
wait( NULL );
return 0;
}