`timescale 1ns / 1ps
module H2L_detect(
    input clk,
    input rst,
    input pin_in,
    output sig_H2L
    );
    //
    reg pin_pre;
    assign sig_H2L = !pin_in & pin_pre;
    always @( posedge clk or posedge rst )
        if( rst )
            pin_pre <= 1'b0;
        else
            pin_pre <= pin_in;
    
endmodule