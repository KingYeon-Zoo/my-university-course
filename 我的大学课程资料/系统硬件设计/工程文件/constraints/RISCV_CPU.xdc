################################################################################
# EGO1 (XC7A35T-CSG324-1) Minimal Constraints
# Top: aclk, aresetn, debug_pc[31:0]
################################################################################

# ---- Board recommended config ----
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]

# ---- 100MHz system clock (SYS_CLK) ----
set_property PACKAGE_PIN P17 [get_ports sys_clk]
set_property IOSTANDARD LVCMOS33 [get_ports sys_clk]
create_clock -name aclk -period 10.000 [get_ports sys_clk]

# ---- Reset button (FPGA_RESET) ----
set_property PACKAGE_PIN P15 [get_ports aresetn]
set_property IOSTANDARD LVCMOS33 [get_ports aresetn]
# 可选：默认上拉，按下为低（如果你发现逻辑相反，再去掉或改 PULLDOWN）
set_property PULLUP true [get_ports aresetn]

# ---- debug_pc[31:0] -> J5 通用扩展IO 32 pins ----
set_property IOSTANDARD LVCMOS33 [get_ports {debug_pc[*]}]

set_property PACKAGE_PIN B16 [get_ports {debug_pc[0]}]
set_property PACKAGE_PIN B17 [get_ports {debug_pc[1]}]
set_property PACKAGE_PIN A15 [get_ports {debug_pc[2]}]
set_property PACKAGE_PIN A16 [get_ports {debug_pc[3]}]
set_property PACKAGE_PIN A13 [get_ports {debug_pc[4]}]
set_property PACKAGE_PIN A14 [get_ports {debug_pc[5]}]
set_property PACKAGE_PIN B18 [get_ports {debug_pc[6]}]
set_property PACKAGE_PIN A18 [get_ports {debug_pc[7]}]
set_property PACKAGE_PIN F13 [get_ports {debug_pc[8]}]
set_property PACKAGE_PIN F14 [get_ports {debug_pc[9]}]
set_property PACKAGE_PIN B13 [get_ports {debug_pc[10]}]
set_property PACKAGE_PIN B14 [get_ports {debug_pc[11]}]
set_property PACKAGE_PIN D14 [get_ports {debug_pc[12]}]
set_property PACKAGE_PIN C14 [get_ports {debug_pc[13]}]
set_property PACKAGE_PIN B11 [get_ports {debug_pc[14]}]
set_property PACKAGE_PIN A11 [get_ports {debug_pc[15]}]
set_property PACKAGE_PIN E15 [get_ports {debug_pc[16]}]
set_property PACKAGE_PIN E16 [get_ports {debug_pc[17]}]
set_property PACKAGE_PIN D15 [get_ports {debug_pc[18]}]
set_property PACKAGE_PIN C15 [get_ports {debug_pc[19]}]
set_property PACKAGE_PIN H16 [get_ports {debug_pc[20]}]
set_property PACKAGE_PIN G16 [get_ports {debug_pc[21]}]
set_property PACKAGE_PIN F15 [get_ports {debug_pc[22]}]
set_property PACKAGE_PIN F16 [get_ports {debug_pc[23]}]
set_property PACKAGE_PIN H14 [get_ports {debug_pc[24]}]
set_property PACKAGE_PIN G14 [get_ports {debug_pc[25]}]
set_property PACKAGE_PIN E17 [get_ports {debug_pc[26]}]
set_property PACKAGE_PIN D17 [get_ports {debug_pc[27]}]
set_property PACKAGE_PIN K13 [get_ports {debug_pc[28]}]
set_property PACKAGE_PIN J13 [get_ports {debug_pc[29]}]
set_property PACKAGE_PIN H17 [get_ports {debug_pc[30]}]
set_property PACKAGE_PIN G17 [get_ports {debug_pc[31]}]


