import re

# Path = "../utils/cit.txt"
#
# with open(Path, "r+", encoding="utf-8") as file:
#     lines = file.read().splitlines()
#     print(lines)
#     for line in lines:
#         print(line+"/city")
#         line_now = line+"/city"+"/n"
#         file.write(line)

str = "北"
Path = "../utils/city_data.txt"

with open(Path, "r+", encoding="utf-8") as file:
    lines = file.read().splitlines()
    for line in lines:
        pattern = r"%s"%str
        print(re.findall(pattern, line))
