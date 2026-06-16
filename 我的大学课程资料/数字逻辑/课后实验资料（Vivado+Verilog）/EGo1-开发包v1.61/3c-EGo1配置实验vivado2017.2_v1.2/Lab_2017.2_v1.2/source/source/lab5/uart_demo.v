`timescale 1ns / 1ps
module uart_demo(
    input clk,
    input rst_n,
    
    input en_sw15,
    output en_sig_ld15,
    
    input get_btn_d,
    input rx_pin_jb1,
    output rx_buf_not_empty,
    output rx_buf_full,
    
    input send_btn_r,
    input [7:0]tx_send_data,                           //SW0~Sw7
    output tx_pin_jb0,
    output tx_buf_not_full,
    
    output [3:0]an,
    output [7:0]seg_code
    );
    wire rst,rx_pin_in,read_sig,write_sig;
    wire rst_btn_c = ~rst_n;
    input_signal_processing sig_processing(
        .clk( clk ),
        .rst_btn_c( rst_btn_c ),
        .rst( rst ),
        
        .rx_pin_jb1( rx_pin_jb1 ),
        .rx_pin_in( rx_pin_in ),
        
        .get_btn_d( get_btn_d ),
        .read_sig( read_sig ),
        
        .send_btn_r( send_btn_r ),
        .write_sig( write_sig ),
        
        .en_sw15( en_sw15 ),
        .en_sig_ld15( en_sig_ld15 )       
    );
    //
    wire [7:0]rx_get_data;
    uart_top uart_top(
        .clk( clk ),
        .rst( rst ),
        
        .en( en_sig_ld15 ),
        
        .rx_read( read_sig ),
        .rx_pin_in( rx_pin_in ),
        .rx_get_data( rx_get_data ),
        .rx_buf_not_empty( rx_buf_not_empty ),
        .rx_buf_full( rx_buf_full ),
        
        .tx_write( write_sig ),
        .tx_pin_out( tx_pin_jb0 ),
        .tx_send_data( tx_send_data ),
        .tx_buf_not_full( tx_buf_not_full )
    );
    
    data_show data_show(
        .clk( clk ),
        .rst( rst ),
        .rx_data( rx_get_data ),
        .tx_data( tx_send_data ),
        .an( an ),
        .seg_code( seg_code )
    );
endmodule
