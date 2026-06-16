#define ELFIN_NAND_BASE		0x70200000

#define NFCONF_OFFSET           0x00
#define NFCONT_OFFSET           0x04
#define NFCMMD_OFFSET           0x08
#define NFADDR_OFFSET           0x0c
#define NFDATA_OFFSET			0x10
#define NFMECCDATA0_OFFSET      0x14
#define NFMECCDATA1_OFFSET      0x18
#define NFSECCDATA0_OFFSET      0x1c
#define NFSBLK_OFFSET           0x20
#define NFEBLK_OFFSET           0x24
#define NFSTAT_OFFSET           0x28
#define NFESTAT0_OFFSET         0x2c
#define NFESTAT1_OFFSET         0x30
#define NFMECC0_OFFSET          0x34
#define NFMECC1_OFFSET          0x38
#define NFSECC_OFFSET           0x3c
#define NFMLCBITPT_OFFSET       0x40
#define NF8ECCERR0_OFFSET		0x44
#define NF8ECCERR1_OFFSET		0x48
#define NF8ECCERR2_OFFSET		0x4c
#define NFM8ECC0_OFFSET			0x50
#define NFM8ECC1_OFFSET			0x54
#define NFM8ECC2_OFFSET			0x58
#define NFM8ECC3_OFFSET			0x5c
#define NFMLC8BITPT0_OFFSET		0x60
#define NFMLC8BITPT1_OFFSET		0x64

#define NFCONF				(ELFIN_NAND_BASE+NFCONF_OFFSET)
#define NFCONT				(ELFIN_NAND_BASE+NFCONT_OFFSET)
#define NFCMMD				(ELFIN_NAND_BASE+NFCMMD_OFFSET)
#define NFADDR           	(ELFIN_NAND_BASE+NFADDR_OFFSET)
#define NFDATA          	(ELFIN_NAND_BASE+NFDATA_OFFSET)
#define NFMECCDATA0     	(ELFIN_NAND_BASE+NFMECCDATA0_OFFSET)
#define NFMECCDATA1     	(ELFIN_NAND_BASE+NFMECCDATA1_OFFSET)
#define NFSECCDATA0      	(ELFIN_NAND_BASE+NFSECCDATA0_OFFSET)
#define NFSBLK          	(ELFIN_NAND_BASE+NFSBLK_OFFSET)
#define NFEBLK           	(ELFIN_NAND_BASE+NFEBLK_OFFSET)
#define NFSTAT           	(ELFIN_NAND_BASE+NFSTAT_OFFSET)
#define NFESTAT0         	(ELFIN_NAND_BASE+NFESTAT0_OFFSET)
#define NFESTAT1         	(ELFIN_NAND_BASE+NFESTAT1_OFFSET)
#define NFMECC0          	(ELFIN_NAND_BASE+NFMECC0_OFFSET)
#define NFMECC1          	(ELFIN_NAND_BASE+NFMECC1_OFFSET)
#define NFSECC           	(ELFIN_NAND_BASE+NFSECC_OFFSET)
#define NFMLCBITPT          (ELFIN_NAND_BASE+NFMLCBITPT_OFFSET)
#define NF8ECCERR0			(ELFIN_NAND_BASE+NF8ECCERR0_OFFSET)
#define NF8ECCERR1			(ELFIN_NAND_BASE+NF8ECCERR1_OFFSET)
#define NF8ECCERR2			(ELFIN_NAND_BASE+NF8ECCERR2_OFFSET)
#define NFM8ECC0			(ELFIN_NAND_BASE+NFM8ECC0_OFFSET)
#define NFM8ECC1			(ELFIN_NAND_BASE+NFM8ECC1_OFFSET)
#define NFM8ECC2			(ELFIN_NAND_BASE+NFM8ECC2_OFFSET)
#define NFM8ECC3			(ELFIN_NAND_BASE+NFM8ECC3_OFFSET)
#define NFMLC8BITPT0		(ELFIN_NAND_BASE+NFMLC8BITPT0_OFFSET)
#define NFMLC8BITPT1		(ELFIN_NAND_BASE+NFMLC8BITPT1_OFFSET)

