d = {'a': 1, 'b': 2, 'c': 3}
keys_to_delete = [k for k, v in d.items() if k == 'b']
for key in keys_to_delete:
    del d[key]
