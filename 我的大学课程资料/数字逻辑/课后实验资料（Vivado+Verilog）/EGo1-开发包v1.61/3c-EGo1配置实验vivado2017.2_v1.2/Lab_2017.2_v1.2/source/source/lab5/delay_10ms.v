`timescale 1ns / 1ps
module delay_10ms(
    input clk,
    input rst,
    input dly_sig,
    output reg dly_over
    );
    //
    parameter T10MS = 20'd1000000;
    //
    reg [19:0]cnt_clk;
    reg pos;
    always @( posedge clk or posedge rst )
        if( rst )
        begin
            cnt_clk <=20'd0;
            dly_over <= 1'b0;
            pos <= 1'b0;
        end
        else 
            case( pos )
                1'b0:
                begin
                    dly_over <= 1'b0;
                    if( dly_sig )
                        pos <= 1'b1;
                end   
                1'b1:
                    if( cnt_clk == T10MS )
                    begin
                        dly_over <= 1'b1;
                        cnt_clk <= 20'd0;
                        pos <= 1'b0;
                    end
                    else
                        cnt_clk <= cnt_clk + 1'b1;
            endcase
    //
endmodule
