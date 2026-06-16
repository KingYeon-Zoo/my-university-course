`timescale 1ns / 1ps
module rx_ctl(
    input clk,
    input rst,
    input rx_pin_in,
    input rx_pin_H2L,
    output reg rx_band_sig,
    input rx_clk_bps,
    output reg[7:0]rx_data,
    output reg rx_done_sig
    );
    localparam [3:0] IDLE = 4'd0, BEGIN = 4'd1, DATA0 = 4'd2,
                     DATA1 = 4'd3, DATA2 = 4'd4, DATA3 = 4'd5, 
                     DATA4 = 4'd6, DATA5 = 4'd7, DATA6 = 4'd8, 
                     DATA7 = 4'd9, END = 4'd10, BFREE = 4'd11; 
    reg [3:0]pos;
    always @( posedge clk or posedge rst )
        if( rst )
        begin
            rx_band_sig <= 1'b0;
            rx_data <= 8'd0;
            pos <= IDLE;
            rx_done_sig <= 1'b0;
        end
        else
            case( pos )
                IDLE:
                    if( rx_pin_H2L )
                    begin
                        rx_band_sig <= 1'b1;
                        pos <= pos + 1'b1;
                        rx_data <= 8'd0;
                    end
                BEGIN:
                    if( rx_clk_bps )
                    begin
                        if( rx_pin_in == 1'b0 )
                        begin
                            pos <= pos + 1'b1;
                        end
                        else
                        begin
                            rx_band_sig <= 1'b0;
                            pos <= IDLE;
                        end
                    end
                DATA0,DATA1,DATA2,DATA3,DATA4,DATA5,DATA6,DATA7:
                    if( rx_clk_bps )
                    begin
                        rx_data[ pos - DATA0 ] <= rx_pin_in;
                        pos <= pos + 1'b1; 
                    end
                END:
                    if( rx_clk_bps )
                    begin
                        rx_done_sig <= 1'b1;
                        pos <= pos + 1'b1;
                        rx_band_sig <= 1'b0;
                    end
                BFREE:
                begin
                    rx_done_sig <= 1'b0;
                    pos <= IDLE;
                end
            endcase
endmodule
