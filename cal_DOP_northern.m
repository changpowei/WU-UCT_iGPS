function [percent] = cal_DOP_northern(BS_lats, BS_lons);

c = physconst('lightspeed');

lat_bound1 = 24.30129; lat_bound2 = 25.29701;
lon_bound1 = 120.9; lon_bound2 = 122.00862;

reference_lat = 24.79915;
reference_lon = 121.45431;
BS_lats = [BS_lats, reference_lat];
BS_lons = [BS_lons, reference_lon];

%
tx = txsite('Name','iGPS Tx',...
    'Latitude',BS_lats(:), ...
    'Longitude',BS_lons(:), ...
    'AntennaHeight',10, ...
    'TransmitterFrequency',375e+06, ...
    'TransmitterPower',50);
% show(tx)
% coverage(tx,"SignalStrengths",-120:10:-20,'MaxRange',30e+03);
%
tx_elevations = elevation(tx);
% 轉直角座標
for itx = 1:size(BS_lats,2),
    tx_xyz(:,itx) = llh2xyz([BS_lats(itx) BS_lons(itx) tx_elevations(itx)]);
end;
% Choose the fifth station as the reference
orgxyz = tx_xyz(:,5);
% 轉ENU座標
for itx = 1:size(BS_lats,2),
    tx_enu(:,itx) = xyz2enu(tx_xyz(:,itx),orgxyz);
end;
%
rx_longitudes = (lon_bound1:0.005:lon_bound2)';
rx_latitudes = (lat_bound1:0.005:lat_bound2)';
%
for ii = 1:length(rx_longitudes),
    for jj = 1:length(rx_latitudes),
        long = rx_longitudes(ii);
        lati = rx_latitudes(jj);
        rx = rxsite('Name','iGPS Rx',...
            'Latitude',lati, ...
            'Longitude',long, ...
            'AntennaHeight',2);
        alti = elevation(rx);
        %
        rx_xyz = llh2xyz([lati long alti]);
        %
        for itx = 1:size(BS_lats,2)
            vec_enu = xyz2enu(rx_xyz,orgxyz);
            vec_view = vec_enu(1:2) - tx_enu(1:2,itx);
            Gmat(itx,:) = [vec_view'/norm(vec_view) 1];
        end
        Lmat = inv(Gmat'*Gmat);
        g2dop(ii,jj) = sqrt(trace(Lmat));
    end
end
count = sum(g2dop<=6);
count = sum(count);
percent = count/(length(rx_longitudes)*length(rx_latitudes))*100;



function xyz = llh2xyz(llh)
%mConvert from latitude, longitude and height
%         to ECEF cartesian coordinates.  WGS-84
phi = llh(1);
lambda = llh(2);
h = llh(3);
%
a = 6378137.0000;	% earth semimajor axis in meters
b = 6356752.3142;	% earth semiminor axis in meters
e = sqrt (1-(b/a).^2);
%
sinphi = sind(phi);
cosphi = cosd(phi);
coslam = cosd(lambda);
sinlam = sind(lambda);
tan2phi = (tand(phi))^2;
tmp = 1 - e*e;
tmpden = sqrt( 1 + tmp*tan2phi );
%
x = (a*coslam)/tmpden + h*coslam*cosphi;
y = (a*sinlam)/tmpden + h*sinlam*cosphi;
tmp2 = sqrt(1 - e*e*sinphi*sinphi);
z = (a*tmp*sinphi)/tmp2 + h*sinphi;
%
xyz = [x; y; z];
end

function llh = xyz2llh(xyz)
% Convert from ECEF cartesian coordinates to
%               latitude, longitude and height.  WGS-84
%
	x = xyz(1);
	y = xyz(2);
	z = xyz(3);
	x2 = x^2;
	y2 = y^2;
	z2 = z^2;

	a = 6378137.0000;	% earth radius in meters
	b = 6356752.3142;	% earth semiminor in meters
	e = sqrt (1-(b/a).^2);
	b2 = b*b;
	e2 = e^2;
	ep = e*(a/b);
	r = sqrt(x2+y2);
	r2 = r*r;
	E2 = a^2 - b^2;
	F = 54*b2*z2;
	G = r2 + (1-e2)*z2 - e2*E2;
	c = (e2*e2*F*r2)/(G*G*G);
	s = ( 1 + c + sqrt(c*c + 2*c) )^(1/3);
	P = F / (3 * (s+1/s+1)^2 * G*G);
	Q = sqrt(1+2*e2*e2*P);
	ro = -(P*e2*r)/(1+Q) + sqrt((a*a/2)*(1+1/Q) ...
                                - (P*(1-e2)*z2)/(Q*(1+Q)) - P*r2/2);
	tmp = (r - e2*ro)^2;
	U = sqrt( tmp + z2 );
	V = sqrt( tmp + (1-e2)*z2 );
	zo = (b2*z)/(a*V);

	height = U*( 1 - b2/(a*V) );

	lati = atand( (z + ep*ep*zo)/r );

	temp = atan(y/x);
	if x >=0
		long = temp;
	elseif (x < 0) & (y >= 0)
		long = pi + temp;
	else
		long = temp - pi;
	end

	llh(1) = lati;
	llh(2) = long*180/pi;
	llh(3) = height;
end


function enu = xyz2enu(xyz,orgxyz)
tmpxyz = xyz;
tmporg = orgxyz;
if size(tmpxyz) ~= size(tmporg), tmporg=tmporg'; end
difxyz = tmpxyz - tmporg;
[m,n] = size(difxyz); if m<n, difxyz=difxyz'; end
orgllh = xyz2llh(orgxyz);
phi = orgllh(1);
lam = orgllh(2);
sinphi = sind(phi);
cosphi = cosd(phi);
sinlam = sind(lam);
coslam = cosd(lam);
R = [ -sinlam          coslam         0     ; ...
      -sinphi*coslam  -sinphi*sinlam  cosphi; ...
       cosphi*coslam   cosphi*sinlam  sinphi];
enu = R*difxyz;
end

end
