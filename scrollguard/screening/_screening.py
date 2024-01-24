import numpy as np
from Levenshtein import ratio

def calculate_ratio(s1: str, s2: str, is_sorted=False) -> float:
    if is_sorted:
        s1_sorted = " ".join(sorted(str(s1).split(" ")))
        s2_sorted = " ".join(sorted(str(s2).split(" ")))
        ratios = [
            ratio(s1, s2),
            ratio(s1, s2_sorted),
            ratio(s1_sorted, s2),
            ratio(s1_sorted, s2_sorted),
        ]
        return max(ratios)
    
    return ratio(s1, s2)