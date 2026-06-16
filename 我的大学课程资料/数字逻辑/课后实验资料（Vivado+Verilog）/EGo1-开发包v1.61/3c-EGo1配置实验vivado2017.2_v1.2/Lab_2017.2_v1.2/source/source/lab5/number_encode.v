`timescale 1ns / 1ps
module number_encode(
    input clk,
    input rst,
    input [3:0]number_in,
    output reg [7:0]code_out
    );
    
//    parameter _0 = 8'b1011_1111,_1 = 8'b1000_0110,_2 = 8'b1101_1011,_3 = 8'b1100_1111,//gong yin
//                   _4 = 8'b1110_0110,_5 = 8'b1110_1101,_6 = 8'b1111_11101,_7 = 8'b1000_0111,
//                   _8 = 8'b1111_1111,_9 = 8'b1110_1111,_10 = 8'b1111_0111,_11 = 8'b1001_1111,
//                 _12 = 8'b1000_1101,_13 = 8'b1011_1101,_14 = 8'b1100_1111,_15 = 8'b1110_1111;
    
        parameter _0 = 8'b10111111,_1 = 8'b10000110,_2 = 8'b11011011,_3 = 8'b11001111,
             _4 = 8'b11100110,_5 = 8'b1110_1101,_6 = 8'b1111_1101,_7 = 8'b1000_0111,
             _8 = 8'b1111_1111,_9 = 8'b1110_1111,_10 = 8'b1111_0111,_11 = 8'b1111_1100,
             _12 = 8'b1011_1001,_13 = 8'b1101_1110,_14 = 8'b1111_1001,_15 = 8'b1111_0001;

    
//    parameter _0 = 8'hc0,_1 = 8'hf9,_2 = 8'ha4,_3 = 8'hb0,//gong yang
//               _4 = 8'h99,_5 = 8'h92,_6 = 8'h82,_7 = 8'hf8,
//               _8 = 8'h80,_9 = 8'h90,_10 = 8'h88,_11 = 8'h83,
//               _12 = 8'hc6,_13 = 8'ha1,_14 = 8'h86,_15 = 8'h8e; 
    always @( posedge clk or posedge rst )
        if( rst )
            code_out <= _0;
        else
            case( number_in )
                4'd0:code_out <= _0;
                4'd1:code_out <= _1;
                4'd2:code_out <= _2;
                4'd3:code_out <= _3;
                4'd4:code_out <= _4;
                4'd5:code_out <= _5;
                4'd6:code_out <= _6;
                4'd7:code_out <= _7;
                4'd8:code_out <= _8;
                4'd9:code_out <= _9;
                4'd10:code_out <= _10;
                4'd11:code_out <= _11;
                4'd12:code_out <= _12;
                4'd13:code_out <= _13;
                4'd14:code_out <= _14;
                4'd15:code_out <= _15;
            endcase
endmodule
