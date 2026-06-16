`timescale 1ns / 1ps
module tx_ctl(
    input clk,
    input rst,
    input tx_clk_bps,
    output reg tx_band_sig,
    output reg tx_pin_out,
    input [7:0]tx_data,
    input tx_buf_not_empty,
    output reg tx_read_buf
    );
    //1位开始位，8位数据位，1位结束位
    localparam [3:0] IDLE = 4'd0, BEGIN = 4'd1, DATA0 = 4'd2,
                     DATA1 = 4'd3, DATA2 = 4'd4, DATA3 = 4'd5, 
                     DATA4 = 4'd6, DATA5 = 4'd7, DATA6 = 4'd8, 
                     DATA7 = 4'd9, END = 4'd10, BFREE = 4'd11; 
                     
    reg [3:0]pos;
    always @( posedge clk or posedge rst )
        if( rst )
        begin
            tx_band_sig <= 1'b0;
            tx_pin_out <= 1'b1;
            tx_read_buf <= 1'b0;
            pos <= IDLE;
        end
        else
            case( pos )
                IDLE:
                    if( tx_buf_not_empty )
                    begin
                        tx_read_buf <= 1'b1;
                        tx_band_sig <= 1'b1;
                        pos <= pos + 1'b1;
                    end
                BEGIN:
                begin
                    tx_read_buf <= 1'b0;
                    if( tx_clk_bps )
                    begin
                        tx_pin_out <= 1'b0;
                        pos <= pos + 1'b1;
                    end
                end
                DATA0, DATA1,DATA2,DATA3,DATA4,DATA5,DATA6,DATA7:
                    if( tx_clk_bps )
                    begin
                        tx_pin_out <= tx_data[ pos - DATA0 ];
                        pos <= pos + 1'b1;
                    end
                END:
                    if( tx_clk_bps )
                    begin
                        tx_pin_out <= 1'b1;
                        pos <= pos + 1'b1;
                    end
                BFREE:
                    if( tx_clk_bps )
                    begin
                        pos <= IDLE;
                        tx_band_sig <= 1'b0;
                    end
            endcase
    
endmodule
