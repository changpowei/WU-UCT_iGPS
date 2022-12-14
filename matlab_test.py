import numpy as np
import matlab.engine
eng = matlab.engine.start_matlab()

if __name__ == "__main__":
    BS_lats = np.array([24.3106260175688,24.39008045,24.8704374680758,0.0])
    BS_lons =  np.array([120.949571652075,121.563320928845,121.160116378823,0.0])

    lats = matlab.double(BS_lats.tolist())
    lons = matlab.double(BS_lons.tolist())

    test_x = np.array([1, 2, 3, 4])
    test_y = np.array([4, 3, 2, 1])

    test_x = matlab.int8(test_x.tolist())
    test_y = matlab.int8(test_y.tolist())

    coverage_rate = eng.cal_coverage_rate_dipole_northern(lats, lons,nargout=1)
    print(coverage_rate)
    print("Fuck")