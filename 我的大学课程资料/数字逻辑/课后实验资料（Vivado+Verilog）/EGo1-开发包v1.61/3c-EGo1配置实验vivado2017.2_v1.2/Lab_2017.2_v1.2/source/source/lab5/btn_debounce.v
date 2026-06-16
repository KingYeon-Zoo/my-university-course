`timescale 1ns / 1ps
module btn_debounce(
    input clk,
    input rst,
    input btn_pin,
    output pin_out
    );
    //
    wire btn_pin_m;
    meta_harden pin_meta(
        .clk( clk ),
        .rst( rst ),
        .sig_src( btn_pin ),
        .sig_dst( btn_pin_m )
    );
    wire reverse_sig;
    reverse_detect reverse_detect(
        .clk( clk ),
        .rst( rst ),
        .pin_in( btn_pin_m ),
        .reverse_sig( reverse_sig )
    );
    //
    wire dly_over;
    delay_10ms delay_10ms(
        .clk( clk ),
        .rst( rst ),
        .dly_sig( reverse_sig ),
        .dly_over( dly_over )
    );
    //
    out_ctl out_ctl(
        .clk( clk ),
        .rst( rst ),
        .dly_over( dly_over ),
        .pin_in( btn_pin_m ),
        .pin_out( pin_out )
    );
endmodule
