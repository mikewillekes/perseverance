
def load_clusters(filename):
    clusters = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            clusters.append(line.strip().split('|'))
    return clusters


def save_clusters(filename, clusters):
    lines = []
    for c in clusters:
        lines.append(f'{"|".join(c)}\n')
    open(filename, 'w').writelines(lines)

