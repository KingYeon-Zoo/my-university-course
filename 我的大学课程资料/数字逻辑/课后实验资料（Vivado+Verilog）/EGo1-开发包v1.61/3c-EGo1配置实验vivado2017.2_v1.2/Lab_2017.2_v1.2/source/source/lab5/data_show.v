`timescale 1ns / 1ps
module data_show(
    input clk,
    input rst,
    input [7:0]rx_data,
    input [7:0]tx_data,
    output [3:0]an,
    output [7:0]seg_code
    );
    wire [7:0]rx_down_code;
    number_encode rx_down_encode(
        .clk( clk ),
        .rst( rst ),
        .number_in( rx_data[3:0] ),
        .code_out( rx_down_code )
    );
    wire [7:0]rx_up_code;
    number_encode rx_up_encode(
        .clk( clk ),
        .rst( rst ),
        .number_in( rx_data[7:4] ),
        .code_out( rx_up_code )
    );
    wire [7:0]tx_down_code;
    number_encode tx_down_encode(
        .clk( clk ),
        .rst( rst ),
        .number_in( tx_data[3:0] ),
        .code_out( tx_down_code )
    );
    wire [7:0]tx_up_code;
    number_encode tx_up_encode(
        .clk( clk ),
        .rst( rst ),
        .number_in( tx_data[7:4] ),
        .code_out( tx_up_code )
    );
    scan_data scan_data(
        .clk( clk ),
        .rst( rst ),
        .rx_down_code( rx_down_code ),
        .rx_up_code( rx_up_code ),
        .tx_down_code( tx_down_code ),
        .tx_up_code( tx_up_code ),  
        .an( an ),
        .seg_code( seg_code )
    );     
endmodule
