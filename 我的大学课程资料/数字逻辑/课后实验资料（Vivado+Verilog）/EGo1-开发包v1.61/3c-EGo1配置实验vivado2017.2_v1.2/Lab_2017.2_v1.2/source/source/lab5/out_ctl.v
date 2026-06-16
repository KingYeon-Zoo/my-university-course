`timescale 1ns / 1ps

module out_ctl(
    input clk,
    input rst,
    input dly_over,
    input pin_in,
    output reg pin_out
    );
    //
    always @( posedge clk or posedge rst )
        if( rst )
            pin_out <= pin_in;
        else if( dly_over )
            pin_out <= pin_in;
endmodule
