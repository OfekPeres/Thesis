s = tf('s');

K = 5;
kp = 2;
kd = 1;
ki = 1;

P = K/s;

C_p = kp;
C_pd = kp + kd*s;
C_pid = kp + kd*s + ki/s;

L_p = P*C_p;
L_pd = P*C_pd;
L_pid = P*C_pid;

H_p = L_p/(1+L_p);
H_pd = L_pd/(1+L_pd);
H_pid = L_pid/(1 + L_pid);

G_p = K/s;
figure
subplot(1,3,1)
rlocus(G_p)
title('P Control in terms of k_p')

G_pd1 = K/(1 + K*kp/s);
subplot(1,3,2)
rlocus(G_pd1)
title('PD Control in terms of k_d')

G_pd2 = K/(s*(1 + K*kd));
subplot(1,3,3)
rlocus(G_pd2)
title('PD Control in terms of k_p')

figure
subplot(3,3,1)
margin(L_p)
subplot(3,3,2)
margin(L_pd)
subplot(3,3,3)
margin(L_pid)
subplot(3,3,4)
step(H_p)
subplot(3,3,5)
step(H_pd)
subplot(3,3,6)
step(H_pid)
subplot(3,3,7)
nyquist(L_p)
subplot(3,3,8)
nyquist(L_pd)
subplot(3,3,9)
nyquist(L_pid)


