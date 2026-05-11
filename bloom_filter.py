"""
A Bloom filter is a space-efficient data structure that tells you
whether an item is definitely NOT in a set, or MAYBE in a set.
It can give false positives, but never false negatives.

Authors: Stella Sophia Ertl, Harsh Kumar Singh 
"""

import math
import hashlib


class BloomFilter:
    """
    - how many items expect to store (n)
    - how often we tolerate a wrong answer (false positive rate, p)
    - filter then figures out the right size and number of hash functions
   
    """

    def __init__(self, expected_items, false_positive_rate):
        """
        Gettin started with the Bloom filter.
        expected_items (how many items we plan to insert (n))
        false_positive_rate (how often wrong 'yes' answers are okay, e.g. 0.01 = 1%
        """

        # save these so we can report them later
        self.expected_items = expected_items
        self.false_positive_rate = false_positive_rate

        # --- figure out the ideal size of the bit array ---
        # formula: m = -(n * ln(p)) / (ln(2)^2)
        # this comes straight from the math behind Bloom filters
        numerator = -(expected_items * math.log(false_positive_rate))
        denominator = (math.log(2) ** 2)
        self.bit_array_size = int(numerator / denominator)

        # --- figure out how many hash functions we need ---
        # formula: k = (m / n) * ln(2)
        self.num_hash_functions = int(
            (self.bit_array_size / expected_items) * math.log(2)
        )

        # make sure we always have at least 1 hash function
        if self.num_hash_functions < 1:
            self.num_hash_functions = 1

        # --- create the bit array (all zeros to start) ---
        # a list of 0s and 1s, one slot per "bit"
        self.bit_array = [0] * self.bit_array_size

        # keep track of how many items have been inserted
        self.num_inserted = 0
# ------------------------------------------------------------------
    # Hash functions
    # ------------------------------------------------------------------

    def _get_hash_positions(self, item):
        """
        For a given item, return k positions in the bit array.

        We run k slightly different hash functions by mixing a different
        seed number into each one. That way one item maps to k positions.

        item : the string we want to hash
        """

        # convert the item to a string just in case it is not already
        item_as_string = str(item)

        positions = []

        for seed in range(self.num_hash_functions):
            # mix the seed into the input so each hash function is different
            combined = f"{seed}:{item_as_string}"

            # SHA-256 gives a reliable spread of bits
            hash_bytes = hashlib.sha256(combined.encode("utf-8")).hexdigest()

            # turn the hex string into a big integer
            hash_as_int = int(hash_bytes, 16)

            # bring that integer into the range of our bit array
            position = hash_as_int % self.bit_array_size

            positions.append(position)

        return positions
    