# 8 个用户 LED 低 8 位
set_property PACKAGE_PIN K3  [get_ports {leds[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {leds[0]}]

set_property PACKAGE_PIN M1  [get_ports {leds[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {leds[1]}]

set_property PACKAGE_PIN L1  [get_ports {leds[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {leds[2]}]

set_property PACKAGE_PIN K6  [get_ports {leds[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {leds[3]}]

set_property PACKAGE_PIN J5  [get_ports {leds[4]}]
set_property IOSTANDARD LVCMOS33 [get_ports {leds[4]}]

set_property PACKAGE_PIN H5  [get_ports {leds[5]}]
set_property IOSTANDARD LVCMOS33 [get_ports {leds[5]}]

set_property PACKAGE_PIN H6  [get_ports {leds[6]}]
set_property IOSTANDARD LVCMOS33 [get_ports {leds[6]}]

set_property PACKAGE_PIN K1  [get_ports {leds[7]}]
set_property IOSTANDARD LVCMOS33 [get_ports {leds[7]}]

# LED8-LED15（第二组 8 个 LED）
set_property PACKAGE_PIN K2  [get_ports {leds[8]}]   ;# D2_0
set_property IOSTANDARD LVCMOS33 [get_ports {leds[8]}]

set_property PACKAGE_PIN J2  [get_ports {leds[9]}]   ;# D2_1
set_property IOSTANDARD LVCMOS33 [get_ports {leds[9]}]

set_property PACKAGE_PIN J3  [get_ports {leds[10]}]  ;# D2_2
set_property IOSTANDARD LVCMOS33 [get_ports {leds[10]}]

set_property PACKAGE_PIN H4  [get_ports {leds[11]}]  ;# D2_3
set_property IOSTANDARD LVCMOS33 [get_ports {leds[11]}]

set_property PACKAGE_PIN J4  [get_ports {leds[12]}]  ;# D2_4
set_property IOSTANDARD LVCMOS33 [get_ports {leds[12]}]

set_property PACKAGE_PIN G3  [get_ports {leds[13]}]  ;# D2_5
set_property IOSTANDARD LVCMOS33 [get_ports {leds[13]}]

set_property PACKAGE_PIN G4  [get_ports {leds[14]}]  ;# D2_6
set_property IOSTANDARD LVCMOS33 [get_ports {leds[14]}]

set_property PACKAGE_PIN F6  [get_ports {leds[15]}]  ;# D2_7
set_property IOSTANDARD LVCMOS33 [get_ports {leds[15]}]


# ===== EGo1 七段数码管 段选 (seg[7:0]) =====
set_property PACKAGE_PIN B4  [get_ports {seg[0]}] ;# LED0_CA
set_property IOSTANDARD LVCMOS33 [get_ports {seg[0]}]
set_property PACKAGE_PIN A4  [get_ports {seg[1]}] ;# LED0_CB
set_property IOSTANDARD LVCMOS33 [get_ports {seg[1]}]
set_property PACKAGE_PIN A3  [get_ports {seg[2]}] ;# LED0_CC
set_property IOSTANDARD LVCMOS33 [get_ports {seg[2]}]
set_property PACKAGE_PIN B1  [get_ports {seg[3]}] ;# LED0_CD
set_property IOSTANDARD LVCMOS33 [get_ports {seg[3]}]
set_property PACKAGE_PIN A1  [get_ports {seg[4]}] ;# LED0_CE
set_property IOSTANDARD LVCMOS33 [get_ports {seg[4]}]
set_property PACKAGE_PIN B3  [get_ports {seg[5]}] ;# LED0_CF
set_property IOSTANDARD LVCMOS33 [get_ports {seg[5]}]
set_property PACKAGE_PIN B2  [get_ports {seg[6]}] ;# LED0_CG
set_property IOSTANDARD LVCMOS33 [get_ports {seg[6]}]
set_property PACKAGE_PIN D5  [get_ports {seg[7]}] ;# LED0_DP
set_property IOSTANDARD LVCMOS33 [get_ports {seg[7]}]

# ===== EGo1 七段数码管 位选 (an[7:0]) - 反向绑定 =====
# 逻辑 an[0] -> 最左边数码管（最高位）
# 逻辑 an[7] -> 最右边数码管（最低位）

set_property PACKAGE_PIN G6 [get_ports {an[0]}] ;# 原 LED_BIT8
set_property IOSTANDARD LVCMOS33 [get_ports {an[0]}]

set_property PACKAGE_PIN E1 [get_ports {an[1]}] ;# 原 LED_BIT7
set_property IOSTANDARD LVCMOS33 [get_ports {an[1]}]

set_property PACKAGE_PIN F1 [get_ports {an[2]}] ;# 原 LED_BIT6
set_property IOSTANDARD LVCMOS33 [get_ports {an[2]}]

set_property PACKAGE_PIN G1 [get_ports {an[3]}] ;# 原 LED_BIT5
set_property IOSTANDARD LVCMOS33 [get_ports {an[3]}]

set_property PACKAGE_PIN H1 [get_ports {an[4]}] ;# 原 LED_BIT4
set_property IOSTANDARD LVCMOS33 [get_ports {an[4]}]

set_property PACKAGE_PIN C1 [get_ports {an[5]}] ;# 原 LED_BIT3
set_property IOSTANDARD LVCMOS33 [get_ports {an[5]}]

set_property PACKAGE_PIN C2 [get_ports {an[6]}] ;# 原 LED_BIT2
set_property IOSTANDARD LVCMOS33 [get_ports {an[6]}]

set_property PACKAGE_PIN G2 [get_ports {an[7]}] ;# 原 LED_BIT1
set_property IOSTANDARD LVCMOS33 [get_ports {an[7]}]


# ===== EGo1 七段数码管 第二组段选 (seg1[7:0]) =====
set_property PACKAGE_PIN D4  [get_ports {seg1[0]}] ;# LED1_CA
set_property IOSTANDARD LVCMOS33 [get_ports {seg1[0]}]

set_property PACKAGE_PIN E3  [get_ports {seg1[1]}] ;# LED1_CB
set_property IOSTANDARD LVCMOS33 [get_ports {seg1[1]}]

set_property PACKAGE_PIN D3  [get_ports {seg1[2]}] ;# LED1_CC
set_property IOSTANDARD LVCMOS33 [get_ports {seg1[2]}]

set_property PACKAGE_PIN F4  [get_ports {seg1[3]}] ;# LED1_CD
set_property IOSTANDARD LVCMOS33 [get_ports {seg1[3]}]

set_property PACKAGE_PIN F3  [get_ports {seg1[4]}] ;# LED1_CE
set_property IOSTANDARD LVCMOS33 [get_ports {seg1[4]}]

set_property PACKAGE_PIN E2  [get_ports {seg1[5]}] ;# LED1_CF
set_property IOSTANDARD LVCMOS33 [get_ports {seg1[5]}]

set_property PACKAGE_PIN D2  [get_ports {seg1[6]}] ;# LED1_CG
set_property IOSTANDARD LVCMOS33 [get_ports {seg1[6]}]

set_property PACKAGE_PIN H2  [get_ports {seg1[7]}] ;# LED1_DP
set_property IOSTANDARD LVCMOS33 [get_ports {seg1[7]}]



