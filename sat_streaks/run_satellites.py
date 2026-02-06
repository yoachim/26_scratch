import argparse
import sqlite3

import numpy as np
import pandas as pd
from astropy import units as u
from rubin_sim.data import get_baseline
from rubin_sim.satellite_constellations import Constellation, create_constellation
from rubin_scheduler.utils import SURVEY_START_MJD


def read_sats(filename="sats.dat", epoch=23274.0):

    planned = pd.read_csv(filename, comment="#", sep="\\s+")
    tles = create_constellation(
        planned["Altitude"].values * u.km,
        planned["Inclination"].values * u.deg,
        planned["No_of_planes"].values,
        planned["Sats_per_plane"].values,
        epoch=epoch,
        name="mega",
        seed=42,
    )
    return tles


if __name__ == "__main__":

    epoch = SURVEY_START_MJD
    parser = argparse.ArgumentParser()
    parser.add_argument("--night", type=int, default=0)
    args = parser.parse_args()

    night = args.night

    baseline_file = get_baseline()
    conn = sqlite3.connect(baseline_file)
    query = (
        "select fieldRA, fieldDec, observationStartMJD, visitTimefrom observations where night = %i;"
        % night
    )
    visits = pd.read_sql(query, conn)
    conn.close()

    tles = read_sats(epoch=epoch)
    constellation = Constellation(tles)

    lengths_deg, n_streaks = constellation.check_pointings(
        visits["fieldRA"].values,
        visits["fieldDec"].values,
        visits["observationStartMJD"].values,
        visits["visitTime"].values,
    )

    np.savez(
        "sat_streak_results_%i.npz" % night,
        lengths_deg=lengths_deg,
        n_streaks=n_streaks,
        mjd=visits["observationStartMJD"].values,
    )
