/*
 * DRAM控制器初始化
 */

#include "common.h"
#define MEMCCMD		0x7e001004
#define P1REFRESH	0x7e001010
#define P1CASLAT	0x7e001014
#define MEM_SYS_CFG	0x7e00f120
#define P1MEMCFG	0x7e00100c
#define P1T_DQSS	0x7e001018
#define P1T_MRD		0x7e00101c
#define P1T_RAS		0x7e001020
#define P1T_RC		0x7e001024
#define P1T_RCD		0x7e001028
#define P1T_RFC		0x7e00102c
#define P1T_RP		0x7e001030
#define P1T_RRD		0x7e001034
#define P1T_WR		0x7e001038
#define P1T_WTR		0x7e00103c
#define P1T_XP		0x7e001040
#define P1T_XSR		0x7e001044
#define P1T_ESR		0x7e001048
#define P1MEMCFG2	0X7e00104c
#define P1_chip_0_cfg	0x7e001200

#define P1MEMSTAT	0x7e001000
#define P1MEMCCMD	0x7e001004
#define P1DIRECTCMD	0x7e001008

#define HCLK	133000000

#define nstoclk(ns)	( ns/(1000000000/HCLK)+1 )			// 纳秒转时钟周期

/*
 * 初始化DRAM控制器
 */
void sdram_init( void )
{
	// 使dramc进入config状态
	set_val(P1MEMCCMD, 0x4);

	// 设置timing参数和chip配置
	// 刷新周期
	set_val(P1REFRESH, nstoclk(7800));
	// 时间参数设置
	set_val( P1CASLAT, ( 3 << 1 ) );  					// CAS Latency=3
	set_val( P1T_DQSS, 0x1 );
	set_val( P1T_MRD, 0x2 );
	set_val( P1T_RAS, nstoclk(42) );
	set_val( P1T_RC, nstoclk(60) );
	u32 trcd = nstoclk( 18 );
	set_val( P1T_RCD, trcd | (( trcd - 3 ) << 3 ) );
	u32 trfc = nstoclk( 72 );
	set_val( P1T_RFC, trfc | ( ( trfc-3 ) << 5 ) );
	u32 trp = nstoclk( 18 );
	set_val( P1T_RP, trp | ( ( trp - 3 ) << 3 ) );
	set_val( P1T_RRD, nstoclk(12) );
	set_val( P1T_WR, nstoclk(12) );
	
	set_val( P1T_WTR, 0x1 );
	set_val( P1T_XP, 0x1 );
	set_val( P1T_XSR, nstoclk(120) );
	set_val( P1T_ESR, nstoclk(120) );
	
	// chip配置
	set_nbit( P1MEMCFG, 0, 3, 0x2 );  					// column address(10)
	set_nbit( P1MEMCFG, 3, 3, 0x3 );  					// row address(14)
	set_zero( P1MEMCFG, 6 );		  					// A10/AP
	set_nbit( P1MEMCFG, 15, 3, 0x2 ); 					// Burst Length
	set_nbit( P1MEMCFG2, 0, 4, 0x5 );
	set_2bit( P1MEMCFG2, 6, 0x1 );						// 32 bit
	set_nbit( P1MEMCFG2, 8, 3, 0x3 );					// Mobile DDR SDRAM
	set_2bit( P1MEMCFG2, 11, 0x1 );
	set_one( P1_chip_0_cfg, 16 );						// Bank-Row-Column organization

	// 初始化sdram
	set_val( P1DIRECTCMD, 0xc0000 ); 					// NOP
	set_val( P1DIRECTCMD, 0x000 );						// precharge
	set_val( P1DIRECTCMD, 0x40000 );					// auto refresh
	set_val( P1DIRECTCMD, 0x40000 );					// auto refresh
	set_val( P1DIRECTCMD, 0xa0000 ); 					// EMRS
	set_val( P1DIRECTCMD, 0x80032 ); 					// MRS

	set_val( MEM_SYS_CFG, 0x0 );
					
	// 使dramc进入ready状态
	set_val( P1MEMCCMD, 0x000 );
	while( !(( read_val( P1MEMSTAT ) & 0x3 ) == 0x1));	// 等待dramc进入ready状态
}



