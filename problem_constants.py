constants = {
    'simulation_time': 7*24*60e-3,
    
    'num_of_agents' : 10,
    
    'queue_waittime': 10e-3,
    
    'client_waittime_lb': 5e-3,
    'client_waittime_ub': 15e-3,
    
    'trip_lb' : 30e-3,
    'trip_ub' : 90e-3,
    
    'rest_lb': 5e-3,
    'rest_ub': 15e-3,
    
    'max_working_time': 480e-3,
    'min_resting_time': 30e-3,
    
    'long_local_trip_time': 50e-3,
    'short_local_trip_time': 30e-3,
    'intercity_trip_time': 70e-3,
    
    'return_time_proportion': 0.85,

    'long_local_trip_fare' : 0.41,
    'short_local_trip_fare': 0.41,
    'intercity_trip_fare': 0.41
}


def compute_num_shifts_in_simulation():
    return constants['simulation_time']/constants['max_working_time']


def compute_expected_time_per_job():
    # num_shifts_in_simulation = compute_num_shifts_in_simulation()
    return constants['queue_waittime']*constants['num_of_agents'] + \
        (constants['client_waittime_lb'] + constants['client_waittime_ub'])/2 + \
        (constants['trip_lb'] + constants['trip_ub'])/2 + \
        (constants['trip_lb'] + constants['trip_ub'])/2 * constants['return_time_proportion'] + \
        constants['min_resting_time']


def compute_expected_money_per_job():
    return ((constants['trip_lb'] + constants['trip_ub'])/2) * constants['long_local_trip_fare']


def get_max_possible_money():
    num_shifts_in_simulation = compute_num_shifts_in_simulation()
    expected_time_per_job = compute_expected_time_per_job()
    
    num_jobs_per_shift = constants['max_working_time']/expected_time_per_job

    expected_money_per_job = (constants['trip_ub'] + constants['trip_lb'] )/2 * \
        (constants['long_local_trip_fare'] + constants['short_local_trip_fare'] + constants['intercity_trip_fare'])/3
    
    return expected_money_per_job * num_shifts_in_simulation * num_jobs_per_shift

