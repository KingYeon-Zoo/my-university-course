`timescale 1ns / 1ps
module uart_top_tb;
    //对时钟、复位以及使能进行初始化和控制
    reg clk,rst,en;
    initial begin
        clk = 1'b0;
        rst = 1'b0;
        en = 1'b0;
        #10 en = 1'b1; //打开时能
        #10 rst = 1'b1;//进行复位，复位时间为10ns（一个时钟周期）
        #10 rst = 1'b0;
    end
    always #5 clk <= ~clk; //由于时间单位是纳秒，而basys3开发板是100M，所以basys3的时钟周期等于10个时间单位
    //检测接收数据功能。向串口控制器发送一个数据，并从接收缓存中读取接收数据。
    reg read,rx_pin_in;
    wire rx_buf_not_empty,rx_clk_bps;
    wire [7:0]rx_get_data;
    //调用波特率生成模块，用于仿真发送波特率（这里也可以调用tx_band_gen模块，功能一样）
    rx_band_gen rx_band_gen( 
        .clk( clk ),
        .rst( rst ),
        .band_sig( 1'b1 ),  //始终有效
        .clk_bps( rx_clk_bps )
    );
    initial
    begin
        read = 1'b0;  //读操作初始化
        rx_pin_in = 1'b1; //接收引脚初始化
        #100
         //发送一帧数据：8'b01010101。根据生成的波特率发送数据，并且从最低位开始发送。
        @( posedge rx_clk_bps ) rx_pin_in = 1'b0;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b1;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b0;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b1;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b0;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b1;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b0;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b1;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b0;
        @( posedge rx_clk_bps ) rx_pin_in = 1'b1;
        //等待两个波特率周期后读取接收缓存数据
        @( posedge rx_clk_bps );
        @( posedge rx_clk_bps );
        @( posedge clk ) read = 1'b1;
        @( posedge clk ) read = 1'b0;
    end
    //检测发送数据功能。向串口控制器的发送缓存中写入两个待发送数据，观察发送引脚tx_pin_out波形。
    reg write;
    wire tx_pin_out,tx_buf_not_full;
    reg [7:0] tx_send_data;
    initial
    begin
        write = 1'b0;
        #10000
        @( posedge clk ) tx_send_data = 8'b01101001; write = 1'b1;
        @( posedge clk ) write = 1'b0; 
                        
        @( posedge clk ) tx_send_data = 8'b01010101; write = 1'b1;
        @( posedge clk ) write = 1'b0;
    end
    //这里主要对uart_top进行仿真。因为input_signal_processing和data_show模块
    //只是对外围设备信号进行处理，不是必须模块，所以这里只对uart_top模块进行仿真
    uart_top uart_top(
        .clk( clk ),
        .rst( rst ),
        .en( en ),
        .rx_read( read ),
        .rx_pin_in( rx_pin_in ),
        .rx_get_data( rx_get_data ),
        .rx_buf_not_empty( rx_buf_not_empty ),
        .tx_write( write ),
        .tx_pin_out( tx_pin_out ),
        .tx_send_data( tx_send_data ),
        .tx_buf_not_full( tx_buf_not_full )
    );
endmodule
