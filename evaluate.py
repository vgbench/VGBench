import json
import argparse
import typing
import utils
from keys import keys
import tqdm
import os
from tqdm.contrib.concurrent import process_map
import functools
import signal
import multiprocessing
import math

available_keys = multiprocessing.Queue()


def init_client(model):
    for key in keys[model]:
        available_keys.put(key)


def default_argument_parser():
    parser = argparse.ArgumentParser(description="Evaluate VGQA Dataset")
    parser.add_argument(
        "--q-type", default="", required=True, help="the type of questions")
    parser.add_argument("--prompt-type", default="zero-shot",
                        choices=["zero-shot", "few-shot", "zero-shot-cot"], required=True)
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    parser.add_argument(
        "--model", choices=["gpt-4", "gpt-35-turbo", "Mixtral-8x7B-Instruct-v0.1", "Llama-3-8B-Instruct-262k", "Llama-3-70B-Instruct-Gradient-262k"], default="", required=True, help="the model used to evaluate")
    parser.add_argument("--min", type=int, default=0,
                        help="filter the lower bound of the length of the vector graphics")
    parser.add_argument("--max", type=int, default=math.inf,
                        help="filter the upper bound of the length of the vector graphics")
    parser.add_argument("--single", action='store_true')
    return parser


def check_question(sample, prompt_type: typing.Literal["zero-shot", "few-shot", "zero-shot-cot"], few_shot_samples, model, qtype:str, vformat: str):
    msg_dir = "results_vqa/%s/%s-msgs-%s-%s" % (vformat, model, qtype, prompt_type)

    if not os.path.exists(msg_dir):
        os.mkdir(msg_dir)
    msg_file = os.path.join(msg_dir, "%d.json" % sample['qid'])
    if os.path.exists(msg_file):
        with open(msg_file) as file:
            messages = json.load(file)
    else:

        code = sample['code']
        question = sample['question']
        options = sample['options']
        options_str = ", ".join(options)
        if prompt_type == "zero-shot":
            messages = [
                {
                    "role": "system",
                    "content": f"I will present a {vformat} code. Please answer my questions only based on code. Answer and only answer the letter corresponding to the correct option. Do not add any additional comment in your response"
                },
                {
                    "role": "user",
                    "content": f"\"{code}\". Given this image, answer {question}. Options are {options_str}"
                }
            ]
            # print(messages)
            # print(json.dumps(messages))
            response = utils.multi_ask(available_keys, messages, model)
        elif prompt_type == "few-shot":
            messages = [
                {
                    "role": "system",
                    "content": f"I will present a {vformat} code. Please answer my questions only based on code. Answer and only answer the letter corresponding to the correct option. Do not add any additional comment in your response. For your reference, I will give you some example"
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
            response = utils.multi_ask(available_keys, messages, model)
        elif prompt_type == "zero-shot-cot":
            messages = [
                {
                    "role": "system",
                    "content": f"I will present a {vformat} code. Please answer my questions only based on code. Please consider the question step by step."
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
            response = utils.multi_ask(available_keys, messages, model)
            messages.append({
                "role": "assistant",
                "content": response})
            messages.append({
                "role": "user",
                "content": f"Carefully consider if the option B is correct"
            })
            response = utils.multi_ask(available_keys, messages, model)
            messages.append({
                "role": "assistant",
                "content": response})
            messages.append({
                "role": "user",
                "content": f"Carefully consider if the option C is correct"
            })
            response = utils.multi_ask(available_keys, messages, model)
            messages.append({
                "role": "assistant",
                "content": response})
            messages.append({
                "role": "user",
                "content": f"Carefully consider if the option D is correct"
            })
            response = utils.multi_ask(available_keys, messages, model)
            messages.append({
                "role": "assistant",
                "content": response})

            # print(messages)
            messages.append({
                "role": "user",
                "content": f"Which option is the best? Answer and only answer the letter corresponding to the correct option. Do not add any additional comment in your response"
            })
            print(json.dumps(messages))
            response = utils.multi_ask(available_keys, messages, model)
        else:
            raise ("Prompt strategy %s is not implemented" % prompt_type)
        messages.append({
            "role": "assistant",
            "content": response})
        with open(msg_file, "w") as file:
            json.dump(messages, file)

    return messages


def convert_sample_format(sample, ans=False):
    query = sample['query']
    org_sample = {"code": sample['data']['code'],
                  "question": query['q'], "options": query['o'], "qid": sample['idx']}
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
    # model = "gpt-4"
    model = args.model

    q_type = args.q_type

    init_client(model)

    dataset = json.load(
        open("data/%s/final_dataset_%s.json" % (args.format, q_type)))
    few_shot_samples = dataset[0:3]
    test_samples = dataset[3:]
    response_messages = []
    dataset_converted = map(convert_sample_format, test_samples)
    few_shot_samples_converted = list(map(
        functools.partial(convert_sample_format, ans=True), few_shot_samples))
    # for sample in tqdm.tqdm(dataset_converted):
    #     pred_results.append(check_question(
    #         sample, prompt_type, few_shot_samples_converted, model, qtype=args.qtype))
    
    wrapped_function = functools.partial(
        check_question, prompt_type=prompt_type, few_shot_samples=few_shot_samples_converted, model=model, qtype=args.q_type, vformat=args.format)
    if args.single:
        for sample in tqdm.tqdm(list(dataset_converted)):
            response_messages.append(wrapped_function(sample))
    else:
        response_messages = process_map(
            wrapped_function, list(dataset_converted), max_workers=8)
    results = []

    for i, sample in enumerate(test_samples):
        if len(sample['data']['code']) < args.min or len(sample['data']['code']) >= args.max:
            continue
        answer = sample['query']['a']
        qid = sample['idx']
        image_id = sample['query']['idx']

        results.append({"msg": response_messages[i], "qid": qid,
                        "image_id": image_id, "answer": answer})

    print("Sample size:", len(results))
    tot_correct = 0
    tot_cnt = 0

    for result in results:
        if result['msg'][-1]['content'] is None:
            continue
        tot_cnt += 1
        assert(result['msg'][-1]['role'] == "assistant")
        if result['msg'][-1]['content'][0] == result['answer']:
            tot_correct += 1
    print("Accuracy:", round(tot_correct/tot_cnt, 3))


if __name__ == '__main__':
    main()
