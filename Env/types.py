from dataclasses import dataclass

@dataclass
class Config:
    BS_num : int
    height : int
    width : int
    lat_min : float
    lat_max : float
    lon_min : float
    lon_max : float
    grid_step_size : float
    DOP_thres : int
    cov_thres : int
    dir_name : str
