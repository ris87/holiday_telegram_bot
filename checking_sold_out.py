def is_merge(s, part1, part2):
    l  = [s.index(x) for x in part1]
    m = [s.index(x) for x in part2]
    a = map(abs(zip(l,m)))

    print(a)
    k = sorted(l)
    if l == sorted(l):
        return True
    else:
        return False



print(not is_merge('codewars', 'cdw', 'oears'))
