"""
Data Structures Assignment

Usage examples
--------------
# Part B – completely random arrays:
    python3 run_experiments.py -a 1 2 5 -s 100 500 1000 3000 -r 20

# Part C – nearly sorted arrays (5 % noise):
    python3 run_experiments.py -a 1 2 5 -s 100 500 1000 3000 -e 1 -r 20

# Part C – nearly sorted arrays (20 % noise):
    python3 run_experiments.py -a 1 2 5 -s 100 500 1000 3000 -e 2 -r 20
"""

import argparse
import random
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Sorting Algorithm
# ---------------------------------------------------------------------------

def bubble_sort(arr):
    """
    Bubble Sort (ID=1)

    Repeatedly steps through the list, compares adjacent elements, and swaps
    them if they are in the wrong order. Orders last to first.
	The `swapped` flag:	If no swaps occur during a full pass the list is already sorted, exit will occur

    Time complexity:
        Worst / Average: O(N^2)
        Best (sorted):   O(N)
    """

    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def selection_sort(arr):
    """
    Selection Sort (ID=2)

    Divides input into a sorted prefix and an unsorted suffix.  In each
    iteration it finds the minimum element from the unsorted part and moves
    it to the end of the sorted part.

    Time complexity: O(N^2)
        (Always performs the same number of comparisons regardless of input.)
    """

    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def quick_sort(arr):
    """
    Quick Sort (ID=5)

    Wrapper that calls the in-place recursive helper on the full array.

    Time complexity:
        Worst:   O(N^2)
        Average: O(N log N)
    """
    _quick_sort_helper(arr, 0, len(arr) - 1)
    return arr

def _quick_sort_helper(arr, low, high):
    """Recursive Quick Sort Algorithm"""
    if low < high:
        pivot_index = _partition(arr, low, high)
        _quick_sort_helper(arr, low, pivot_index - 1)
        _quick_sort_helper(arr, pivot_index + 1, high)

def _partition(arr, low, high):
    """
    Lomuto partition scheme with randomised pivot.

    A random pivot is chosen and swapped to the end to avoid worst-case
    behaviour on already-sorted or nearly-sorted inputs.
    """
    # Choose a random pivot and move it to the end
    pivot_idx = random.randint(low, high)
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]

    pivot = arr[high]
    i = low - 1  # i tracks the boundary of elements <= pivot

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    # Place the pivot in its correct sorted position
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Algorithm IDs

ALGORITHMS = {
    1: ("Bubble Sort",    bubble_sort),
    2: ("Selection Sort", selection_sort),
    5: ("Quick Sort",     quick_sort),
}





# ---------------------------------------------------------------------------
# Array Generation Helpers
# ---------------------------------------------------------------------------

def generate_random_array(size):
    """Return a list of random integers in [0, 1000000]."""
    return [random.randint(0, 1000000) for _ in range(size)]


def generate_nearly_sorted_array(size, noise_fraction):
    """
    Steps:
        1. Create a sorted array [0, 1, ..., size-1].
        2. k = int(size * noise_fraction) – the number of random swaps.
    """
    arr = list(range(size))
    num_swaps = int(size * noise_fraction)
    for _ in range(num_swaps):
        i = random.randint(0, size - 1)
        j = random.randint(0, size - 1)
        arr[i], arr[j] = arr[j], arr[i]
    return arr





# ---------------------------------------------------------------------------
# Benchmarking
# ---------------------------------------------------------------------------

