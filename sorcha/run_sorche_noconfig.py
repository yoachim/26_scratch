
from sorcha.sorcha import runLSSTSimulation
from sorcha.utilities.sorchaConfigs import (inputConfigs, simulationConfigs,
                                            filtersConfigs, saturationConfigs,
                                            phasecurvesConfigs, fovConfigs,
                                            fadingfunctionConfigs, linkingfilterConfigs,
                                            outputConfigs, lightcurveConfigs, activityConfigs,
                                            expertConfigs, auxiliaryConfigs, basesorchaConfigs)
from sorcha.utilities.sorchaArguments import sorchaArguments


if __name__ == "__main__":

    pointing_database = "baseline_v2.0_1yr.db"
    orbin_file = "sspp_testset_orbits.des"
    params = "sspp_testset_colours.txt"
    stats_out_file = "nofile_test_stats"

    query = ("SELECT observationId, observationStartMJD as observationStartMJD_TAI, "
             "visitTime, visitExposureTime, filter, seeingFwhmGeom as seeingFwhmGeom_arcsec, "
             "seeingFwhmEff as seeingFwhmEff_arcsec, fiveSigmaDepth as fieldFiveSigmaDepth_mag , "
             "fieldRA as fieldRA_deg, fieldDec as fieldDec_deg, rotSkyPos as "
             "fieldRotSkyPos_deg FROM observations order by observationId")

    ephemerides_type = "ar"
    survey_name = "rubin_sim"
    observing_filters = "r,g,i,z,u,y"

    input_config = inputConfigs(ephemerides_type=ephemerides_type,
                                eph_format="csv",
                                size_serial_chunk=5000,
                                aux_format="whitespace",
                                pointing_sql_query=query)

    simulation_config = simulationConfigs(ar_ang_fov=2.06,
                                          ar_fov_buffer=0.2,
                                          ar_picket=1,
                                          ar_obs_code="X05",
                                          ar_healpix_order=6,
                                          ar_n_sub_intervals=101,
                                          _ephemerides_type=ephemerides_type)

    filters_config = filtersConfigs(observing_filters=observing_filters,
                                    survey_name=survey_name,
                                    mainfilter=None,
                                    othercolours=None)

    saturation_config = saturationConfigs(bright_limit_on=True,
                                          bright_limit=16.0,
                                          _observing_filters=observing_filters)

    phasecurves_config = phasecurvesConfigs(phase_function="HG")

    fov_config = fovConfigs(camera_model="footprint",
                            footprint_path=None,
                            fill_factor=None,
                            circle_radius=None,
                            footprint_edge_threshold=2.,
                            survey_name=survey_name)

    fading_config = fadingfunctionConfigs(fading_function_on=True,
                                          fading_function_width=0.1,
                                          fading_function_peak_efficiency=1.)

    linking_config = linkingfilterConfigs(ssp_linking_on=True,
                                          drop_unlinked=False,
                                          ssp_detection_efficiency=0.95,
                                          ssp_number_observations=2,
                                          ssp_separation_threshold=0.5,
                                          ssp_maximum_time=0.0625,
                                          ssp_number_tracklets=3,
                                          ssp_track_window=15,
                                          ssp_night_start_utc=16.0)
    output_confg = outputConfigs(output_format="csv",
                                 output_columns="basic",
                                 position_decimals=None,
                                 magnitude_decimals=None)

    lightcurve_config = lightcurveConfigs(lc_model=None)

    activity_config = activityConfigs(comet_activity=None)

    expert_config = expertConfigs()

    aux_config = auxiliaryConfigs()

    config = basesorchaConfigs(survey_name=survey_name,
                               input=input_config,
                               simulation=simulation_config,
                               filters=filters_config,
                               saturation=saturation_config,
                               phasecurves=phasecurves_config,
                               fov=fov_config,
                               fadingfunction=fading_config,
                               linkingfilter=linking_config,
                               output=output_confg,
                               lightcurve=lightcurve_config,
                               activity=activity_config,
                               expert=expert_config,
                               auxiliary=aux_config,
                                 )

    sorcha_args = sorchaArguments(cmd_args_dict={"paramsinput": params,
                                                 "orbinfile": orbin_file,
                                                 "input_ephemeris_file": None,
                                                 "configfile": "sspp_testset_colours.txt",
                                                 "outpath": "./",
                                                 "outfilestem": "nofile_test",
                                                 "pointing_database": pointing_database,
                                                 "output_ephemeris_file": None,
                                                 "ar_data_path": None,
                                                 "loglevel": None,
                                                 "stats": stats_out_file,
                                                 "surveyname": survey_name,
                                                 "seed": 42})


    observations, stats = runLSSTSimulation(sorcha_args, config, return_only=True)

    # to get how many were linked:
    n_linked = stats.groupby("ObjID").agg(any_linked=("object_linked", "any")).values.sum()

    import pdb ; pdb.set_trace()
