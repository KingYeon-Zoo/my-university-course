`timescale 1ns / 1ps
module input_signal_processing(
    input clk,
    input rst_btn_c,
    output rst,
    
    input rx_pin_jb1,
    output rx_pin_in,
    
    input get_btn_d,
    output read_sig,
    
    input send_btn_r,
    output write_sig,
    
    input en_sw15,
    output en_sig_ld15    
    );
    meta_harden rst_meta(
        .clk( clk ),
        .rst( 1'b0 ),
        .sig_src( rst_btn_c ),
        .sig_dst( rst )
    );
    meta_harden rx_pin_meta(
        .clk( clk ),
        .rst( rst ),
        .sig_src( rx_pin_jb1 ),
        .sig_dst( rx_pin_in )
    );
    ////////////////////////////////
    wire get_pin;
    btn_debounce get_btn(
        .clk( clk ),
        .rst( rst ),
        .btn_pin( get_btn_d ),
        .pin_out( get_pin ) 
    );
    L2H_detect read_detect(
        .clk( clk ),
        .rst( rst ),
        .pin_in( get_pin ),
        .sig_L2H( read_sig )
    );
    /////////////////////////////////////
    wire send_pin;
    btn_debounce send_btn(
        .clk( clk ),
        .rst( rst ),
        .btn_pin( send_btn_r ),
        .pin_out( send_pin )
    );
    L2H_detect write_detect(
        .clk( clk ),
        .rst( rst ),
        .pin_in( send_pin ),
        .sig_L2H( write_sig )
    );
    ////////////////////////////////////
    btn_debounce en_sw(
        .clk( clk ),
        .rst( rst ),
        .btn_pin( en_sw15 ),
        .pin_out( en_sig_ld15 ) 
    );
endmodule
