from dataclasses import dataclass

@dataclass
class Config:
    BS_num : int
    height : int
    width : int
    DOP_thres : int
    cov_thres : int
    dir_name : str
