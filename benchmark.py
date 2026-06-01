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


# ------------------------------------------------------------------
# Helper: generate random words
# ------------------------------------------------------------------

def make_random_word(length=8):
    """Return a random lowercase string of the given length."""
    letters = string.ascii_lowercase
    word = "".join(random.choice(letters) for _ in range(length))
    return word


def make_random_words(how_many, word_length=8):
    """Return a list of how_many random words."""
    words = [make_random_word(word_length) for _ in range(how_many)]
    return words