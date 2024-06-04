import os
import glob
import json

dir = "graphviz_dataset"

sorted_files = sorted(glob.glob(os.path.join(dir, "graphviz_data_*")))

print(sorted_files)

results = []

for file in sorted_files:
    with open(file) as fp:
        obj = json.load(fp)
    results += obj

print(len(results))
json.dump(results, open(os.path.join(dir, "graphviz.json"), "w"))