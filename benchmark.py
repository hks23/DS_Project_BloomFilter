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