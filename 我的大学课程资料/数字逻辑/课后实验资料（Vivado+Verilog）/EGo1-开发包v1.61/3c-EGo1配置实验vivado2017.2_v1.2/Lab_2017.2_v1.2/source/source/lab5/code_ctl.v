`timescale 1ns / 1ps
module en_ctl(
    input clk,
    input rst,
    
    input en,
    
    input rx_read,
    input tx_write,
    
    output gate_clk,
    output reg rst_en_ctl,
    output rx_read_buf,
    output tx_write_buf
    );
    //
    reg en_reg;
    assign rx_read_buf = rx_read & en_reg;
    assign tx_write_buf = tx_write & en_reg;
    assign gate_clk = clk & en_reg;
    
    //对rst的控制。由于en引发的系统不稳定（主要是tx_top,rx_top的不稳定，主要对tx_top,rx_top进行复位）
    wire en_H2L;
    reg en_pre;
    assign en_H2L = !en & en_pre;
    always @( posedge clk or posedge rst )
        if( rst )
            en_pre <= 1'b0;
        else
            en_pre <= en;    
    always @( posedge clk or posedge rst )
        if( rst )
            rst_en_ctl <= 1'b1;
        else if( en_H2L )
            rst_en_ctl <= 1'b1;
        else
            rst_en_ctl <= 1'b0;
    
    //对en使能控制。由于rst会引起系统的不稳定(主要是FIFO模块的不稳定)，所以需要对en使能进行延时。
    reg [3:0]cnt;
    always @( posedge clk or posedge rst )
        if( rst )
            en_reg <= 1'b0;
        else if( cnt == 4'd15 )
            en_reg <= en;
    always @( posedge clk or posedge rst )
        if( rst )
            cnt <= 4'd0;
        else if( cnt != 4'd15 )
            cnt <= cnt + 1'b1;
endmodule
