from mutagen.mp4 import MP4


# Example usage
file_path = "data/U4_lBvIIVWE.m4a"  # Replace with your file path
title = get_title(file_path)
print("Title:", title)

duration_seconds = get_duration_in_seconds(file_path)
print("Duration in seconds:", duration_seconds)