import time

print("RAM AT START: {:01.f} MiB".format(
    memory_profiler.memory_usage()[0]
))

t1 = time.perf_counter()

words = [w for w in text_example.readers]
print("Loading {0} words".format(len(words)))

t2 = time.perf_counter()

print("RAM after cerating list {:0.1f} MiB, took {:0.1f} s".format(
    memory_profiler.memory_usage()[0], t2 - t1
))