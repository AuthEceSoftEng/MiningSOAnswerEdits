# Mining Stack Overflow Answer Edits
This repository contains a methodology for mining Stack Overflow answer edits.

## Research Overview
The answers to Stack Overflow question posts often undergo several edits by
different community members in order to provide the best solution to the problem.
Our methodology compares answer edits using a similarity scheme that takes into
account their text and their code differences, while clustering techniques
are employed to extract common answer edit patterns. These edit patterns
represent best practices and can be useful for evolving answer posts (or
generally snippets), for assessing whether answers are complete (i.e. not
requiring any more edits), or even for studying the co-evolution between
different post elements (text, code snippets).

The complete description of our methodology is available at the publication:
```
Themistoklis Diamantopoulos, Maria-Ioanna Sifaki, and Andreas L. Symeonidis.
"Towards Mining Answer Edits to Extract Evolution Patterns in Stack Overflow."
Paper accepted at the 16th International Conference on Mining Software
Repositories (MSR '19), 2019.
```
This repository contains all code and instructions required to reproduce the
findings of the above publication. If this seems helpful or relevant to your
work, you may cite it.

## Instructions
Our methodology is applied on the data dump of SOTorrent, which is available
[here](https://empirical-software.engineering/projects/sotorrent/).
So, the first step is to clone this repository and download also the data dump of SOTorrent.
The code is actually a collection of scripts that are used to make dat manipulations
one after the other (we use the numbering t0, t1, t2, ... to dictate the order of
running the scripts).

### Data Preprocessing
This step reads the SOTorrent data dump and produces a new data dump, which
includes the Java-related data.

Open file `properties.py` and set the variable `data_dump_original_path` to the
directory where SOTorrent is downloaded. Set also the variable `data_dump_final_path`
to the directory where you want to save the final data dump.

Run the script `t0_preprocess_data_dump.py` and check that the new data dump is created
correctly in the new directory. If there are any issues when reading gz files, you
can run the script `t0_fix_gz_file.sh` giving as input the problematic gz file in order to
be fixed (e.g. `./t0_fix_gz_file.sh PostVersion.csv.gz`).

Set up a MySQL server (available [here](https://dev.mysql.com/downloads/mysql/)),
navigate to the new directory and follow the instructions there for creating the
database and importing the data.

### Database Connection
After creating the database, make sure that the relevant settings for connecting to it
in file `properties.py` are set correctly.

Set also the `data_path` to the path where all data of the methodology are going to be
stored.

Run the script `t1_extract_data_from_db.py`. This should produce a file `answer_posts_with_edits.csv`, 
which includes answer posts with columns `Id`, `Text`, and `Code` for the content of each post,
as well as `PredPostHistoryId` and `Comment` if the post is an edit to another answer (with
id equal to `PredPostHistoryId`) and the edit also has a comment (`Comment`).

### Edit Dataset Construction
Download the SequenceExtractor tool (available [here](https://github.com/thdiaman/SequenceExtractor)),
copy the file `sequenceextractor.py` in the source code and set the variable `sequence_extractor_path`
in the properties file to the path of the SequenceExtractor jar.

After that, run the script `t2_create_edit_dataset.py`. This should produce a file `edits.csv`
that is a dataset of edits with columns for
the ids of the post before and after the edit (`IdBefore` and `IdAfter`),
the comment of the edit (`Comment`),
the text of the post before and after the edit (`TextBefore` and `TextAfter`),
the code of the post before and after the edit (`CodeBefore` and `CodeAfter`),
and the code sequences of the post before and after the edit (`CodeSequenceBefore` and `CodeSequenceAfter`).

Run also the script `t3_create_edit_differences` to create the file `edit_differences.csv`,
which includes the data of the edits (i.e. as in `edits.csv`) as well as their differences (fields
`TextDiff`, `CodeDiff`, `CodeSequenceDiff`, `TextAdditions`, `TextDeletions`, `CodeAdditions`,
`CodeDeletions`, `CodeSequenceAdditions`, `CodeSequenceDeletions`) computed per line.

### Distance Matrix Creation
Run the script `t4_create_similarity_matrix.py` to create a similarity matrix between all edits (file
`similarity_matrix.csv`). Also run `t5_filter_similarity_matrix.py` to filter the matrix (and produce
`filtered_similarity_matrix.csv`).

After that, run the script `t6_create_distance_matrices.py` to create the distance matrix for text, code,
and code sequence differences (sparse: `distance_matrix_sparse_full.pickle`, dense: `distance_matrix_dense_full.pickle`),
the dense distance matrix for comment differences (`distance_matrix_dense_comment.pickle`), and the
corresponding labels (`distance_matrix_labels.pickle`).

### Clustering Execution
Then, run the script `t7_find_optimal_number_of_clusters.py` to perform optimization in order to
find the optimal number of clusters. The script produces the SSE at every step (`clustering_stats.csv`),
prints the optimal number of clusters, and creates the graph (`clusters-vs-sse.pdf`).

Finally, run the script `t8_apply_hierarchical_clustering.py` to group the data into clusters (`clusters.txt`) and
find also the top comments per cluster (`cluster_names.txt`).
