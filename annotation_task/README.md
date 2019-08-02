# Annotation Task

This directory consists the data and code for the annotation task of tagging screenplay lines with different screenplay tags.

The objective is -

1. Evaluate our mica parser on how well it identifies different screenplay elements.

2. Improve the mica parser to parse other screenplay elements aside from character name and dialogue

### Data

The annotation folder is [here](https://drive.google.com/drive/folders/1kmhjRuWce7ve-uBO7oobdlrls46Ltl7c?usp=sharing). It contains the three completed annotation xlsx files from three different annotators - Ming (Annotator 1), Saby (Annotator 2) and Tiantian (Annotator 3), and a readme that details the annotation guidelines. The same folder can be found here at `data/annotations/`.

Additionally, `data/movies.txt` contains the list of movies whose screenplay is available to us and `data/annotation_movies.txt` contains the list of movies and their corresponding beginning and ending line numbers (indexing starts from 1) of the excerpts used for annotation. The latter file can be used to find the annotation data exactly.

### Inter-rater agreement

Out of the total 14397 annotation examples, the three annotators disagreed (no majority) on only 18 examples. The average Cohen's kappa score among all three annotators is **0.984** and the krippendorf's alpha score is **0.983**. The gold annotations are found by taking majority, and in case of no majority for those 18 examples, the samples are discarded for evaluation.

### MICA Parser Performance

| Screenplay Element | Precision | Recall | F1 |
| ------------------ | --------- | ------ | ---|
| Dialogue           | 0.832     | 0.954  | 0.889 |
| Character Names    | 0.982     | 0.927  | 0.954 |
| *Scene Boundary     | 0.965     | 0.959  | 0.962 |
| *Transitions        | 1         | 0.791  | 0.883 |
| *Scene Descriptions | 0.863     | 0.889  | 0.876 |

The screenplay elements marked * are the new elements that our parser can parse now, that were not previously parsed. Please check the readme of the annotation task to understand what each screenplay element means.

Our parser does admirably in parsing all the above mentioned screenplay elements. I recommend reporting these numbers in any work that uses our parser to add confidence to the final results.

### ML Parser?

Our parser is regular expression based, and already does very well in parsing the different screenplay elements.  Further improvement can be achived by a sequence tagging model, although the motivation for one has been greatly tempered by the reported numbers.