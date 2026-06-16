# EGo Pin Assignmentso
############################
# On-board Slide Switches  #
############################
set_property -dict { PACKAGE_PIN P5   IOSTANDARD LVCMOS33 } [get_ports { swt[0] }];
set_property -dict { PACKAGE_PIN P4   IOSTANDARD LVCMOS33 } [get_ports { swt[1] }];
set_property -dict { PACKAGE_PIN P3   IOSTANDARD LVCMOS33 } [get_ports { swt[2] }];
set_property -dict { PACKAGE_PIN P2   IOSTANDARD LVCMOS33 } [get_ports { swt[3] }];
set_property -dict { PACKAGE_PIN R2   IOSTANDARD LVCMOS33 } [get_ports { swt[4] }];
set_property -dict { PACKAGE_PIN M4   IOSTANDARD LVCMOS33 } [get_ports { swt[5] }];
set_property -dict { PACKAGE_PIN N4   IOSTANDARD LVCMOS33 } [get_ports { swt[6] }];
set_property -dict { PACKAGE_PIN R1   IOSTANDARD LVCMOS33 } [get_ports { swt[7] }];

############################
# On-board led             #
############################
set_property -dict { PACKAGE_PIN F6   IOSTANDARD LVCMOS33 } [get_ports { led[0] }];
set_property -dict { PACKAGE_PIN G4   IOSTANDARD LVCMOS33 } [get_ports { led[1] }];
set_property -dict { PACKAGE_PIN G3   IOSTANDARD LVCMOS33 } [get_ports { led[2] }];
set_property -dict { PACKAGE_PIN J4   IOSTANDARD LVCMOS33 } [get_ports { led[3] }];
set_property -dict { PACKAGE_PIN H4   IOSTANDARD LVCMOS33 } [get_ports { led[4] }];
set_property -dict { PACKAGE_PIN J3   IOSTANDARD LVCMOS33 } [get_ports { led[5] }];
set_property -dict { PACKAGE_PIN J2   IOSTANDARD LVCMOS33 } [get_ports { led[6] }];
set_property -dict { PACKAGE_PIN K2   IOSTANDARD LVCMOS33 } [get_ports { led[7] }];