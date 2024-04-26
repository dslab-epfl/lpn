from ..lpn_extension import IntSymbol

def log_out_as_one_class(p_list, file_path):
    _str = "=== start-all-tokens\n"
    for p in p_list:
        if len(p.tokens) == 0:
            continue
        _str += "== " + p.id + "\n"
        tk_cnt = 0
        for tk in p.tokens:
            _str += "= token " + str(tk_cnt) + "\n"
            for k, v in tk.dict_items():
                if isinstance(v, int):
                    _str += "property:" + k + ";sample:" + str(int(v)) + ";ranges:NULL\n"
                elif isinstance(v, IntSymbol):
                    _str += "property:" + k + ";sample:" + str(v.value) + ";ranges:[" + str(v.lower_bound) + ", " + str(v.upper_bound) + "]\n"
            tk_cnt += 1
    _str += "=== end-all-tokens\n"
    with open(file_path, 'w') as f:
        f.write(_str)
