import json
import util

def add_ner_tags(infile,outfile):
  #this function adds the entity count and, for sentences with exactly two entities, it encloses entity 1 and 2 in << >> and  [[ ]]
  #infile = path to file returned by ner module
  #outfile = path to new json file "text-nertags.json"
  
    with open(infile, "r",encoding="utf-8") as f:
        articles = json.loads(f.read())


# Because we want to save the result periodically.
    batch_index = 0
    batch_size = 500

    # Run prediction on each sentence in each article.
    for pmid in articles:
        if batch_index > batch_size:
            util.append_to_json_file(outfile, articles)
            batch_index = 0
        sentences = articles[pmid]["sentences"]
        for i, sentence in enumerate(sentences):

            count = len(articles[pmid]["sentences"][i]["entities"])
            #x = {"text2": articles[pmid]["sentences"][i]["entities"][0]}
            if count == 2:
              entity_1 = articles[pmid]["sentences"][i]["entities"][0]
              entity_2 = articles[pmid]["sentences"][i]["entities"][1]
              string = articles[pmid]["sentences"][i]["text"]
              string = string.replace(entity_1, "<< "+entity_1+" >>")
              string = string.replace(entity_2, "[[ "+entity_2+" ]]")
            else:
              string = ""
            articles[pmid]["sentences"][i]["tagged"] = string
            articles[pmid]["sentences"][i]["entitycount"] = count

        batch_index += 1

    util.append_to_json_file(outfile, articles)

    print("Finished running NER script.")
