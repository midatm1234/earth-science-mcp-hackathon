"""Build the tiny synthetic SWOT-like NetCDF file that the tests use. Run by the tests; no network.

Layout follows the CMR variable metadata of SWOT_L2_LR_SSH_D (Basic): groups 'left' and 'right', each with
latitude, longitude (0..360), ssh_karin (m), ssh_karin_qual (0 = no flag) on a num_lines x num_pixels grid.
The values are INVENTED for testing and are not SWOT measurements.
"""

from pathlib import Path

import numpy as np
from netCDF4 import Dataset

FILL = 2147483647


def build(path: Path) -> None:
    with Dataset(path, "w") as ds:
        for side, lon0 in (("left", 235.0), ("right", 235.4)):
            g = ds.createGroup(side)
            g.createDimension("num_lines", 4)
            g.createDimension("num_pixels", 3)
            lat = g.createVariable("latitude", "f8", ("num_lines", "num_pixels"))
            lon = g.createVariable("longitude", "f8", ("num_lines", "num_pixels"))
            ssh = g.createVariable("ssh_karin", "i4", ("num_lines", "num_pixels"), fill_value=FILL)
            qual = g.createVariable("ssh_karin_qual", "u4", ("num_lines", "num_pixels"))
            ssh.scale_factor = 0.001
            lat[:] = np.repeat(np.arange(34.0, 38.0, 1.0), 3).reshape(4, 3)
            lon[:] = lon0 + np.tile(np.arange(3) * 0.1, (4, 1))  # 235.0 -> -125.0 in -180..180
            values = (np.arange(12).reshape(4, 3) * 10 + 100) * 0.001  # physical metres 0.100 .. 0.210; stored as raw 100 .. 210
            ssh[:] = np.ma.masked_array(values, mask=False)
            q = np.zeros((4, 3), dtype="u4")
            if side == "left":
                ssh[0, 0] = np.ma.masked   # one fill value
                q[1, 1] = 4                # one flagged point
            qual[:] = q
