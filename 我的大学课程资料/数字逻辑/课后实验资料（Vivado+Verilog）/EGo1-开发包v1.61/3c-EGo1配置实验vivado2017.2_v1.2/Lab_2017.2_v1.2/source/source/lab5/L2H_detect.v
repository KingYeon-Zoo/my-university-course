`timescale 1ns / 1ps
module L2H_detect(
    input clk,
    input rst,
    input pin_in,
    output sig_L2H
    );
    //
    reg pin_pre;
    assign sig_L2H = pin_in & !pin_pre;
    always @( posedge clk or posedge rst )
        if( rst )
            pin_pre <= 1'b0;
        else
            pin_pre <= pin_in;
    
endmodule