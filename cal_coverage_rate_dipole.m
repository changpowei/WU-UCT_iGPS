function [coverage_rate] = cal_coverage_rate(BS_lats, BS_lons);

divide_decimal = 2;
grid_area = 2385;
lat_bound1 = 24.59; lat_bound2 = 25.11;
lon_bound1 = 120.98; lon_bound2 = 121.41;

txs_sinr_all = [];
height_txs_sinr = [];

for j = 1:size(BS_lats, 2)
    txs_sinr = [];

    txs = txsite('Name', "Antenna", ...
                    'Latitude', BS_lats(j), ...
                    'Longitude', BS_lons(j), ...
                    'Antenna', dipole, ...
                    'TransmitterFrequency', 37.5e7, ...
                    'TransmitterPower', 50);

    txs_sinr = sinr(txs);
    txs_sinr = txs_sinr.Data;

    % 刪除所有SINR小於3的row
    toDelete = txs_sinr.SINR < 3;
    txs_sinr(toDelete,:) = [];
    txs_sinr.Longitude = round(txs_sinr.Longitude,divide_decimal);
    txs_sinr.Latitude = round(txs_sinr.Latitude,divide_decimal);
    txs_sinr = unique(txs_sinr(:,1:2)); % 去除重複資料
    height_txs_sinr(j) = height(txs_sinr);
    txs_sinr_all = [txs_sinr_all;txs_sinr];
end

txs_sinr_all = table2array(txs_sinr_all);
% 計算與分析覆蓋面積
txs_sinr_all_string = arrayfun(@num2str,txs_sinr_all,'un',0); % 轉換成string array
txs_sinr_all_string = strcat(txs_sinr_all_string(:,1),",",txs_sinr_all_string(:,2)); % 將經緯度結合成string
signal_statistics = convertCharsToStrings(tabulate(txs_sinr_all_string));

signals_num_1=[]; signals_num_2=[]; signals_num_3=[]; signals_num_4=[];
for k = 1:height(signal_statistics)
    if(signal_statistics{k,2})==1
        signals_num_1(height(signals_num_1)+1,1:2) = str2double(strsplit(signal_statistics{k,1},','));
    elseif(signal_statistics{k,2})==2
        signals_num_2(height(signals_num_2)+1,1:2) = str2double(strsplit(signal_statistics{k,1},','));
    elseif(signal_statistics{k,2})==3
        signals_num_3(height(signals_num_3)+1,1:2) = str2double(strsplit(signal_statistics{k,1},','));
    else
        signals_num_4(height(signals_num_4)+1,1:2) = str2double(strsplit(signal_statistics{k,1},','));
    end
end

signals_num_1=[]; signals_num_2=[]; signals_num_3=[]; signals_num_4=[];
for k = 1:height(signal_statistics)
    if(signal_statistics{k,2})==1
        signals_num_1(height(signals_num_1)+1,1:2) = str2double(strsplit(signal_statistics{k,1},','));
    elseif(signal_statistics{k,2})==2
        signals_num_2(height(signals_num_2)+1,1:2) = str2double(strsplit(signal_statistics{k,1},','));
    elseif(signal_statistics{k,2})==3
        signals_num_3(height(signals_num_3)+1,1:2) = str2double(strsplit(signal_statistics{k,1},','));
    else
        signals_num_4(height(signals_num_4)+1,1:2) = str2double(strsplit(signal_statistics{k,1},','));
    end
end

% 將被三個以上訊號覆蓋的點結合,並刪除超出網格邊界的row
location_point = [signals_num_3;signals_num_4];
if (isempty(location_point) == 1)
    coverage_rate = 0;
else
    toDelete = ((location_point(:,1)>=lat_bound1 & location_point(:,1)<=lat_bound2) & ...
                  (location_point(:,2)>=lon_bound1 & location_point(:,2)<=lon_bound2));  % 在網格邊界內的row=1
    location_point(~toDelete,:) = [];

    coverage_rate = (height(location_point)/grid_area)*100;
end
