Testing out sorcha

conda install seemed to be fast and easy

sorcha run -c sorcha_config_demo.ini -p sspp_testset_colours.txt --orbits sspp_testset_orbits.des --pointing-db baseline_v2.0_1yr.db -o ./ -t testrun_e2e --stats testrun_stats

ok, it's putting about a gig of files in /Users/yoachim/Library/Caches/sorcha

looks like the test on 1-year takes 21.5 sec

time sorcha run -c sorcha_config_demo.ini -p sspp_testset_colours.txt --orbits sspp_testset_orbits.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t testrun_10y_e2e --stats testrun_10y_stats

3:01 total


let's try the ephem generation

time sorcha run -c sorcha_config_demo.ini -p sspp_testset_colours.txt --orbits sspp_testset_orbits.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t testrun_10y_e2e --stats testrun_10y_stats --ew testrun_10t_eph -f


generated 2M file testrun_10t_eph.h5


run with the saved ephem:
time sorcha run -c sorcha_config_demo_read.ini -p sspp_testset_colours.txt --orbits sspp_testset_orbits.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t testrun_10y_e2e --stats testrun_10y_stats --er testrun_10t_eph.h5 -f

that took 7 minutes? wtf?


How long to run a orbit file I already have?

time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v2.0_1yr.db -o ./ -t gran_1y --stats gran_1y_stats -f 

2:15.48 total



time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t gran_10y --stats gran_10y_stats -f

looks like this gets up to 2.8GB (and creeping up)
21:25.22 total



should test again with writing the ephemeridies then reading them in

time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t gran_10y --stats gran_10y_stats -f --ew gran_10_eph

21:47.99 total


time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t gran_10y --stats gran_10y_stats -f --er gran_10_eph.h5

20:56.95 total

wow, only shaved a minute off. That's pretty wild.

-----

let's time test movingObjects

with pre-computed orbits:

time make_lsst_obs --simulation_db baseline_v5.1.2_10yrs.db --orbit_file /Users/yoachim/rubin_sim_data/orbits/granvik_5k.txt --positions_file /Users/yoachim/rubin_sim_data/orbits_precompute/granvik_5k.npz

17:40.86 total


w/o pre-computed positions
time make_lsst_obs --simulation_db baseline_v5.1.2_10yrs.db --orbit_file /Users/yoachim/rubin_sim_data/orbits/granvik_5k.txt

58:00.23 total


time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t gran_10y -f 

21:10.28 total


time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t gran_10y -f --er gran_10_eph.h5

21:12.18 total
generates 910871 observations, compared to 1504084 in the moving objects.

----
running again with H=0, and simple objID

time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t gran_10y 

20:56.84 total. But didn't output? 

ok, going back to H=12 gets me 910955

so probably something with the seed going on as well. 

What happens if we go H=5?

time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t gran_10y_b

no output.

ok, so let's try H=15. 
time sorcha run -c sorcha_config_demo_read.ini -p granvik_5k_params.txt --orbits granvik_5k.des --pointing-db baseline_v5.1.2_10yrs.db -o ./ -t gran_10y_b

ok, that got me a file. And much bigger.

