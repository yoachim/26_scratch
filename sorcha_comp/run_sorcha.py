import rubin_sim.splat as splat
from rubin_sim.data import get_data_dir
import glob

if __name__ == "__main__":

    dd = get_data_dir()
    baseline_file = "comp_survey_v5.3.0_10yrs.db"

    orbit_files = glob.glob(dd + "/sorcha/*_kep.csv")
    color_files = [filename.replace("kep", "param") for filename in orbit_files]

    for of, cf in zip(orbit_files, color_files):
        print("computing sorcha on %s" % of)
        observations, stats = splat.solar_system.sorcha_wrapper(
            baseline_file, of, cf
        )

        outfile = of.replace("_kep.csv", "")

        observations.to_csv("sorcha_obs_" + outfile + ".csv")
        stats.to_csv("sorcha_stats_" + outfile + ".csv")

