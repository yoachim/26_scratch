import numpy as np
import glob
from rubin_sim.data import get_baseline
import sqlite3
import pandas as pd


if __name__ == "__main__":

    save_files = glob.glob("*.npz")

    baseline_file = get_baseline()
    conn = sqlite3.connect(baseline_file)
    query = ("select * from observations where night < 365;")
    visits = pd.read_sql(query, conn)
    conn.close()

    lengths = []
    streaks = []
    mjds = []

    for filename in save_files:
        _temp = np.load(filename, allow_pickle=True)
        if not None in _temp["n_streaks"] :
            lengths.append(_temp["lengths_deg"].copy())
            streaks.append(_temp["n_streaks"].copy())
            mjds.append(_temp["mjd"])
            scale = _temp["scale"]


    lengths = np.concatenate(lengths, axis=0)
    streaks = np.concatenate(streaks)
    mjds = np.concatenate(mjds)

    mjd_order = np.argsort(mjds)

    lengths = lengths[mjd_order]
    streaks = streaks[mjd_order]
    mjds = mjds[mjd_order]

    diff = visits["observationStartMJD"] - mjds

    if np.max(np.abs(diff)) > 1e-6:
        raise ValueError("MJDs do not match")

    visits["streak_lengths"] = lengths
    visits["n_streaks"] = streaks

    outfile = "baseline_w_streaks_scale%i.sql" % scale

    con = sqlite3.connect(outfile)
    visits.to_sql("observations", con)
    # If I was good I'd port over the info table too.
    info = pd.read_sql("select * from info;", con)
    info.to_sql("info", con)
    con.close()

