#!/bin/bash

source venv/Scripts/activate

for j in 0 1 2
do
    for i in {1..100}
    do
        python main.py $j > "results_run_{$i}.out"
    done
    printf "agent_type,earned_money,reputation,jobs_lost,jobs_done,time_worked\n" > results_{$j}.csv
    cat results_run_*.out >> "results_{$j}.csv"
    rm results_run_*.out
done
deactivate