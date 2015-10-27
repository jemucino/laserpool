% Transform from LIDAR to pool table coordinates

function [xt,yt]=transformdata(x)

rawdata=double(x.data{end});

r=rawdata(1:4:end)+rawdata(2:4:end)*2^8+rawdata(3:4:end)*2^16+rawdata(4:4:end)*2^24;
% r=2400*ones(1,571);
% x0=r.*cos(185/180*pi-theta);
% y0=r.*sin(185/180*pi-theta);
% plot(x0.*(y0<10000),y0.*(y0<10000),'o','MarkerSize',4)
tableorientation=atan2(211,274.14); 
Ro=1888.8;	% Distance to center of table in mm
To=pi/2+atan(-55/R0);	% Rotation of LIDAR axes relative to pool table axes

% Compute position of center of table in rotated LIDAR coordinates
Xo=Ro*cos(pi-To-tableorientation);
Yo=Ro*sin(pi-To-tableorientation);

theta=([-5/180:1/540:185/180]*pi-tableorientation); %already oriented to the table

%r=cat(2,r,0);
%theta=cat(2,theta,0);

xt=r.*cos(theta)-Xo;
yt=r.*sin(theta)-Yo;

% origin=[Ro,To];




% D=(r.^2+Ro^2-2*Ro*r.*cos(To-theta)).^0.5;
% beta=asin(r.*sin(To-theta)./D2);
% beta=acos((D.^2+Ro^2-r.^2)./(2*Ro*D));
% alpha=-To-beta-tableorientation;

% xt=D.*cos(alpha);
% yt=D.*sin(alpha);

%plot(xt(end),yt(end),'ko','MarkerFaceColor','k','MarkerSize',6)

