%% data
distance_data = xlsread('distance_data');
distance = distance_data(:,1);
area_percent = distance_data(:,2);
n = 28;

a = 8.228;
b = -0.512;
x = linspace(0, 0.6, 130);
y_fit = a.*x.^b;

figure
plot(area_percent, distance, 'o', 'Linewidth', 2)
hold on
plot(x, y_fit, 'Linewidth', 2)
ylabel('distance (inches)')
xlabel('percent area (%)')

%% nonlinear least squares data fitting

y = area_percent;
m = 28;
d = distance;

g       = @(x) x(1).*d.^x(2) + x(3) - y;
dgda    = @(x) d.^x(2);
dgdb    = @(x) x(2)*x(1).*d.^(x(2)-1);
dgdc    = ones(m,1);

J = @(x) [dgda(x), dgdb(x), dgdc];

a0 = 1;
b0 = -2;
c0 = 0;

x_k = [a0; b0; c0];

for i = 1:10
    x_k = x_k - (J(x_k)'*J(x_k))\J(x_k)'*g(x_k);
end

x_k

% figure(6)
% plot(t,y,'.')
% hold on
% T = @(x) x(1).*sin(2.*pi./x(5).*t + x(4)) + x(2).*t + x(3);
% plot(t,T(x_k),'LineWidth',2)
% xlabel('time (days)')
% ylabel('Temperature (degrees Farenheit)')
% title('Average Daily Temperature Model')
% legend('Temperature Data', 'Temperature Model')
