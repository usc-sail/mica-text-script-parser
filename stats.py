import numpy as np

def get_stats(arr, bins = "auto"):
    arr = np.array(arr)
    MIN = np.min(arr)
    MAX = np.max(arr)
    MEAN = np.mean(arr)
    STD = np.std(arr)
    MEDIAN = np.median(arr)
    HIST, BINS = np.histogram(arr, bins = bins, density = False)
    return dict(MIN = MIN, MAX = MAX, MEAN = MEAN, STD = STD, MEDIAN = MEDIAN, HIST = (HIST, BINS))

def get_stats_report(title, arr, bins = "auto"):
    stats = get_stats(arr, bins = bins)
    desc = f"{title} STATS\n"
    desc += f"\t\tmin  = {stats['MIN']}\n"
    desc += f"\t\tmax  = {stats['MAX']}\n"
    desc += f"\t\tmean = {stats['MEAN']} (+-{stats['STD']})\n"
    desc += f"\t\tmed  = {stats['MEDIAN']}\n\n"
    desc += f"\t\t{'BINS':20s}\t\tNUMBER\t\tFRACTION\n"
    hist, bins = stats['HIST']
    total = np.sum(hist)
    for i in range(len(hist)):
        frac = hist[i]/total
        desc += f"\t\t{bins[i]:8.2f} -- {bins[i + 1]:8.2f}\t{hist[i]:8d}\t\t{frac:.5f}\n"
    desc += "\n"
    return desc