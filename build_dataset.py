import pandas
import argparse
import os
import json
import numpy as np

def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument("--dataset-path", required=True)
    parser.add_argument(
        "--q-type", default="", required=True, help="the type of questions")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    return parser


def load_questions(vformat: str, q_type):
    questions = json.load(open("data/%s/questions_%s.json" % (vformat, q_type)))
    return questions


def main():
    args = default_argument_parser().parse_args()
    q_type = args.q_type
    directory = os.path.join("data/%s/annotations"%args.format, q_type)
    result = []
    unannoted_dataset = json.load(
        open(args.dataset_path, "r"))
    questions = load_questions(args.format, q_type)
    total_questions = 0
    known_question = set()
    for file in os.listdir(directory):
        # print(file)
        data = pandas.read_excel(os.path.join(
            directory, file), engine="openpyxl")
        for _, row in data.iterrows():
            if np.isnan(row['Valid']):
                continue
            total_questions += 1
            if row['Valid'] != 1:
                continue
            # print(row)
            idx = row['QuestionIndex']
            img_idx = row['ImgIndex']
            assert(idx not in known_question)
            known_question.add(idx)
            result.append(
                {'idx': idx, 'data': unannoted_dataset[img_idx], 'query': questions[idx]})
    print("Passing Rate:", len(known_question)/total_questions)
    print("Total:", len(known_question))
    # print(result)
    json.dump(result, open("data/%s/final_dataset_%s.json" %
              (args.format, q_type), "w"))


if __name__ == '__main__':
    main()
