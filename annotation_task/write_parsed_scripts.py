from script_parser import script_parser

def write_parsed_scripts():
    movies = open("data/movies.txt").read().strip().split("\n")
    for movie in movies:
        src = "../../mica-scripts/scripts_txt/{}.txt".format(movie)
        dst = "../../mica-scripts/parsed_scripts_with_scenes/{}.txt".format(movie)
        script_parser(src, dst, write = True)
    
if __name__ == "__main__":
    write_parsed_scripts()