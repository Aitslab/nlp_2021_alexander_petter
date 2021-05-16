import csv
import torch

from transformers import BertTokenizer
from transformers import BertForSequenceClassification


# input  = articles from tagged NER file, dir to pre-trained SciBERT model
# output = predictions on the format: entity1 relation entity2 sentence
def run(articles, model_dir, output_path):
  setup_model(model_dir)

  with open(output_path, "w") as tsv_file:
    writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')

    for article in articles.values():
      sentences = article["sentences"]

      for sentence in sentences:
        if sentence["entitycount"] == 2:
          tagged   = sentence["tagged"]
          text     = sentence["text"]
          entities = sentence["entities"]
          pred_rel = predict_relation(tagged)

          writer.writerow([entities[0], pred_rel, entities[1], text])


def setup_model(model_dir):
  global model, tokenizer, device

  model     = BertForSequenceClassification.from_pretrained(model_dir, local_files_only=True, cache_dir=None)
  tokenizer = BertTokenizer.from_pretrained(model_dir)
  device    = torch.device("cuda")
  model.to(device)

def predict_relation(tagged):
  classes    = ["NOT", "PART-OF", "INTERACTOR", "REGULATOR-POSITIVE", "REGULATOR-NEGATIVE"]
  input_ids  = torch.tensor(tokenizer.encode(tagged)).unsqueeze(0).to(device)
  outputs    = model(input_ids)
  pred_rel   = classes[torch.softmax(outputs.logits, dim=1).argmax()]
  return pred_rel
