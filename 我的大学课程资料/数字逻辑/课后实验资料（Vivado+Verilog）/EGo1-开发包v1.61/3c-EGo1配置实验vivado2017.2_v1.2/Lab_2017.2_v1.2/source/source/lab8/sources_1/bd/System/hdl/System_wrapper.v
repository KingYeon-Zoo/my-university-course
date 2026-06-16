//Copyright 1986-2017 Xilinx, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2017.2 (win64) Build 1909853 Thu Jun 15 18:39:09 MDT 2017
//Date        : Mon Jul 10 22:38:27 2017
//Host        : GWDRJUW2FOFGBND running 64-bit Service Pack 1  (build 7601)
//Command     : generate_target System_wrapper.bd
//Design      : System_wrapper
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module System_wrapper
   (clk,
    led_tri_o,
    uart_rtl_rxd,
    uart_rtl_txd);
  input clk;
  output [7:0]led_tri_o;
  input uart_rtl_rxd;
  output uart_rtl_txd;

  wire clk;
  wire [7:0]led_tri_o;
  wire uart_rtl_rxd;
  wire uart_rtl_txd;

  System System_i
       (.clk(clk),
        .led_tri_o(led_tri_o),
        .uart_rtl_rxd(uart_rtl_rxd),
        .uart_rtl_txd(uart_rtl_txd));
endmodule
