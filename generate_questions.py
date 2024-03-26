from openai import AzureOpenAI, OpenAI
import utils
import json
from io import BytesIO
import base64
import xlsxwriter
import PIL.Image
import os
import concurrent.futures
import queue

keys = [
]

available_clients = queue.Queue()

question_type = "relation"

for key in keys:
    available_clients.put(AzureOpenAI(
        api_version="2023-07-01-preview",
        azure_endpoint=key["GPT4_V_ENDPOINT"],
        api_key=key["GPT4V_KEY"]
    ))


def generate_system_message(qtype):
    if qtype == "general":
        json_example = {"q": "What is the type of this image?",
                        "o": ["A: Topological Figures", "B: Graphical Figures", "C: Geometric Figures", "D: Three-Dimensional Figures"],
                        "a": "B"}
        return "Generate a JSON object containing a quiz question based on an image rendered from an TiKz file. \
                The caption is also provided to help you better curate the question, but note that the caption is not leaked to the observer. \
                If the caption does not clearly correspond to the image, just discard that caption, never over-rely on the it. \
                The question should be designed to test a model's perception to the image by making the correct answer evident only upon seeing the image. \
                Include four answer options, ensuring that the correct answer is straightforward to identify for someone who actually view this image. \
                The question should relate to the image's semantic category. \
                Provide the JSON structure with fields for the question, the four options (labeled A, B, C, D), and the correct answer indicated. \
                Below is an example of how to structure the question, options and the answer within the JSON format. \
                Example 1: you propose a question :\"What is the type of this image?\" with the following four options,\n \
                A: Topological Figures\n \
                B: Graphical Figures\n \
                C: Geometric Figures\n \
                D: Three-Dimensional Figures\n \
                If the correct answer is B, you should output: %s \
                The example is just for illustrating the format, not for content.\
                Unlike the example, you should focus on the type of the image.\
                Ensuring that the correct answer is straightforward to identify for someone who actually view this image.\
                You are NOT allowed to ask questions about any specific object in the image.\
                Do not add any additional character. Your output should start with \"{\" and end with \"}\"" % json.dumps(json_example)
    elif qtype == "counting":
        json_example = {"q": "How many layers does this neural network have?",
                        "o": ["A: 2", "B: 3", "C: 4", "D: 5"],
                        "a": "B"}
        return "Generate a JSON object containing a quiz question based on an image rendered from an TiKz file. \
            The caption is also provided to help you better curate the question, but note that the caption is not leaked to the observer. \
            If the caption does not clearly correspond to the image, just discard that caption, never over-rely on the it. \
            The question should be designed to test a model's perception to the image by making the correct answer evident only upon seeing the image. \
            Include four answer options, ensuring that the correct answer is straightforward to identify for someone who actually view this image. \
            The question should relate to the image's semantic category. \
            Provide the JSON structure with fields for the question, the four options (labeled A, B, C, D), and the correct answer indicated. \
            Below is an example of how to structure the question, options and the answer within the JSON format. \
            Example 1: you propose a question :\"How many layers does this neural network have?\" with the following four options,\n \
            A: 2\n \
            B: 3\n \
            C: 4\n \
            D: 5\n \
            If the correct answer is B, you should output: %s \
            The example is just for illustrating the format, not for content.\
            Your question should test the model's ability to count specific objects in the image. Your options should be numbers.\
            Ensuring that the correct answer is straightforward to identify for someone who actually view this image.\
            You are NOT allowed to ask questions about any specific object in the image.\
            Do not add any additional character. Your output should start with \"{\" and end with \"}\"" % json.dumps(json_example)
    elif qtype == "relation":
        json_example = {"q": "What's the relation between the red node and the black node?",
                        "o": ["A: the red node is the black node's father",
                              "B: the black node is the red node's father",
                              "C: the red node and the black node are siblings",
                              "D: the red node is the black node's aunt"],
                        "a": "B"}
        return "Generate a JSON object containing a quiz question based on an image rendered from an TiKz file. \
            The caption is also provided to help you better curate the question, but note that the caption is not leaked to the observer. \
            If the caption does not clearly correspond to the image, just discard that caption, never over-rely on the it. \
            The question should be designed to test a model's perception to the image by making the correct answer evident only upon seeing the image. \
            Include four answer options, ensuring that the correct answer is straightforward to identify for someone who actually view this image. \
            The question should relate to the image's semantic category. \
            Provide the JSON structure with fields for the question, the four options (labeled A, B, C, D), and the correct answer indicated. \
            Below is an example of how to structure the question, options and the answer within the JSON format. \
            Example 1: you propose a question :\"What's the relation between the red node and the black node?\" with the following four options,\n \
            A: the red node is the black node's father\n \
            B: the black node is the red node's father\n \
            C: the red node and the black node are siblings\n \
            D: the red node is the black node's aunt\n \
            If the correct answer is B, you should output: %s \
            Another example of acceptable question is \"In which direction is this circle relative to the rectangle?\"\
            The examples are just for illustrating the format, not for content.\
            Your question should test the model's ability to recognize the relationship between different objects in the image.\
            The relation could be relation in positions or the relation in logic.\
            Ensuring that the correct answer is straightforward to identify for someone who actually view this image.\
            You are NOT allowed to ask questions about any specific object in the image.\
            Do not add any additional character. Your output should start with \"{\" and end with \"}\"" % json.dumps(json_example)

    else:
        raise "Unknown type %s" % qtype


def process_image(client: OpenAI, caption: str, img: PIL.Image):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    messages = [
        {
            "role": "system",
            "content": generate_system_message(question_type)
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "The caption of this image is %s, generate the json according to the instruction" % caption
                }, {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,%s" % image_base64},
                }
            ]
        }
    ]
    response = json.loads(utils.ask_gpt(client=client, messages=messages))
    # print(response)
    result = {}
    result['q'] = response['q']
    result['a'] = response['a']
    result['o'] = response['o']
    # result['img'] = img
    assert (len(result['a']) == 1)
    return result


def process_iamge_wrapper(args):
    idx, caption, img = args
    result = None
    while result is None:
        client = available_clients.get()
        try:
            result = process_image(client, caption, img)
        except:
            pass
        available_clients.put(client)
    result['idx'] = idx
    print(result)
    return result


def data_loader(limit):
    idx = 0
    cnt = 0
    dataset = json.load(open("/home/zbc/research/datasets/datikz.json"))
    input_dir = "pngs"
    while cnt < limit:
        img_path = os.path.join(input_dir, "%d.png" % idx)
        if not os.path.exists(img_path):
            idx += 1
            continue
        caption = dataset[idx]['caption']
        img = PIL.Image.open(img_path)
        yield (idx, caption, img)
        idx += 1
        cnt += 1


def main():
    # with concurrent.futures.ThreadPoolExecutor(max_workers=available_clients.qsize()) as executor:
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = list(executor.map(
            process_iamge_wrapper, data_loader(limit=20)))
    print(results)
    with open("questions_%s.json" % question_type, "w") as f:
        json.dump(results, f)


if __name__ == '__main__':
    main()
