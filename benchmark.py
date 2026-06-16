"""
This script runs timing and false positive experiments on the Bloom filter.
It is meant to be run on an HPC cluster with a job script (job.sh).

It tests:
  - How fast insert() and contains() are as the number of items grows
  - How the false positive rate changes as the filter fills up
  - Compression ratio compared to storing all items in a plain Python set

Results are saved to a CSV file so we can plot them in the notebook.
"""

import time
import csv
import random
import string
import os
import sys

# add the project folder to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bloom_filter import BloomFilter



def make_random_word(length=8):
    """Return a random lowercase string of the given length."""
    letters = string.ascii_lowercase
    word = "".join(random.choice(letters) for _ in range(length))
    return word


def make_random_words(how_many, word_length=8):
    """Return a list of how_many random words."""
    words = [make_random_word(word_length) for _ in range(how_many)]
    return words

# Experiment 1: timing insert and contains
# ------------------------------------------------------------------

def run_timing_experiment(sizes, false_positive_rate=0.01):
    """
    For each size in `sizes`, create a fresh Bloom filter, insert that many
    words, then time both insert() and contains().

    Returns a list of dicts with the results.
    """

    print("\n--- Timing experiment ---")
    results = []

    for num_words in sizes:
        print(f"  Testing with {num_words} words...", end=" ", flush=True)

        # generate two separate word lists so we test 'contains' on known items
        words_to_insert = make_random_words(num_words)
        words_to_search = make_random_words(num_words)

        # create the filter sized for exactly num_words items
        bloom = BloomFilter(
            expected_items=num_words,
            false_positive_rate=false_positive_rate
        )

        # --- time the inserts ---
        start_insert = time.perf_counter()
        for word in words_to_insert:
            bloom.insert(word)
        end_insert = time.perf_counter()

        total_insert_time = end_insert - start_insert
        avg_insert_time = total_insert_time / num_words  # seconds per insert

        # --- time the lookups ---
        start_search = time.perf_counter()
        for word in words_to_search:
            bloom.contains(word)
        end_search = time.perf_counter()

        total_search_time = end_search - start_search
        avg_search_time = total_search_time / num_words  # seconds per lookup

        row = {
            "num_words": num_words,
            "total_insert_sec": round(total_insert_time, 6),
            "avg_insert_sec": round(avg_insert_time, 8),
            "total_search_sec": round(total_search_time, 6),
            "avg_search_sec": round(avg_search_time, 8),
            "bit_array_size": bloom.bit_array_size,
            "num_hash_functions": bloom.num_hash_functions,
        }

        results.append(row)
        print(f"insert avg={avg_insert_time:.6f}s  search avg={avg_search_time:.6f}s")

    return results

# Experiment 2: false positive rate as a function of load
# ------------------------------------------------------------------

def run_false_positive_experiment(max_words, false_positive_rate=0.01, steps=20):
    """
    Insert words one batch at a time into a filter designed for max_words.
    After each batch, measure the actual false positive rate.

    We also go BEYOND max_words to see what happens when the filter overflows.

    Returns a list of dicts with the results.
    """

    print("\n--- False positive rate experiment ---")

    # we will test up to 3x the designed capacity so we see overflow behavior
    total_to_insert = max_words * 3
    batch_size = total_to_insert // steps

    # filter sized for max_words
    bloom = BloomFilter(
        expected_items=max_words,
        false_positive_rate=false_positive_rate
    )

    # generate all the words we will insert
    all_words_to_insert = make_random_words(total_to_insert)

    # generate a separate pool of words that we will NEVER insert
    # we use these to measure false positives
    test_pool_size = 2000
    words_never_inserted = make_random_words(test_pool_size, word_length=10)

    results = []
    inserted_so_far = 0

    for step in range(steps + 10):  # +10 steps to go well past capacity
        # inserting one more batch
        start = inserted_so_far
        end = min(start + batch_size, total_to_insert)

        for word in all_words_to_insert[start:end]:
            bloom.insert(word)

        inserted_so_far = end

        # count how many of the "never inserted" words the filter says are present
        false_positive_count = 0
        for test_word in words_never_inserted:
            if bloom.contains(test_word):
                false_positive_count += 1

        actual_fpr = false_positive_count / test_pool_size
        theoretical_fpr = bloom.get_false_positive_rate()

        row = {
            "num_inserted": inserted_so_far,
            "actual_fpr": round(actual_fpr, 6),
            "theoretical_fpr": round(theoretical_fpr, 6),
            "over_capacity": inserted_so_far > max_words,
        }

        results.append(row)
        print(
            f"  inserted={inserted_so_far:>7}  "
            f"actual fpr={actual_fpr:.4f}  "
            f"theoretical={theoretical_fpr:.4f}  "
            f"{'[OVER CAPACITY]' if inserted_so_far > max_words else ''}"
        )

        if inserted_so_far >= total_to_insert:
            break

    return results
# ------------------------------------------------------------------
# Experiment 3: compression ratio
# ------------------------------------------------------------------

def run_compression_experiment():
    """
    Compare the logical size (bits) of a Bloom filter against storing
    all items in a Python set, for different expected sizes and FPRs.

    Returns a list of dicts with the results.
    """

    print("\n--- Compression ratio experiment ---")

    sizes = [100, 500, 1000, 5000, 10000, 50000, 100000]
    fprs = [0.01, 0.05, 0.10]

    # rough bytes per item in a Python set (a string of ~8 chars is ~57 bytes)
    bytes_per_set_item = 57

    results = []

    for n in sizes:
        for fpr in fprs:
            bloom = BloomFilter(expected_items=n, false_positive_rate=fpr)

            bloom_bytes = bloom.get_memory_bytes()
            set_bytes = n * bytes_per_set_item

            compression_ratio = set_bytes / bloom_bytes

            row = {
                "expected_items": n,
                "false_positive_rate": fpr,
                "bloom_bytes": bloom_bytes,
                "set_bytes": set_bytes,
                "compression_ratio": round(compression_ratio, 2),
                "num_hash_functions": bloom.num_hash_functions,
                "bit_array_size": bloom.bit_array_size,
            }

            results.append(row)
            print(
                f"  n={n:>7}  fpr={fpr}  "
                f"bloom={bloom_bytes:>7} bytes  "
                f"set={set_bytes:>8} bytes  "
                f"ratio={compression_ratio:.1f}x"
            )

    return results


# ------------------------------------------------------------------
# Save results to CSV
# ------------------------------------------------------------------

def save_to_csv(rows, filename):
    """Write a list of dicts to a CSV file."""
    if not rows:
        print(f"  (no data to save for {filename})")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Saved {len(rows)} rows to {filename}")


# ------------------------------------------------------------------
# Main: run all experiments
# ------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)  # fix seed so results are reproducible

    output_dir = "benchmark_results"
    os.makedirs(output_dir, exist_ok=True)

    # sizes to test for timing (adjust upward for real HPC runs)
    timing_sizes = [
        100, 500, 1000, 2000, 5000,
        10000, 20000, 50000, 100000, 200000
    ]

    # ---- run experiments ----
    timing_rows = run_timing_experiment(timing_sizes)
    save_to_csv(timing_rows, f"{output_dir}/timing_results.csv")

    fpr_rows = run_false_positive_experiment(max_words=10000)
    save_to_csv(fpr_rows, f"{output_dir}/false_positive_results.csv")

    compression_rows = run_compression_experiment()
    save_to_csv(compression_rows, f"{output_dir}/compression_results.csv")

    print("\nAll experiments finished. Results saved in:", output_dir)