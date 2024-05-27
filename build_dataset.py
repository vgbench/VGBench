import pandas
import argparse
import os
import json


def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--q-type", default="", required=True, help="the type of questions")
    return parser

def load_questions(q_type):
    questions = json.load(open("data/questions_%s.json"%q_type))
    return questions


def main():
    args = default_argument_parser().parse_args()
    q_type = args.q_type
    directory = os.path.join("data/annotations", q_type)
    result = []
    unannoted_dataset = json.load(
        open("/home/zbc/research/datasets/datikz.json", "r"))
    questions = load_questions(q_type)
    for file in os.listdir(directory):
        # print(file)
        data = pandas.read_excel(os.path.join(directory, file), engine="openpyxl")
        for _, row in data.iterrows():
            if row['Valid'] != 1:
                continue
            # print(row)
            idx = row['QuestionIndex']
            img_idx = row['ImgIndex']
            result.append({'idx': idx, 'data': unannoted_dataset[img_idx], 'query': questions[idx]})
    # print(result)
    json.dump(result, open("data/final_dataset_%s.json"%q_type, "w"))

if __name__ == '__main__':
    main()
