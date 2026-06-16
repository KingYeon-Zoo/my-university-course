clear;
clc;
x=0:1/100:4;
y=0.1*sin(pi.*x)+0.1*sin(2*pi*49.*x);
plot(x,y);
y=fix(y*(2^8));
fid = fopen('sample.coe','wt');
fprintf(fid,'memory_initialization_radix = 10;\nmemory_initialization_vector = ');
for i = 1 : 801
    if mod(i-1,8) == 0 
        fprintf(fid,'\n');
    end
    fprintf(fid,'%4d,',y);
end
