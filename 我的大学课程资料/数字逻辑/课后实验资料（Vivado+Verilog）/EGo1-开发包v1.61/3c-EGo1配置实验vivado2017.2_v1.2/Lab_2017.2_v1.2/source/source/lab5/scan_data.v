`timescale 1ns / 1ps
module scan_data(
    input clk,
    input rst,
    input [7:0]rx_down_code,
    input [7:0]rx_up_code,
    input [7:0]tx_down_code,
    input [7:0]tx_up_code,
    output reg[3:0]an,
    output reg[7:0]seg_code
    );
    parameter AN0 = 4'b0001,AN1 = 4'b0010,AN2 = 4'b0100,AN3 = 4'b1000;
    parameter FRE_CNT = 20'd625000;
    
    reg [19:0]cnt_fre;
    reg [1:0]pos;
    always @( posedge clk or posedge rst )
        if( rst )
        begin
            pos <= 2'd0;
            cnt_fre <= 20'd0;
        end
        else if( cnt_fre == FRE_CNT )
        begin
            pos <= pos + 1'b1;
            cnt_fre <= 20'd0;
        end
        else
            cnt_fre <= cnt_fre + 1'b1;
                
    always @( posedge clk or posedge rst )
        if( rst )
        begin
            an <= 4'hf;
            seg_code <= 8'hff;
        end
        else
            case( pos )
                2'd0:
                begin
                    an <= AN0;
                    seg_code <= tx_down_code;
                end
                2'd1:
                begin
                    an <= AN1;
                    seg_code <= tx_up_code;
                end
                2'd2:
                begin
                    an <= AN2;
                    seg_code <= rx_down_code;
                end
                2'd3:
                begin
                    an <= AN3;
                    seg_code <= rx_up_code;
                end
            endcase
endmodule
