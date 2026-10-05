CHALLENGES = {
    "1": {
        "title": "Palindrome Cleaner (Edge Cases & Punctuation)",
        "description": "Function that determines if a string is a palindrome, ignoring non-alphanumeric chars and case.",
        "buggy_code": '''def is_palindrome(s: str) -> bool:
    # BUG: naive reverse without stripping punctuation or handling case
    return s == s[::-1]
''',
        "test_code": '''assert is_palindrome("racecar") == True, "Failed racecar"
assert is_palindrome("A man, a plan, a canal: Panama") == True, "Failed Panama"
assert is_palindrome("race a car") == False, "Failed race a car"
assert is_palindrome(" ") == True, "Failed empty space"
assert is_palindrome("0P") == False, "Failed alphanumeric 0P"
print("All palindrome tests passed!")
'''
    },
    "2": {
        "title": "Binary Search (Off-by-one Boundary Bug)",
        "description": "Binary search algorithm that returns the index of target in sorted list nums, or -1 if not found.",
        "buggy_code": '''def binary_search(nums: list[int], target: int) -> int:
    left = 0
    right = len(nums) # BUG: should be len(nums) - 1 or while left < right
    while left < right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid # BUG: will infinite loop if left == mid
        else:
            right = mid
    return -1
''',
        "test_code": '''assert binary_search([-1, 0, 3, 5, 9, 12], 9) == 4, "Failed finding 9"
assert binary_search([-1, 0, 3, 5, 9, 12], 2) == -1, "Failed missing 2"
assert binary_search([5], 5) == 0, "Failed single element found"
assert binary_search([5], -5) == -1, "Failed single element missing"
assert binary_search([], 1) == -1, "Failed empty list"
assert binary_search([2, 5], 5) == 1, "Failed 2-element search"
print("All binary search tests passed!")
'''
    },
    "3": {
        "title": "Deep Nested Dict Flattener",
        "description": "Flattens a nested dictionary into dot-separated keys, e.g. {'a': {'b': 1}} -> {'a.b': 1}.",
        "buggy_code": '''def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            # BUG: recursive call return value not unpacked properly
            items.append((new_key, flatten_dict(v, new_key, sep=sep)))
        else:
            items.append((new_key, v))
    return dict(items)
''',
        "test_code": '''sample = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
result = flatten_dict(sample)
assert result == {"a": 1, "b.c": 2, "b.d.e": 3}, f"Got {result}"

empty_dict = {}
assert flatten_dict(empty_dict) == {}, "Failed empty dict"

nested_empty = {"a": {}}
assert flatten_dict(nested_empty) == {}, "Failed nested empty dict"
print("All flatten dict tests passed!")
'''
    }
}