def benchmark(algo_ids, sizes, repetitions, experiment_type):
    """
    Run the sorting experiments and return timing statistics.

    Parameters
    ----------
    algo_ids : list[int]
        Algorithm IDs to benchmark (keys in ALGORITHMS).

    sizes : list[int]
        Array sizes to test.

    repetitions : int
        How many times to repeat each (algorithm, size) pair.

    experiment_type : int / None
        None  -> fully random arrays (Part B).
        1     -> nearly sorted, 5 % noise (Part C).
        2     -> nearly sorted, 20 % noise (Part C).

    Returns
    -------
    results : dict
        {algo_id: {"mean": np.array, "std": np.array}} keyed by algo_id,
        where each array has one entry per size.
    """

    # Decide array generation strategy
    if experiment_type == 1:
        noise = 0.05
        gen_array = lambda s: generate_nearly_sorted_array(s, noise)
    elif experiment_type == 2:
        noise = 0.20
        gen_array = lambda s: generate_nearly_sorted_array(s, noise)
    else:
        gen_array = generate_random_array

    results = {}

    for algo_id in algo_ids:
        algo_name, algo_func = ALGORITHMS[algo_id]
        means = []
        stds = []

        for size in sizes:
            times = []
            for _ in range(repetitions):
                arr = gen_array(size)

                start = time.perf_counter()
                algo_func(arr)
                elapsed = time.perf_counter() - start
                times.append(elapsed)

            means.append(np.mean(times))
            stds.append(np.std(times))

        results[algo_id] = {"mean": np.array(means), "std": np.array(stds)}
        print(f"  ✓ {algo_name} done")

    return results





# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_results(results, sizes, experiment_type):
    """
    result1.png  – random arrays (Part B)
    result2.png  – nearly-sorted arrays (Part C)
    """

    plt.figure(figsize=(10, 6))

    # One line + shaded region per algorithm
    for algo_id, data in results.items():
        algo_name = ALGORITHMS[algo_id][0]
        mean = data["mean"]
        std = data["std"]

        plt.plot(sizes, mean, marker="o", label=algo_name)
        plt.fill_between(sizes, mean - std, mean + std, alpha=0.2)

    plt.xlabel("Array size (n)")
    plt.ylabel("Runtime (seconds)")

    # Build a descriptive title
    if experiment_type is None:
        title = "Sorting Benchmark – Random Arrays"
        filename = "result1.png"
    elif experiment_type == 1:
        title = "Sorting Benchmark – Nearly Sorted (5% noise)"
        filename = "result2.png"
    else:
        title = "Sorting Benchmark – Nearly Sorted (20% noise)"
        filename = "result2.png"

    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

    print(f"\nPlot saved as {filename}")





# ---------------------------------------------------------------------------
# Command Line Interface
# ---------------------------------------------------------------------------

def parse_args():
    """
    Parse command-line arguments.

    Flags
    -----
    -a : algorithm IDs          (required, one or more from {1, 2, 5})
    -s : array sizes            (required, one or more positive integers)
    -e : experiment type        (optional; 1 = 5% noise, 2 = 20% noise)
    -r : number of repetitions  (required, positive integer)
    """

    parser = argparse.ArgumentParser(
        description="Sorting algorithm benchmarking tool for Data Structures course."
    )

    parser.add_argument(
        "-a",
        type=int,
        nargs="+",
        required=True,
        choices=sorted(ALGORITHMS.keys()),
        help="Algorithm IDs to compare (e.g. 1 2 5).",
    )

    parser.add_argument(
        "-s",
        type=int,
        nargs="+",
        required=True,
        help="Array sizes to test (e.g. 100 500 1000 3000).",
    )

    parser.add_argument(
        "-e",
        type=int,
        choices=[1, 2],
        default=None,
        help="Experiment type: 1 = 5%% noise, 2 = 20%% noise. "
             "Omit for fully random arrays.",
    )

    parser.add_argument(
        "-r",
        type=int,
        required=True,
        help="Number of repetitions per experiment.",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # Increase recursion limit for Quick Sort on larger arrays
    sys.setrecursionlimit(max(10000, max(args.s) * 3))

    # Pretty-print the experiment configuration
    algo_names = [ALGORITHMS[a][0] for a in args.a]
    exp_label = {None: "Random", 1: "Nearly sorted (5% noise)",
                 2: "Nearly sorted (20% noise)"}

    print("=" * 55)
    print("  Sorting Algorithm Benchmark")
    print("=" * 55)
    print(f"  Algorithms : {', '.join(algo_names)}")
    print(f"  Sizes      : {args.s}")
    print(f"  Experiment : {exp_label[args.e]}")
    print(f"  Repetitions: {args.r}")
    print("=" * 55)
    print()

    results = benchmark(args.a, args.s, args.r, args.e)
    plot_results(results, args.s, args.e)


if __name__ == "__main__":
    main()
