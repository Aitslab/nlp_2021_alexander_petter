import csv
import torch

from transformers import BertTokenizer
from transformers import BertForSequenceClassification


# input  = articles from tagged NER file, dir to pre-trained SciBERT model
#          path to predictions file, path to statistics file
# output = predictions on the format: entity1 relation entity2 sentence
#          statistics sorted by frequency on the format: entity1 entity2 relation frequency
def run(articles, model_dir, preds_path, stats_path):
  stats = {}
  setup_model(model_dir)

  with open(preds_path, "w") as tsv_file:
    writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')

    for article in articles.values():
      sentences = article["sentences"]

      for sentence in sentences:
        if sentence["entitycount"] == 2:
          tagged   = sentence["tagged"]
          text     = sentence["text"]
          entity1  = sentence["entities"][0]
          entity2  = sentence["entities"][1]

          pred_rel = predict_relation(tagged)
          add_count(entity1, entity2, pred_rel, stats)

          writer.writerow([entity1, pred_rel, entity2, text])
  
  sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
  write_stats(stats_path, sorted_stats)


def add_count(entity1, entity2, relation, stats):

  if (entity1, entity2, relation) in stats:
    stats[(entity1, entity2, relation)] += 1
  else:
    stats[(entity1, entity2, relation)] = 1


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


def write_stats(stats_path, sorted_stats):

  with open(stats_path, "w") as tsv_file:
    writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')

    for (entity1, entity2, relation), count in sorted_stats:
      writer.writerow([entity1, entity2, relation, count])