#define __REG(x)				(*(volatile unsigned long *)(x))
#define __REGb(x)				(*(volatile unsigned char *)(x))
#define NFCONF_REG				__REG(ELFIN_NAND_BASE+NFCONF_OFFSET)
#define NFCONT_REG				__REG(ELFIN_NAND_BASE+NFCONT_OFFSET)
#define NFCMD_REG				__REG(ELFIN_NAND_BASE+NFCMMD_OFFSET)
#define NFADDR_REG           	__REG(ELFIN_NAND_BASE+NFADDR_OFFSET)
#define NFDATA_REG          	__REG(ELFIN_NAND_BASE+NFDATA_OFFSET)
#define NFDATA8_REG          	__REGb(ELFIN_NAND_BASE+NFDATA_OFFSET)
#define NFMECCDATA0_REG     	__REG(ELFIN_NAND_BASE+NFMECCDATA0_OFFSET)
#define NFMECCDATA1_REG     	__REG(ELFIN_NAND_BASE+NFMECCDATA1_OFFSET)
#define NFSECCDATA0_REG      	__REG(ELFIN_NAND_BASE+NFSECCDATA0_OFFSET)
#define NFSBLK_REG          	__REG(ELFIN_NAND_BASE+NFSBLK_OFFSET)
#define NFEBLK_REG           	__REG(ELFIN_NAND_BASE+NFEBLK_OFFSET)
#define NFSTAT_REG           	__REG(ELFIN_NAND_BASE+NFSTAT_OFFSET)
#define NFESTAT0_REG         	__REG(ELFIN_NAND_BASE+NFESTAT0_OFFSET)
#define NFESTAT1_REG         	__REG(ELFIN_NAND_BASE+NFESTAT1_OFFSET)
#define NFMECC0_REG          	__REG(ELFIN_NAND_BASE+NFMECC0_OFFSET)
#define NFMECC1_REG          	__REG(ELFIN_NAND_BASE+NFMECC1_OFFSET)
#define NFSECC_REG           	__REG(ELFIN_NAND_BASE+NFSECC_OFFSET)
#define NFMLCBITPT_REG         	__REG(ELFIN_NAND_BASE+NFMLCBITPT_OFFSET)

#define NAND_DISABLE_CE()	(NFCONT_REG |= (1 << 1))
#define NAND_ENABLE_CE()	(NFCONT_REG &= ~(1 << 1))
#define NF_TRANSRnB()		do { while(!(NFSTAT_REG & (1 << 0))); } while(0)


// Standard NAND flash commands
#define NAND_CMD_READ0		0
#define NAND_CMD_READ1		1
#define NAND_CMD_RNDOUT		5
#define NAND_CMD_PAGEPROG	0x10
#define NAND_CMD_READOOB	0x50
#define NAND_CMD_ERASE1		0x60
#define NAND_CMD_STATUS		0x70
#define NAND_CMD_STATUS_MULTI	0x71
#define NAND_CMD_SEQIN		0x80
#define NAND_CMD_RNDIN		0x85
#define NAND_CMD_READID		0x90
#define NAND_CMD_ERASE2		0xd0
#define NAND_CMD_RESET		0xff
// Extended commands for large page devices
#define NAND_CMD_READSTART	0x30
#define NAND_CMD_RNDOUTSTART	0xE0
#define NAND_CMD_CACHEDPROG	0x15



#define MEM_SYS_CFG     (*((volatile unsigned long *)0x7E00F120))
void nand_init(void)
{
	/* 让xm0csn2用作nand flash cs0 片选引脚 */
	MEM_SYS_CFG = 0xd;

	/* 设置时间参数 */
	NFCONF_REG |= ( (0x77<<8)|(0x7<<4) );
	NFCONT_REG |= (0x3<<0);

}



// 读一页:2048byte
static int nandll_read_page (unsigned char *buf, unsigned long addr, int large_block)
{

	int i;
	int page_size = 512;

	if (large_block)
		page_size = 2048;

	NAND_ENABLE_CE();

	NFCMD_REG = NAND_CMD_READ0;

	/* Write Address */
	NFADDR_REG = 0;

	if (large_block)
		NFADDR_REG = 0;

	NFADDR_REG = (addr) & 0xff;
	NFADDR_REG = (addr >> 8) & 0xff;
	NFADDR_REG = (addr >> 16) & 0xff;

	if (large_block)
		NFCMD_REG = NAND_CMD_READSTART;

	NF_TRANSRnB();

	/* for compatibility(2460). u32 cannot be used. by scsuh */
	for(i=0; i < page_size; i++) {
		*buf++ = NFDATA8_REG;
	}

	NAND_DISABLE_CE();

	//led_blink();
	return 0;
}

// Read data from NAND.
static int nandll_read_blocks (unsigned long dst_addr, unsigned long size, int large_block)
{
	unsigned char *buf = (unsigned char *)dst_addr;
	int i;
	unsigned int page_shift = 9;

	if (large_block)
		page_shift = 11;

	/* Read pages */
	for (i = 0; i < (size>>page_shift); i++, buf+=(1<<page_shift))
	{
		nandll_read_page(buf, i, large_block);
	}

	return 0;
}


int copy2ddr(unsigned int nand_start, unsigned int ddr_start, unsigned int len)
{
	nand_init();

	int large_block = 0;
	int i;
	volatile unsigned char id;

	NAND_ENABLE_CE();
	NFCMD_REG = NAND_CMD_READID;
	NFADDR_REG =  0x00;

	/* wait for a while */
	for (i=0; i<200; i++);
	id = NFDATA8_REG;
	id = NFDATA8_REG;

	if (id > 0x80)
	{
		large_block = 1;
		len = (len/2048+1)*2048;
	}
	else
	{
		len = (len/512+1)*512;
	}

	// ddr_start:目的，链接地址
	// 大小:64K
	return nandll_read_blocks(ddr_start, len, large_block);
}

