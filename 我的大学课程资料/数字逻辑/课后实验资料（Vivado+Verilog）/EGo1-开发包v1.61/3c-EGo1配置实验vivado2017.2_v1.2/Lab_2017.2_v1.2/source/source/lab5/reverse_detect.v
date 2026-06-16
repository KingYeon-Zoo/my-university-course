`timescale 1ns / 1ps
module reverse_detect(
    input clk,
    input rst,
    input pin_in,
    output reverse_sig
    );
    reg pin_pre;
    always @( posedge clk or posedge rst )
        if( rst )
            pin_pre <= 1'b0;
        else
            pin_pre <= pin_in;
    //
    assign reverse_sig = ( pin_in != pin_pre );
    //
endmodule
