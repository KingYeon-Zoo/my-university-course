; bootsect.s		(C) 1991 Linus Torvalds
;
;
; bootsect.s 被bios-启动子程序加载至 0x7c00 (31k)处，并将自己移到了地
; 址0x90000 (576k)处，并跳转至那里。 
;
; 它然后使用BIOS 中断将'setup'直接加载到自己的后面(0x90200)(576.5k)，
; 并将system 加载到地址0x10000 处。
;
; 注意! 目前的内核系统最大长度限制为(8*65536)(512k)字节，即使是在将来这也应该 
; 没有问题的。我想让它保持简单明了。这样512k 的最大内核长度应该足够了，
; 尤其是这里没有象 minix 中一样包含缓冲区高速缓冲。
;
; 加载程序已经做的够简单了，所以持续的读出错将导致死循环。只能手工重启。只要可能，
; 通过一次取取所有的扇区，加载过程可以做的很快的。
;
SYSSIZE equ 0x3000					; SYS_SIZE 是要加载的节数（16 字节为1 节）。0x3000 共为0x30000 字节=
									; 192 kB，对于当前的版本空间已足够了。
SETUPLEN equ 4						; setup 程序的扇区数
BOOTSEG  equ 0x07c0					; bootsect 的原始地址（是段地址，以下同）
INITSEG  equ 0x9000					; 将bootsect 移到这里
SETUPSEG equ 0x9020					; setup 程序从这里开始
SYSSEG   equ 0x1000					; system 模块加载到0x10000（64 kB）处
ENDSEG   equ SYSSEG + SYSSIZE		; 停止加载的段地址

; 根文件系统设备使用与引导时同样的软驱设备；
ROOT_DEV equ 0x301

[section .s16]
[BITS 16]
_start:
	mov	ax,BOOTSEG			; 将ds 段寄存器置为0x7C0
	mov	ds,ax
	mov	ax,INITSEG			; 将es 段寄存器置为0x9000
	mov	es,ax
	mov	cx,256				; 移动计数值=256 字
	sub	si,si
	sub	di,di
	rep 
	movsw
	jmp	INITSEG:go			;间接跳转。这里INITSEG 指出跳转到的段地址
	
; 从下面开始，CPU移动到0x90000 位置处的代码中执行。这段代码设置几个段寄存器，
; 包括栈寄存器ss 和sp。栈指针sp 只要指向远大于512 字节偏移（即地址 0x90200）
; 处都可以。 因为从0x90200 地址开始处还要放置setup 程序，而此时setup 程序大约
; 为4个扇区，因此sp 要指向大于（0x200 + 0x200 * 4 + 堆栈大小）处。实际上BIOS
; 把引导扇区加载到0x7c00 处并把执行权交给引导程序，ss = 0x00，sp = 0xfffe。


go:	mov	ax,cs
	mov	ds,ax
	mov	es,ax
	mov	ss,ax
	mov	sp,0xFF00		; 将堆栈指针sp 指向0x9ff00(即0x9000:0xff00)处
;
; 在 bootsect 程序块后紧跟着加载 setup模块的代码数据
; 注意es 已经设置好了。（在移动代码时es 已经指向目的段地址处0x9000）


; 【标号一】的用途是利用BIOS 中断INT 0x13 将setup 模块从磁盘第2 个扇区
; 开始读到0x90200 开始处，共读4 个扇区。如果读出错，则复位驱动器，并
; 重试，没有退路。
;
; INT 0x13 的使用方法如下：读扇区：
; ah = 0x02 - 读磁盘扇区到内存；al = 需要读出的扇区数量；
; ch = 磁道(柱面)号的低8 位； cl = 开始扇区(0-5 位)，磁道号高2 位(6-7)；
; dh = 磁头号； dl = 驱动器号（如果是硬盘则要置位7）；
; es:bx ->指向数据缓冲区； 如果出错则CF 标志置位。
load_setup:  
	mov	dx,0x0000		
	mov	cx,0x0002	
	mov	bx,0x0200		
	mov	ax,0x0200+SETUPLEN	
	int	0x13			;【标号一】		
	jnc	ok_load_setup	; 读取成功
	mov	dx,0x0000
	mov	ax,0x0000		; 读取失败，重试
	int	0x13
	jmp	load_setup

