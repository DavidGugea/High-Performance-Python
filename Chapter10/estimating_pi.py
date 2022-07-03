import time
import random
import ipyparallel as ipp
from ipyparallel import require


@require("random")
def estimate_nbr_points_in_quarter_circle(nbr_estimates):
    nbr_trials_in_quarter_unit_circle = 0

    for step in range(int(nbr_estimates)):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)

        is_in_unit_circle = x * x + y * y <= 1.0
        nbr_trials_in_quarter_unit_circle += is_in_unit_circle

    return nbr_trials_in_quarter_unit_circle


if __name__ == '__main__':
    c = ipp.Client()
    nbr_engines = len(c.ids)
    print("We're using {0} engines".format(nbr_engines))
    nbr_samples_in_total = 1e8
    nbr_parallel_blocks = 4

    dview = c[:]

    nbr_samples_per_worker = nbr_samples_in_total / nbr_parallel_blocks
    t1 = time.perf_counter()
    nbr_in_quarter_unit_circles = dview.apply_sync(estimate_nbr_points_in_quarter_circle, nbr_samples_per_worker)
    print("Estimates made: {0}".format(nbr_in_quarter_unit_circles))

    nbr_jobs = len(nbr_in_quarter_unit_circles)
    pi_estimate = sum(nbr_in_quarter_unit_circles) * 4 / nbr_samples_in_total
    print("Estimated pi {0}".format(pi_estimate))
    print("Delta: {)}".format(time.perf_counter() - t1))
