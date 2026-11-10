"""Repeatable synthetic benchmarks for multi-file matching.

These timings are local measurements, not production-capacity guarantees.
Run from this folder:
    python benchmark_multi_file_consolidation.py
Optional:
    python benchmark_multi_file_consolidation.py --exact-records 20000 --profiles 500
"""
from __future__ import annotations

import argparse
import random
import string
import time

import multi_file_consolidation as consolidation


def make_record(index, name, email):
    return {
        "source_file": f"synthetic_{index % 4 + 1}.xlsx",
        "worksheet": "Synthetic",
        "original_row": index + 2,
        "data": {
            "customerid": f"SYN-{index:07d}",
            "name": name,
            "email": email,
            "city": "Benchmark City",
            "phone": "",
            "department": "",
        },
        "error": None,
    }


def build_exact_records(record_count):
    """Build duplicate pairs with a predictable number of exact groups."""
    if record_count < 2 or record_count % 2:
        raise ValueError("exact-records must be an even integer of at least 2")

    records = []
    for pair in range(record_count // 2):
        name = f"Exact Customer {pair:07d}"
        email = f"exact{pair:07d}@benchmark.example"
        records.append(make_record(pair * 2, name, email))
        records.append(make_record(pair * 2 + 1, name, email))
    return records


def build_name_profiles(profile_count, seed=20261110):
    """Build mostly unrelated names plus one known similar-name pair."""
    if profile_count < 2:
        raise ValueError("profiles must be at least 2")

    rng = random.Random(seed)
    records = [
        make_record(0, "Sarah Example", "sarah.one@benchmark.example"),
        make_record(1, "Sara Example", "sara.two@benchmark.example"),
    ]
    used_names = {"sarah example", "sara example"}

    while len(records) < profile_count:
        token = "".join(rng.choices(string.ascii_lowercase, k=18))
        name = f"{token} Person"
        if name.casefold() in used_names:
            continue
        used_names.add(name.casefold())
        index = len(records)
        records.append(
            make_record(index, name, f"profile{index:05d}@benchmark.example")
        )
    return records


def timed(label, operation):
    started = time.perf_counter()
    result = operation()
    elapsed = time.perf_counter() - started
    print(f"{label}: {elapsed:.4f} seconds")
    return result, elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exact-records", type=int, default=20_000)
    parser.add_argument("--profiles", type=int, default=500)
    args = parser.parse_args()

    print("MULTI-FILE CONSOLIDATION BENCHMARK")
    print("Synthetic data only; no client input files are modified.")
    print(f"Exact-match records: {args.exact_records:,}")

    exact_records = build_exact_records(args.exact_records)
    exact_groups, exact_seconds = timed(
        "Indexed exact matching",
        lambda: consolidation._exact_match_groups(exact_records),
    )
    expected_exact_groups = args.exact_records // 2
    print(f"Exact groups found: {len(exact_groups):,}")
    print(f"Expected exact groups: {expected_exact_groups:,}")
    if len(exact_groups) != expected_exact_groups:
        raise SystemExit("FAIL: exact-match group count did not match expectation.")

    print(f"\nDistinct name/email profiles: {args.profiles:,}")
    profile_records = build_name_profiles(args.profiles)
    possible_groups, possible_seconds = timed(
        "Possible-name matching",
        lambda: consolidation._possible_name_groups(profile_records),
    )
    expected_possible_groups = 1
    print(f"Possible-name groups found: {len(possible_groups):,}")
    print(f"Expected possible-name groups: {expected_possible_groups:,}")
    if len(possible_groups) != expected_possible_groups:
        raise SystemExit("FAIL: possible-name group count did not match expectation.")

    candidate_members, profile_keys = possible_groups[0]
    print(f"Candidate profiles in known match: {len(profile_keys)}")
    print(f"Source records in known match: {len(candidate_members)}")
    if len(profile_keys) != 2 or len(candidate_members) != 2:
        raise SystemExit("FAIL: known possible-name pair was not isolated.")

    print("\nBENCHMARK RESULT: PASS")
    print(f"Exact matching time: {exact_seconds:.4f}s")
    print(f"Possible-name matching time: {possible_seconds:.4f}s")
    print("Timings describe this run and machine only; they are not capacity guarantees.")


if __name__ == "__main__":
    main()