ok_load_setup:

; 取磁盘驱动器的参数，特别是每道的扇区数量。
;
; INT 0x13 调用格式和返回信息如下：
; ah = 0x08 dl = 驱动器号（如果是硬盘则要置位7 为1）。
; 返回信息：
; 如果出错则CF 置位，并且ah = 状态码。
; ah = 0， al = 0， bl = 驱动器类型（AT/PS2）
; ch = 最大磁道号的低8 位，cl = 每磁道最大扇区数(位0-5)，最大磁道号高2 位(位6-7)
; dh = 最大磁头数， dl = 驱动器数量，
; es:di -> 软驱磁盘参数表。

	mov	dl,0x00
	mov	ax,0x0800		
	int	0x13
	mov	ch,0x00
;	seg cs						; 本条语句可要，也可以不要，因为本程序的所有段都在同一个段中。
	mov	[sectors],cx			; 保存每磁道扇区数
	mov	ax,INITSEG				; 因为上面去磁盘参数以改变es 的值，故重新赋值
	mov	es,ax


	mov	ah,0x03		
	xor	bh,bh
	int	0x10					; 读光标位置
	
	mov	cx,24
	mov	bx,0x0007	
	mov	bp,msg1
	mov	ax,0x1301		
	int	0x10					; 输出字符串

; 现在开始将system 模块加载到0x10000(64k)处

	mov	ax,SYSSEG
	mov	es,ax					; es = 存放system 的段地址
	call	read_it				; 读磁盘上system 模块，es 为输入参数
	call	kill_motor			; 关闭驱动器马达，这样就可以知道驱动器的状态了


; 此后，我们检查要使用哪个根文件系统设备（简称根设备）。如果已经指定了设备(!=0)
; 就直接使用给定的设备。否则就需要根据BIOS 报告的每磁道扇区数来
; 确定到底使用/dev/PS0 (2,28) 还是 /dev/at0 (2,8)。
; 上面一行中两个设备文件的含义：
; 在Linux 中软驱的主设备号是2，次设备号 = type*4 + nr，其中 nr 为0-3 分别对应
; 软驱A、B、C 或D；type 是软驱的类型（2->1.2M 或7->1.44M 等）。
; 因为7*4 + 0 = 28，所以 /dev/PS0 (2,28)指的是1.44M A 驱动器,其设备号是0x021c
; 同理 /dev/at0 (2,8)指的是1.2M A 驱动器，其设备号是0x0208。

;	seg cs
	mov	ax,[root_dev]		; 去508,509字节处的根设备号并判断是否已被定义
	cmp	ax,0
	jne	root_defined
;	seg cs
; 取上面保存的每磁道扇区数。如果sectors=15
; 则说明是1.2Mb 的驱动器；如果sectors=18，则说明是
; 1.44Mb 软驱。因为是可引导的驱动器，所以肯定是A 驱。
	mov	bx,[sectors]
	mov	ax,0x0208		; /dev/ps0 - 1.2Mb
	cmp	bx,15
	je	root_defined	; 如果等于，则ax 中就是引导驱动器的设备号
	mov	ax,0x021c		; /dev/PS0 - 1.44Mb
	cmp	bx,18
	je	root_defined	; 如果都不一样，则死循环（死机)
undef_root:
	jmp undef_root		
root_defined:
;	seg cs
	mov	[root_dev],ax	; 将检查过的设备号保存起来

;
; 到此，所有程序都加载完毕，我们就跳转到被加载在bootsect 后面的setup 程序去。

	jmp	SETUPSEG:0

; 该子程序将系统模块加载到内存地址0x10000 处，并确定没有跨越64KB 的内存
; 边界。我们试图尽快地进行加载，只要可能，就每次加载整条磁道的数据。
;
; 输入：es – 开始内存地址段值（通常是0x1000）
;
sread:	dw 1+SETUPLEN	; 当前磁道中已读的扇区数
head:	dw 0			; 当前磁头号
track:	dw 0			; 当前磁道号

read_it:
; 测试输入的段值。必须位于内存地址64KB 边界处，否则进入死循环。清bx 寄存器，
; 用于表示当前段内存放数据的开始位置。
	mov ax,es
	test ax,0x0fff
