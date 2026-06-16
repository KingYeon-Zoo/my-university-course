extern int sys_setup ();		// 系统启动初始化设置函数。 (kernel/blk_drv/hd.c)
extern int sys_exit ();			// 程序退出。 (kernel/exit.c)
extern int sys_fork ();			// 创建进程。 (kernel/system_call.s)
extern int sys_read ();			// 读文件。 (fs/read_write.c)
extern int sys_write ();		// 写文件。 (fs/read_write.c)
extern int sys_open ();			// 打开文件。 (fs/open.c)
extern int sys_close ();		// 关闭文件。 (fs/open.c)
extern int sys_waitpid ();		// 等待进程终止。 (kernel/exit.c)
extern int sys_creat ();		// 创建文件。 (fs/open.c)
extern int sys_link ();			// 创建一个文件的硬连接。 (fs/namei.c)
extern int sys_unlink ();		// 删除一个文件名(或删除文件)。 (fs/namei.c)
extern int sys_execve ();		// 执行程序。 (kernel/system_call.s)
extern int sys_chdir ();		// 更改当前目录。 (fs/open.c)
extern int sys_time ();			// 取当前时间。 (kernel/sys.c)
extern int sys_mknod ();		// 建立块/字符特殊文件。 (fs/namei.c)
extern int sys_chmod ();		// 修改文件属性。 (fs/open.c)
extern int sys_chown ();		// 修改文件宿主和所属组。 (fs/open.c)
extern int sys_break ();		// (-kernel/sys.c)
extern int sys_stat ();			// 使用路径名取文件的状态信息。 (fs/stat.c)
extern int sys_lseek ();		// 重新定位读/写文件偏移。 (fs/read_write.c)
extern int sys_getpid ();		// 取进程id。 (kernel/sched.c)
extern int sys_mount ();		// 安装文件系统。 (fs/super.c)
extern int sys_umount ();		// 卸载文件系统。 (fs/super.c)
extern int sys_setuid ();		// 设置进程用户id。 (kernel/sys.c)
extern int sys_getuid ();		// 取进程用户id。 (kernel/sched.c)
extern int sys_stime ();		// 设置系统时间日期。 (-kernel/sys.c)
extern int sys_ptrace ();		// 程序调试。 (-kernel/sys.c)
extern int sys_alarm ();		// 设置报警。 (kernel/sched.c)
extern int sys_fstat ();		// 使用文件句柄取文件的状态信息。(fs/stat.c)
extern int sys_pause ();		// 暂停进程运行。 (kernel/sched.c)
extern int sys_utime ();		// 改变文件的访问和修改时间。 (fs/open.c)
extern int sys_stty ();			// 修改终端行设置。 (-kernel/sys.c)
extern int sys_gtty ();			// 取终端行设置信息。 (-kernel/sys.c)
extern int sys_access ();		// 检查用户对一个文件的访问权限。(fs/open.c)
extern int sys_nice ();			// 设置进程执行优先权。 (kernel/sched.c)
extern int sys_ftime ();		// 取日期和时间。 (-kernel/sys.c)
extern int sys_sync ();			// 同步高速缓冲与设备中数据。 (fs/buffer.c)
extern int sys_kill ();			// 终止一个进程。 (kernel/exit.c)
extern int sys_rename ();		// 更改文件名。 (-kernel/sys.c)
extern int sys_mkdir ();		// 创建目录。 (fs/namei.c)
extern int sys_rmdir ();		// 删除目录。 (fs/namei.c)
extern int sys_dup ();			// 复制文件句柄。 (fs/fcntl.c)
extern int sys_pipe ();			// 创建管道。 (fs/pipe.c)
extern int sys_times ();		// 取运行时间。 (kernel/sys.c)
extern int sys_prof ();			// 程序执行时间区域。 (-kernel/sys.c)
extern int sys_brk ();			// 修改数据段长度。 (kernel/sys.c)
extern int sys_setgid ();		// 设置进程组id。 (kernel/sys.c)
extern int sys_getgid ();		// 取进程组id。 (kernel/sched.c)
extern int sys_signal ();		// 信号处理。 (kernel/signal.c)
extern int sys_geteuid ();		// 取进程有效用户id。 (kenrl/sched.c)
extern int sys_getegid ();		// 取进程有效组id。 (kenrl/sched.c)
extern int sys_acct ();			// 进程记帐。 (-kernel/sys.c)
extern int sys_phys ();			// (-kernel/sys.c)
extern int sys_lock ();			// (-kernel/sys.c)
extern int sys_ioctl ();		// 设备控制。 (fs/ioctl.c)
extern int sys_fcntl ();		// 文件句柄操作。 (fs/fcntl.c)
extern int sys_mpx ();			// (-kernel/sys.c)
extern int sys_setpgid ();		// 设置进程组id。 (kernel/sys.c)
extern int sys_ulimit ();		// (-kernel/sys.c)
extern int sys_uname ();		// 显示系统信息。 (kernel/sys.c)
extern int sys_umask ();		// 取默认文件创建属性码。 (kernel/sys.c)
extern int sys_chroot ();		// 改变根系统。 (fs/open.c)
extern int sys_ustat ();		// 取文件系统信息。 (fs/open.c)
extern int sys_dup2 ();			// 复制文件句柄。 (fs/fcntl.c)
extern int sys_getppid ();		// 取父进程id。 (kernel/sched.c)
extern int sys_getpgrp ();		// 取进程组id，等于getpgid(0)。(kernel/sys.c)
extern int sys_setsid ();		// 在新会话中运行程序。 (kernel/sys.c)
extern int sys_sigaction ();	// 改变信号处理过程。 (kernel/signal.c)
extern int sys_sgetmask ();		// 取信号屏蔽码。 (kernel/signal.c)
extern int sys_ssetmask ();		// 设置信号屏蔽码。 (kernel/signal.c)
extern int sys_setreuid ();		// 设置真实与/或有效用户id。 (kernel/sys.c)
extern int sys_setregid ();		// 设置真实与/或有效组id。 (kernel/sys.c)
extern int sys_sigpending();
extern int sys_sigsuspend();
extern int sys_sethostname();
extern int sys_setrlimit();
extern int sys_getrlimit();
extern int sys_getrusage();
extern int sys_gettimeofday();
extern int sys_settimeofday();
extern int sys_getgroups();
extern int sys_setgroups();
extern int sys_select();
extern int sys_symlink();
extern int sys_lstat();
extern int sys_readlink();
extern int sys_uselib();
// 系统调用函数指针表。用于系统调用中断处理程序(int 0x80)，作为跳转表。
// 数组元素为系统调用内核函数的函数指针，索引即系统调用号
fn_ptr sys_call_table[] = { 
sys_setup,			//0 
sys_exit,           //1   
sys_fork,           //2
sys_read,           //3
sys_write,          //4
sys_open,           //5
sys_close,          //6
sys_waitpid,        //7
sys_creat,          //8
sys_link,           //9
sys_unlink,         //10 
sys_execve,         //11
sys_chdir,          //12
sys_time,           //13
sys_mknod,          //14
sys_chmod,          //15 
sys_chown,          //16 
sys_break,          //17
sys_stat,           //18
sys_lseek,          //19
sys_getpid,         //20
sys_mount,          //21
sys_umount,         //22 
sys_setuid,         //23
sys_getuid,         //24
sys_stime,          //25
sys_ptrace,         //26
sys_alarm,          //27
sys_fstat,          //28 
sys_pause,          //29
sys_utime,          //30
sys_stty,           //31
sys_gtty,           //32 
sys_access,         //33
sys_nice,           //34
sys_ftime,          //35
sys_sync,           //36
sys_kill,           //37
sys_rename,         //38
sys_mkdir,          //39
sys_rmdir,          //40
sys_dup,            //41   
sys_pipe,           //42
sys_times,          //43
sys_prof,           //44
sys_brk,            //45
sys_setgid,         //46
sys_getgid,         //47
sys_signal,         //48
sys_geteuid,        //49
sys_getegid,        //50
sys_acct,           //51
sys_phys,           //52
sys_lock,           //53
sys_ioctl,          //54
sys_fcntl,          //55
sys_mpx,            //56
sys_setpgid,        //57
sys_ulimit,         //58
sys_uname,          //59
sys_umask,          //60
sys_chroot,         //61
sys_ustat,          //62
sys_dup2,           //63
sys_getppid,        //64
sys_getpgrp,        //65
sys_setsid,         //66
sys_sigaction,      //67
sys_sgetmask,       //68
sys_ssetmask,       //69
sys_setreuid,       //70
sys_setregid,       //71
sys_sigsuspend, 	//72
sys_sigpending, 	//73
sys_sethostname,	//74
sys_setrlimit, 		//75
sys_getrlimit, 		//76
sys_getrusage, 		//77
sys_gettimeofday,	//78 
sys_settimeofday, 	//79
sys_getgroups, 		//80
sys_setgroups, 		//81
sys_select, 		//82
sys_symlink,		//83
sys_lstat, 			//84
sys_readlink, 		//85
sys_uselib 			//86 
};
