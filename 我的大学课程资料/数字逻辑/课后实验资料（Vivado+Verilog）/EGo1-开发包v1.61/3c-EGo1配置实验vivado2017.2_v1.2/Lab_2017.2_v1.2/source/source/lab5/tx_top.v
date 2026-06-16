`timescale 1ns / 1ps
module tx_top(
    input clk,
    input rst,
    
    output tx_pin_out,
    input [7:0]tx_data,
    input tx_buf_not_empty,
    output tx_read_buf
    );
    
    wire tx_band_sig;
    wire clk_bps;
    tx_band_gen tx_band_gen(
        .clk( clk ),
        .rst( rst ),
        .band_sig( tx_band_sig ),
        .clk_bps( clk_bps )
    );
    tx_ctl tx_ctl(
        .clk( clk ),
        .rst( rst ),
        .tx_clk_bps( clk_bps ),
        .tx_band_sig( tx_band_sig ),
        .tx_pin_out( tx_pin_out ),
        .tx_data( tx_data ),
        .tx_buf_not_empty( tx_buf_not_empty ),
        .tx_read_buf( tx_read_buf )
    );
    
endmodule
