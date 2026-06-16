`timescale 1ns / 1ps
module uart_top(
    input clk,
    input rst,
    
    input en,
    
    input rx_read,
    input rx_pin_in,
    output rx_buf_not_empty,
    output rx_buf_full,
    output [7:0]rx_get_data,
    
    input tx_write,
    input [7:0]tx_send_data,
    output tx_pin_out,
    output tx_buf_not_full
    );
    
    wire rx_read_buf,tx_write_buf;
    wire gate_clk,rst_en_ctl;
    en_ctl en_ctl(
        .clk( clk ),
        .rst( rst ),
        
        .en( en ),
        
        .rx_read( rx_read ),
        .tx_write( tx_write ),
        
        .gate_clk( gate_clk ),
        .rst_en_ctl( rst_en_ctl ),
        .rx_read_buf( rx_read_buf ),
        .tx_write_buf( tx_write_buf )
    );
    wire [7:0]rx_data;
    wire rx_write_buf;
    wire rx_buf_empty;
    assign rx_buf_not_empty = ~rx_buf_empty;
    data_buf rx_buf (
      .clk( clk ),      // input wire clk
      .rst( rst ),      // input wire rst
      .din( rx_data ),      // input wire [7 : 0] din
      .wr_en( rx_write_buf ),  // input wire wr_en
      .rd_en( rx_read_buf ),  // input wire rd_en
      .dout( rx_get_data ),    // output wire [7 : 0] dout
      .full( rx_buf_full ),    // output wire full
      .empty( rx_buf_empty )  // output wire empty
    );
    wire tx_read_buf;
    wire [7:0]tx_data;
    wire tx_buf_full,tx_buf_empty;
    wire tx_buf_not_empty;
    assign tx_buf_not_full = ~tx_buf_full;
    assign tx_buf_not_empty = ~tx_buf_empty;
    data_buf tx_buf (
      .clk( clk ),      // input wire clk
      .rst( rst ),      // input wire rst
      .din( tx_send_data ),      // input wire [7 : 0] din
      .wr_en( tx_write_buf ),  // input wire wr_en
      .rd_en( tx_read_buf ),  // input wire rd_en
      .dout( tx_data ),    // output wire [7 : 0] dout
      .full( tx_buf_full ),    // output wire full
      .empty( tx_buf_empty )  // output wire empty
    );
    
    tx_top tx_top(
        .clk( clk ),
        .rst( rst_en_ctl ),
        .tx_pin_out( tx_pin_out ),
        .tx_data( tx_data ),
        .tx_buf_not_empty( tx_buf_not_empty ),
        .tx_read_buf( tx_read_buf )
    );
    rx_top rx_top(
        .clk( clk ),
        .rst( rst_en_ctl ),
        .rx_pin_in( rx_pin_in ),
        .rx_data( rx_data ),
        .rx_done_sig( rx_write_buf )
    );
endmodule
