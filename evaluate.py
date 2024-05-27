import json
import argparse
import typing
import utils
import queue
from openai import AzureOpenAI, OpenAI
from keys import keys
import tqdm
import os

available_clients = queue.Queue()

for key in keys:
    available_clients.put(AzureOpenAI(
        api_version="2024-02-01",
        azure_endpoint=key["GPT4_V_ENDPOINT"],
        api_key=key["GPT4V_KEY"]
    ))


def multi_ask(messages):
    success = False
    while not success:
        client = available_clients.get()
        try:
            response = utils.ask_gpt(client, messages, model="gpt-4v")
            success = True
        except:
            continue
        available_clients.put(client)
        break
    return response


def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--q-type", default="", required=True, help="the type of questions")
    return parser


def check_question(code: str, question: str, options: typing.List[str], type: typing.Literal["zero-shot"]):
    options_str = ", ".join(options)
    if type == "zero-shot":
        messages = [
            {
                "role": "system",
                "content": "I will present a TikZ code. Please answer my questions only based on code. Answer and only answer the letter corresponding to the correct option. Do not add any additional comment in your response"
            },
            {
                "role": "user",
                "content": f"{code}"
            },
            {
                "role": "user",
                "content": f"Given this image, answer {question}. Options are {options_str}"
            }
        ]
        # print(messages)
        return multi_ask(messages)


def main():
    args = default_argument_parser().parse_args()
    q_type = args.q_type
    dataset = json.load(open("data/final_dataset_%s.json" % q_type))
    results = []
    # dataset = dataset[0:1]
    prompt_type = "zero-shot"
    for sample in tqdm.tqdm(dataset):
        code = sample['data']['code']
        query = sample['query']
        question = query['q']
        options: typing.List[str] = query['o']
        pred = check_question(code, question, options,
                              type=prompt_type)
        qid = sample['idx']
        image_id = sample['query']['idx']

        results.append({"pred": pred, "qid": qid, "image_id": image_id})
        # print(answer, check_question(code, question, options, answer, type="zero-shot"))
        # print("="*20)
    tot_correct = 0
    tot_cnt = 0

    for i, sample in enumerate(dataset):
        tot_cnt += 1
        pred = results[i]['pred']
        answer = query['a']
        if pred == answer:
            tot_correct += 1
    print(tot_correct/tot_cnt)
    json.dump(results, open(os.path.join("results", "%s_%s.json"%(q_type, prompt_type)), "w"))


if __name__ == '__main__':
    main()
