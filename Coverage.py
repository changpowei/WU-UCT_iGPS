from collections import Counter
import math


class Coverage:

    def __init__(self, lat_min, lat_max, lon_min, lon_max, step_size):
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.step_size = step_size
        self.file_folder = './data/BS_data_building_NCSIST/'

    def read_data(self, file_loc, lat_min, lat_max, lon_min, lon_max):
        all_position = []
        origin_all_posistions = []
        for one_loc in file_loc:
            with open(one_loc) as f:
                lines = f.readlines()
                origin_all_posistions += lines
                for line in lines:
                    line = line.strip()
                    latitude = float(line.split(',')[0])
                    longitude = float(line.split(',')[1])
                    if latitude >= lat_min and latitude <= lat_max and longitude >= lon_min and longitude <= lon_max:
                        all_position.append(line)
        return all_position

    def duplicate_count(self, position_list):
        counts = dict(Counter(position_list))
        duplicates = {key: value for key, value in counts.items() if value >= 3}
        return duplicates

    def coverage(self, duplicate_numbers, grid_numbers):
        return (duplicate_numbers * 100) / grid_numbers

    def compute_coverage(self, actions):

        file_loc = []
        for action in actions:
            file_loc.append(self.file_folder + 'BS_{}.txt'.format(action + 1))

        lat_step_count = math.ceil((self.lat_max - self.lat_min) / self.step_size)
        lon_step_count = math.ceil((self.lon_max - self.lon_min) / self.step_size)
        grid_numbers = lat_step_count * lon_step_count

        all_position = self.read_data(file_loc, self.lat_min, self.lat_max, self.lon_min, self.lon_max)
        duplicates = self.duplicate_count(all_position)
        coverage_rate = self.coverage(len(duplicates), grid_numbers)
        # print(coverage_rate)

        return coverage_rate