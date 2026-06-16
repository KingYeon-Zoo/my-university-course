`timescale 1ns / 1ps
module rx_top(
    input clk,
    input rst,
    input rx_pin_in,
    output [7:0]rx_data,
    output rx_done_sig
    );
    wire rx_pin_H2L;
    H2L_detect rx_in_detect(
        .clk( clk ),
        .rst( rst ),
        .pin_in( rx_pin_in ),
        .sig_H2L( rx_pin_H2L )
    );
    wire rx_band_sig;
    wire clk_bps;
    rx_band_gen rx_band_gen(
        .clk( clk ),
        .rst( rst ),
        .band_sig( rx_band_sig ),
        .clk_bps( clk_bps )
    );
    rx_ctl rx_ctl(
        .clk( clk ),
        .rst( rst ),
        .rx_pin_in( rx_pin_in ),
        .rx_pin_H2L( rx_pin_H2L ),
        .rx_band_sig( rx_band_sig ),
        .rx_clk_bps( clk_bps ),
        .rx_data( rx_data ),
        .rx_done_sig( rx_done_sig )
    );
endmodule
