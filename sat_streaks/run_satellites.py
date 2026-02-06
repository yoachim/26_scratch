import argparse
import sqlite3

import numpy as np
import pandas as pd
from astropy import units as u
from rubin_sim.data import get_baseline
from rubin_sim.satellite_constellations import Constellation, create_constellation
from rubin_scheduler.utils import SURVEY_START_MJD


def read_sats(filename="sats.dat", epoch=23274.0, scale_down=5):
    """

    Parameters
    ----------
    scale_down : int
        Factor to scale down the Sats_per_plane value.
    """

    planned = pd.read_csv(filename, comment="#", sep="\\s+")
    tles = create_constellation(
        planned["Altitude"].values * u.km,
        planned["Inclination"].values * u.deg,
        planned["No_of_planes"].values,
        (planned["Sats_per_plane"].values/scale_down).astype(int),
        epoch=epoch,
        name="mega",
        seed=42,
    )
    return tles


if __name__ == "__main__":

    epoch = SURVEY_START_MJD
    parser = argparse.ArgumentParser()
    parser.add_argument("--night", type=int, default=0)
    parser.add_argument("--scale", type=int, default=5)

    args = parser.parse_args()

    night = args.night
    scale = args.scale

    baseline_file = get_baseline()
    conn = sqlite3.connect(baseline_file)
    query = (
        "select fieldRA, fieldDec, observationStartMJD, visitTime from observations where night = %i;"
        % night
    )
    visits = pd.read_sql(query, conn)
    conn.close()

    if len(visits) > 0:
        tles = read_sats(epoch=epoch, scale_down=scale)
        constellation = Constellation(tles)

        lengths_deg, n_streaks = constellation.check_pointings(
            visits["fieldRA"].values,
            visits["fieldDec"].values,
            visits["observationStartMJD"].values,
            visits["visitTime"].values,
        )
        mjd = visits["observationStartMJD"].values
    else:
        lengths_deg = None
        n_streaks = None
        mjd = None

    np.savez(
        "sat_streak_results_%i.npz" % night,
        lengths_deg=lengths_deg,
        n_streaks=n_streaks,
        mjd=mjd,
        scale=scale
    )
