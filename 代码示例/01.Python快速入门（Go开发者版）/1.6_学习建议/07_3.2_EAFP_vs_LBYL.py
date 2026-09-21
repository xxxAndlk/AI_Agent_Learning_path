# LBYL (Look Before You Leap) - Go风格
if key in dictionary:
    value = dictionary[key]
else:
    value = default

# EAFP (Easier to Ask Forgiveness than Permission) - Python风格
try:
    value = dictionary[key]
except KeyError:
    value = default
