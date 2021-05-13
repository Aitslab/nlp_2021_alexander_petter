# thesis-code

## Setup

### Setup using Conda (Anaconda / Miniconda)

It's best to create a custom environment first:

```
conda create -n ENV_NAME
conda activate ENV_NAME
conda install python==3.7
```

This will create an empty environment and install Python 3.7 together with
the corresponding version of pip. We will then use _that_ version of pip
to install the requirements.

Clone this repo using git, navigate to the folder. Then run:

```
pip install -r requirements.txt
```

It's important to get this right, since BERT requires TensorFlow 1.15,
which in its turn requires Python/pip 3.7 (not 3.8). If you get an error for tensorflow (ERROR: Could not find a version that satisfies the requirement tensorflow==1.15.0
ERROR: No matching distribution found for tensorflow==1.15.0) check if you are inside the environment you made.

### Understanding the pipeline

The pipeline consists of several steps, which need not all be rerun every time.

- Step 1 is to fetch and save the data: for this purpose _either_
  `downloader` or `cord_loader` is used.
  - For `downloader`, the input is a list of newline-separated PubMed IDs. The output is a json file with the abstracts.
  - For `cord_loader`, the input is the `metadata.csv` file from inside the
    `.tar.gz` files in the [CORD-19 Historical Releases](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html) (this seems unavailable for early releases).
- Step 2 is `sentencer` which processes the data further for use by the models. The input is the json file created by the downloader or cord_loader. The output is a json file with individual sentences.
- Step 3 is `ner`, named-entity recognition.
- Step 4 is `add_tags`, adds brackets to the recognized entities for the re model (free standing script variant here: https://github.com/Aitslab/nlp_2021_alexander_petter/blob/master/under_development/add_ner_tags.py)
- Step 5 is `re`, relationship extraction (under development).
- Optional step: `metrics` will create metrics such as F1-score for the NER model.
- Optional step: `analysis` will analyse the NER results to find co-occurrences.

### Download the NER model
Download the model and model vocab (vocab file is also in biobert_bc5cdr-chem folder).
**[BioBERT-Base fine-tuned ONNX-model with vocabulary](https://drive.google.com/drive/folders/1neThCq4MqFPd0133WDDC4MYUycE84fT7?usp=sharing)** - fine-tuned on BC5CDR-chem dataset

### Running the pipeline
Make the following folders in your main directory: input, output, biobert_onnx. Place the input files for the CORD loader or the downloader (example input file for downloader her: https://github.com/Aitslab/nlp_2021_alexander_petter/blob/master/pmid.txt) into the input folder and the biobert model and vocab in the biobert_onnx folder. 

Edit the `config.json` file:
1. un-ignore the steps you want to run by setting them to `false`. 
2. Check that you have the correct paths to your input, output and biobert_onnx folder. Modify the other parameters in the config file if desired. To run the metrics part of the pipeline you have to define the location of the annotated evaluation corpus, e.g. the training file of BC5CDR-chem.

Here's a nice little chart to help you understand (A-H are
file names).

```
(A)———[downloader]———.                                       .——[analysis]———(E)
                      |———(C)———[sentencer]———(D)———[ner]———|
(B)———[cord_loader]——'                                       '——[add_tags]———(F)———[re]———(G)

(H)———[metrics]———(I)  (independent)
```

Then run the script by doing: `python main.py`

## Training a new model
Upload the datasets for training.

### Training a BioBERT NER model
Follow the instructions here:
https://github.com/dmis-lab/biobert

Additional instructions here: https://github.com/Aitslab/BioNLP/blob/master/antton/test_bioBERT.ipynb
Make sure the actual model is saven (in .pb format)

### Training a relation extraction model
For the RE-model see instructions on datasets and training here: https://github.com/Aitslab/nlp_2021_alexander_petter/blob/master/utils/chemprot/README.md

## Converting BioBERT (TensorFlow) to ONNX
The model to be converted should be in .pb format
First make sure to install `tf2onnx`:

```
pip install -U tf2onnx
```

Then convert your (exported) TensorFlow model:

```
python -m tf2onnx.convert --saved-model ./PATH_TO_MODEL_DIR/ --output ./OUT_PATH/model_name.onnx
```
More info here: https://docs.unity3d.com/Packages/com.unity.barracuda@1.0/manual/Exporting.html
## Creating a symlink to a model

`ln -s [absolute path to model] [path to link]`

## Corpora used for training
The Chemprot corpus has annotations for chemical-gene/protein interactions in the direction chemical -> protein only 
(i.e. only relations of “what a chemical does to a gene/protein")

corpora for training BioBERT can be found here:
https://github.com/dmis-lab/biobert