die:	jne die			; es 值必须位于64KB 地址边界
	xor bx,bx			; bx 为段内偏移位置
rp_read:
	mov ax,es
	cmp ax,ENDSEG		; 是否已经加载了全部数据？
	jb ok1_read
	ret
ok1_read:
; 计算和验证当前磁道需要读取的扇区数，放在ax 寄存器中。
; 根据当前磁道还未读取的扇区数以及段内数据字节开始偏移位置，计算如果全部读取这些未读扇区，所
; 读总字节数是否会超过64KB 段长度的限制。若会超过，则根据此次最多能读入的字节数(64KB – 段内
; 偏移位置)，反算出此次需要读取的扇区数。
	mov ax,[sectors]	; 取每磁道扇区数
	sub ax,[sread]		; 减去当前磁道已读扇区数
	mov cx,ax
	shl cx,9			; cx = cx * 512 字节。
	add cx,bx			; cx = cx + 段内当前偏移值(bx)
	jnc ok2_read		; 若没有超过64KB 字节，则跳转至ok2_read 处执行
	je ok2_read
	xor ax,ax			; 若加上此次将读磁道上所有未读扇区时会超过64KB，则计算
	sub ax,bx			; 此时最多能读入的字节数(64KB – 段内读偏移位置)，再转换
	shr ax,9			; 成需要读取的扇区数
ok2_read:
	call read_track
	mov cx,ax			; cx = 该次操作已读取的扇区数
	add ax,[sread]		; 当前磁道上已经读取的扇区数
;	seg cs
	cmp ax,[sectors]
	jne ok3_read		; 如果当前磁道上的还有扇区未读，则跳转到ok3_read 处
	mov ax,1
	sub ax,[head]		
	jne ok4_read		; 如果是0 磁头，则再去读1 磁头面上的扇区数据
	inc word [track]	; 否则去读下一磁道
ok4_read:
	mov [head],ax		; 保存当前磁头号
	xor ax,ax			; 清当前磁道已读扇区数
ok3_read:
	mov [sread],ax		; 保存当前磁道已读扇区数
	shl cx,9			; 上次已读扇区数*512 字节
	add bx,cx			; 调整当前段内数据开始位置
	jnc rp_read			; 若小于64KB 边界值，则跳转到rp_read处，继续读数据。! 否则调整当前段，为读下一段数据作准备。
	mov ax,es
	add ax,0x1000		; 将段基址调整为指向下一个64KB 段内存
	mov es,ax
	xor bx,bx
	jmp rp_read			; 跳转至rp_read处，继续读数据

; 读当前磁道上指定开始扇区和需读扇区数的数据到es:bx 开始处。
; int 0x13，ah=2 的说明。
; al – 需读扇区数；es:bx – 缓冲区开始位置。

read_track:
	push ax
	push bx
	push cx
	push dx
	mov dx,[track]		; 取当前磁道号
	mov cx,[sread]		; 取当前磁道上已读扇区数
	inc cx				; cl = 开始读扇区
	mov ch,dl			; ch = 当前磁道号
	mov dx,[head]		; 取当前磁头号
	mov dh,dl			; dh = 磁头号
	mov dl,0			; dl = 驱动器号(为0 表示当前驱动器)
	and dx,0x0100		; 磁头号不大于1
	mov ah,2			; ah = 2，读磁盘扇区功能号
	int 0x13
	jc bad_rt			; 若出错，则跳转至bad_rt
	pop dx
	pop cx
	pop bx
	pop ax
	ret
; 执行驱动器复位操作
bad_rt:	mov ax,0
	mov dx,0
	int 0x13
	pop dx
	pop cx
	pop bx
	pop ax
	jmp read_track

; 这个子程序用于关闭软驱的马达，这样我们进入内核后它处于已知状态，以后也就无须担心它了
kill_motor:
	push dx
	mov dx,0x3f2
	mov al,0
	out dx,ax
	pop dx
	ret

sectors:
	dw 0

msg1:
	db 13,10
	db "Loading system ..."
	db 13,10,13,10

times 	508-($-$$)	db	0	
root_dev:
	dw ROOT_DEV
boot_flag:
	dw 0xAA55

