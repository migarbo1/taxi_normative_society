import matplotlib.pyplot as plt

# pick clients
#(math.pow(math.e, agent.total_time/1000) / math.pow(math.e, constants['simulation_time'])) * (1 - agent.earned_money/get_max_possible_money())

# jump queue
# random.random() < (1 - math.pow(math.e, (agent.sucessful_pickup_count * compute_expected_time_per_job())/1000) / math.pow(math.e, agent.total_time))

# working will
# 1 - self.earned_money/(self.total_time*1000*money_per_time)

import numpy as np
import math

total_exec_time = 1400
n_jobs = np.arange(0, 8, 1)
current_times = np.arange(0, 1440, 1)

def y(n):
    y = []
    for t in current_times:
        y.append(
            max(1 - math.pow(math.e, (n * 131)/1000) / math.pow(math.e, t/1000), 0)
            # max((math.pow(math.e, t/1000) / math.pow(math.e, total_exec_time/1000)) * (1 - (n*131)/(n_jobs[-1]*131)), 0)
        )
    return y

for j in n_jobs:
    plt.plot(current_times, y(j), label=f'{j} jobs done')
plt.legend()
plt.ylabel('Break norm score')
plt.xlabel('Time')
plt.title('Jump queue decision function')
plt.show()