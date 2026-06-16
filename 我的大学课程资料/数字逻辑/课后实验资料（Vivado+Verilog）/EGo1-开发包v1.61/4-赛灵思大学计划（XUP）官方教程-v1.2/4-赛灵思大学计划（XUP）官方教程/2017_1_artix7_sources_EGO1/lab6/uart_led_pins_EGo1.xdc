# EGo xdc
# LED [7:0]
############################
# On-board led             #
############################
set_property -dict {PACKAGE_PIN F6 IOSTANDARD LVCMOS33} [get_ports {led_pins[0]}]
set_property -dict {PACKAGE_PIN G4 IOSTANDARD LVCMOS33} [get_ports {led_pins[1]}]
set_property -dict {PACKAGE_PIN G3 IOSTANDARD LVCMOS33} [get_ports {led_pins[2]}]
set_property -dict {PACKAGE_PIN J4 IOSTANDARD LVCMOS33} [get_ports {led_pins[3]}]
set_property -dict {PACKAGE_PIN H4 IOSTANDARD LVCMOS33} [get_ports {led_pins[4]}]
set_property -dict {PACKAGE_PIN J3 IOSTANDARD LVCMOS33} [get_ports {led_pins[5]}]
set_property -dict {PACKAGE_PIN J2 IOSTANDARD LVCMOS33} [get_ports {led_pins[6]}]
set_property -dict {PACKAGE_PIN K2 IOSTANDARD LVCMOS33} [get_ports {led_pins[7]}]

# CLK source 100 MHz
set_property -dict {PACKAGE_PIN P17 IOSTANDARD LVCMOS33} [get_ports clk_pin]

# BTNU
set_property -dict {PACKAGE_PIN R11 IOSTANDARD LVCMOS33} [get_ports btn_pin]

# RXD UART
set_property -dict {PACKAGE_PIN N5 IOSTANDARD LVCMOS33} [get_ports rxd_pin]

# Reset - BTNC
set_property -dict {PACKAGE_PIN P15 IOSTANDARD LVCMOS33} [get_ports rst_pin]