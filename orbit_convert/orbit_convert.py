import glob
import os
from rubin_scheduler.data import get_data_dir
from sbpy.data import Orbit
from rubin_sim.moving_objects import Orbits
from astropy.table import Table, hstack
import astropy.units as u
from astropy.time import Time
import numpy as np
import pandas as pd
from rubin_sim.phot_utils import Bandpass, Sed


def read_filters(
    filter_dir=None,
    bandpass_root="total_",
    bandpass_suffix=".dat",
    filterlist=("u", "g", "r", "i", "z", "y"),
    v_dir=None,
    v_filter="harris_V.dat",
):
    """Read (LSST) and Harris (V) filter throughput curves.

    Only the defaults are LSST specific;
    this can easily be adapted for any survey.

    Parameters
    ----------
    filter_dir : `str`, optional
        Directory containing the filter throughput curves ('total*.dat')
        Default set by 'LSST_THROUGHPUTS_BASELINE' env variable.
    bandpass_root : `str`, optional
        Rootname of the throughput curves in filterlist.
        E.g. throughput curve names are bandpass_root + filterlist[i]
        + bandpass_suffix
        Default `total_` (appropriate for LSST throughput repo).
    bandpass_suffix : `str`, optional
        Suffix for the throughput curves in filterlist.
        Default '.dat' (appropriate for LSST throughput repo).
    filterlist : `list`, optional
        List containing the filter names to use to calculate colors.
        Default ('u', 'g', 'r', 'i', 'z', 'y')
    v_dir : `str`, optional
        Directory containing the V band throughput curve.
        Default None = $RUBIN_SIM_DATA_DIR/movingObjects
    v_filter : `str`, optional
        Name of the V band filter curve.
        Default harris_V.dat.
    """
    if filter_dir is None:
        filter_dir = os.path.join(get_data_dir(), "throughputs/baseline")
    if v_dir is None:
        v_dir = os.path.join(get_data_dir(), "movingObjects")
    # Read filter throughput curves from disk.
    bps = {}
    for f in filterlist:
        bps[f] = Bandpass()
        bps[f].read_throughput(os.path.join(filter_dir, bandpass_root + f + bandpass_suffix))
    return bps


def calc_colors(bps, f1=["u", "g", "i", "z", "y"], f2=["r", "r", "r", "r", "r"], sedname="C.dat", sed_dir=None):
    """Calculate the colors for a given SED.

    If the sedname is not already in the dictionary self.colors,
    this reads the SED from disk and calculates all V-[filter] colors
    for all filters in self.filterlist.
    The result is stored in self.colors[sedname][filter], so will not
    be recalculated if the SED + color is reused for another object.

    Parameters
    ----------
    sedname : `str`, optional
        Name of the SED. Default 'C.dat'.
    sed_dir : `str`, optional
        Directory containing the SEDs of the moving objects.
        Default None = $RUBIN_SIM_DATA_DIR/movingObjects,

    Returns
    -------
    colors : `dict` {'filter': color}}
        Dictionary of the colors in self.filterlist.
    """

    if sed_dir is None:
        sed_dir = os.path.join(get_data_dir(), "movingObjects")
    mo_sed = Sed()
    mo_sed.read_sed_flambda(os.path.join(sed_dir, sedname))

    result = {}

    for filtername1, filtername2 in zip(f1, f2):
        result["%s-%s" % (filtername1, filtername2)] = mo_sed.calc_mag(bps[filtername1]) - mo_sed.calc_mag(bps[filtername2])

    return result


if __name__ == "__main__":

    orbit_files = glob.glob(os.path.join(get_data_dir(), "orbits")+"/*.txt")

    units = {"a": u.au, "incl": u.deg, "Omega": u.deg, "w": u.deg,
             "M": u.deg, "H": u.mag, "q": u.au}

    bps = read_filters()

    for filename in orbit_files:
        rsorb = Orbits()
        rsorb.read_orbits(filename)

        # rename some columns to try and match astropy
        rsorb.orbits.rename(columns={"inc": "incl", "argPeri": "w",
                            "meanAnomaly": "M", "objId":
                            "targetname", "tPeri": "Tp"},
                            inplace=True)
        rsorb.orbits["G"] = 0

        table = Table()
        table = table.from_df(rsorb.orbits, units=units)
        table["epoch"] = Time(table["epoch"], format="mjd")
        if "Tp" in table.keys():
            table["Tp"] = Time(rsorb.orbits["Tp"], format="mjd")
        table["id"] = np.arange(table["epoch"].size)

        orbit = Orbit.from_table(table)

        orbit_kep = orbit.oo_transform('KEP') 

        # Catch if openOrb failed silently!
        a_failed_indx = np.where(orbit_kep["a"] == 0)[0]
        if np.size(a_failed_indx) > 0:
            for indx in np.arange(len(orbit_kep)):
                orbit_kep._table[indx] = orbit[indx].oo_transform('KEP')._table[0]

        outfilename = os.path.basename(filename).split(".")[0] + '_kep.csv'
        # orbit_kep.to_file(outfilename, format="ascii.csv", overwrite=True)
        sorcha_style = pd.DataFrame()
        sorcha_style["ObjID"] = np.arange(table["epoch"].size)
        sorcha_style["a"] = orbit_kep["a"].value
        sorcha_style["e"] = orbit_kep["e"].value
        sorcha_style["inc"] = orbit_kep["incl"].value
        sorcha_style["node"] = orbit_kep["Omega"].value
        sorcha_style["argPeri"] = orbit_kep["w"].value
        sorcha_style["ma"] = orbit_kep["M"].value
        sorcha_style["epochMJD_TDB"] = orbit_kep["epoch"].value
        sorcha_style["FORMAT"] = "KEP"

        ack = np.where(sorcha_style["e"] >= 1)[0]
        good_orbits = np.where(sorcha_style["e"] < 1)[0]

        # Going to fudge wacky orbits that have e > 1
        if len(ack) > 0:
            if len(ack) > 1:
                sorcha_style = sorcha_style.iloc[good_orbits]
            else:
                for indx in ack:
                    sorcha_style.loc[indx, "e"] = .9999
                    sorcha_style.loc[indx, "ma"] = 359.

        sorcha_style.to_csv(outfilename, index=False, sep=" ")

        # Now need to write a params file

        params = pd.DataFrame()
        params["ObjID"] = table["id"]

        params["H_r"] = 4.
        params["GS"] = 0.15

        sed_names = np.unique(rsorb.orbits["sed_filename"])

        params["u-r"] = 0.
        params["g-r"] = 0.
        params["i-r"] = 0.
        params["z-r"] = 0.
        params["y-r"] = 0.

        for sed_name in sed_names:
            colors = calc_colors(bps, sedname=sed_name)

            indx = np.where(rsorb.orbits["sed_filename"].values == sed_name)[0]

            params.loc[indx, "u-r"] = colors["u-r"]
            params.loc[indx, "g-r"] = colors["g-r"]
            params.loc[indx, "i-r"] = colors["i-r"]
            params.loc[indx, "z-r"] = colors["z-r"]
            params.loc[indx, "y-r"] = colors["y-r"]

        params = params.iloc[good_orbits]

        params.to_csv(os.path.basename(filename).split(".")[0] + '_param.csv', index=False, sep=" ")

