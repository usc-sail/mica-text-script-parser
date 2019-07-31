import os

def read_annotation_movies():
    cur_path = os.path.dirname(__file__)
    annotation_filepath = os.path.join(cur_path, "../data/annotation_movies.txt")
    with open(annotation_filepath) as fr:
        content = fr.read().split("\n")
        movies = [line.split()[0].strip() for line in content]
        begs = [int(line.split()[1]) for line in content]
        ends = [int(line.split()[2]) for line in content]
        return movies, begs, ends