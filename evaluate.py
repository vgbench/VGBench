import json
import argparse
import typing
import utils
import queue
from openai import AzureOpenAI, OpenAI
from keys import keys
import tqdm
import os
from tqdm.contrib.concurrent import process_map
import functools
import signal

available_clients = queue.Queue()

def init_client(model):
    for key in keys[model]:
        available_clients.put(AzureOpenAI(
            api_version="2024-02-01",
            azure_endpoint=key["GPT_ENDPOINT"],
            api_key=key["GPT_KEY"]
        ))


def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--q-type", default="", required=True, help="the type of questions")
    parser.add_argument("--prompt-type", default="zero-shot",
                        choices=["zero-shot", "few-shot", "chain-of-thought"], required=True)
    parser.add_argument(
        "--format", choices=["tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    return parser


def check_question(sample, prompt_type: typing.Literal["zero-shot", "few-shot", "chain-of-thought"], few_shot_samples, model="gpt-4"):
    code = sample['code']
    question = sample['question']
    options = sample['options']
    options_str = ", ".join(options)
    if prompt_type == "zero-shot":
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
        return utils.multi_ask(available_clients, messages, model)
    elif prompt_type == "few-shot":
        messages = [
            {
                "role": "system",
                "content": "I will present a TikZ code. Please answer my questions only based on code. Answer and only answer the letter corresponding to the correct option. Do not add any additional comment in your response. For your reference, I will give you some example"
            }]
        for few_shot_sample in few_shot_samples:
            messages.append({
                "role": "user",
                "content": "This is an example, the code is: %s" % few_shot_sample['code']
            })
            messages.append({
                "role": "user",
                "content": f"Given this image, answer {few_shot_sample['question']}. Options are {few_shot_sample['options']}"
            })
            messages.append({
                "role": "assistant",
                "content": few_shot_sample['answer']
            })

        messages += [
            {
                "role": "user",
                "content": f"The code is: {code}"
            },
            {
                "role": "user",
                "content": f"Given this image, answer {question}. Options are {options_str}"
            }
        ]
        # print(messages)
        return multi_ask(messages, model)
    elif prompt_type == "chain-of-thought":
        messages = [
            {
                "role": "system",
                "content": "I will present a TikZ code. Please answer my questions only based on code. Please consider the question step by step."
            },
            {
                "role": "user",
                "content": f"{code}"
            },
            {
                "role": "user",
                "content": f"Given this image, the question is {question}. Options are {options_str}. Do not answer directly, consider each option individually."
            }
        ]
        messages.append({
            "role": "user",
            "content": f"Carefully consider if the option A is correct"
        })
        response = multi_ask(messages, model)
        messages.append({
            "role": "assistant",
            "content": response})
        messages.append({
            "role": "user",
            "content": f"Carefully consider if the option B is correct"
        })
        response = multi_ask(messages, model)
        messages.append({
            "role": "assistant",
            "content": response})
        messages.append({
            "role": "user",
            "content": f"Carefully consider if the option C is correct"
        })
        response = multi_ask(messages, model)
        messages.append({
            "role": "assistant",
            "content": response})
        messages.append({
            "role": "user",
            "content": f"Carefully consider if the option D is correct"
        })
        response = multi_ask(messages, model)
        messages.append({
            "role": "assistant",
            "content": response})

        # print(messages)
        messages.append({
            "role": "user",
            "content": f"Which option is the best? Answer and only answer the letter corresponding to the correct option. Do not add any additional comment in your response"
        })
        print(json.dumps(messages))
        return multi_ask(messages, model)
    else:
        raise ("Prompt strategy %s is not implemented" % prompt_type)


def convert_sample_format(sample, ans=False):
    query = sample['query']
    org_sample = {"code": sample['data']['code'],
                  "question": query['q'], "options": query['o']}
    if ans:
        org_sample['answer'] = query['a']
    return org_sample


def signal_handler(sig, frame):
    os.killpg(0, signal.SIGTERM)




def main():
    os.setpgrp()
    signal.signal(signal.SIGINT, signal_handler)
    args = default_argument_parser().parse_args()

    prompt_type = args.prompt_type
    model = "gpt-4"

    q_type = args.q_type

    init_client(model)

    dataset = json.load(open("data/%s/final_dataset_%s.json" % (args.format, q_type)))
    few_shot_samples = dataset[0:3]
    test_samples = dataset[3:]
    pred_results = []
    dataset_converted = map(convert_sample_format, test_samples)
    few_shot_samples_converted = list(map(
        functools.partial(convert_sample_format, ans=True), few_shot_samples))
    # for sample in tqdm.tqdm(dataset_converted):
    #     pred_results.append(check_question(
    #         sample, prompt_type, few_shot_samples_converted, model))
    pred_results = process_map(functools.partial(
        check_question, prompt_type=prompt_type, few_shot_samples=few_shot_samples_converted, model=model), dataset_converted)
    tot_correct = 0
    tot_cnt = 0
    results = []

    for i, sample in enumerate(test_samples):
        tot_cnt += 1
        answer = sample['query']['a']
        pred = pred_results[i]
        qid = sample['idx']
        image_id = sample['query']['idx']

        results.append({"pred": pred, "qid": qid,
                       "image_id": image_id, "answer": answer})

        if pred == answer:
            tot_correct += 1
    print(round(tot_correct/tot_cnt, 3))
    json.dump(results, open(os.path.join(
        "results/%s"%args.format, "%s_%s.json" % (q_type, prompt_type)), "w"))


if __name__ == '__main__':
    main()
