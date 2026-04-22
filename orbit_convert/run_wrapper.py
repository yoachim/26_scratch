from sorcha_wrapper import sorcha_wrapper
import glob
import datetime


if __name__ == "__main__":

    pointing_database = "baseline_v5.1.2_10yrs.db"

    orbit_files = glob.glob("*_kep.csv")
    orbit_files.sort()

    # XXX
    #orbit_files = [filename for filename in orbit_files if "vatiras" in filename]

    for orbit_file in orbit_files:
        start_time = datetime.datetime.now()
        print("starting ", orbit_file, start_time)
        params = orbit_file.replace("kep", "param")

        sorcha_obs, sorcha_stats = sorcha_wrapper(pointing_database,
                                                  orbit_file, params)

        end_time = datetime.datetime.now()
        diff = end_time - start_time
        print("ran %s, %s in %.1f minutes" % (pointing_database, orbit_file, diff.seconds/60.))

        rootname = orbit_file.split("_kep")[0]

        sorcha_obs.to_csv("sorcha_frames/" + rootname + "_obs.csv")
        sorcha_obs.to_csv("sorcha_frames/" + rootname + "_stats.csv")