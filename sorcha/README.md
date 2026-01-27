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
