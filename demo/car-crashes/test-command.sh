crashed pipelines crashed_pipeline select_into \
    --sql "SELECT inj_or_fatal,fatality,males,females,driver,pedestrian,old_driver,young_driver,unlicencsed,heavyvehicle,passengervehicle,motorcycle,accident_time,accident_type,day_of_week,dca_code,hit_run_flag,light_condition,road_geometry,speed_zone,alcohol_related FROM crashed.crashes_raw WHERE accident_date BETWEEN '2013-01-01' AND '2017-12-31'" \
    --output_dataset "crashed" \
    --output_table "crashes_training"