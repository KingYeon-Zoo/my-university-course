clear;
clc;
x=0:1/100:4;
y=0.1*sin(pi.*x)+0.1*sin(2*pi*49.*x);
Hd = mylowerfilter;
output=filter(Hd,y);
plot(output);
title('ÂË²¨ºóµÄ²¨ÐÎ');

