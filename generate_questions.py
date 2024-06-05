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
from keys import keys, PERSONAL_GPT_KEY
import argparse
from tqdm.contrib.concurrent import process_map
import tqdm

# gpt_model = "gpt-4-turbo"
gpt_model = "gpt-4v"

available_clients = queue.Queue()

# available_clients.put(OpenAI(api_key=PERSONAL_GPT_KEY))
for key in keys[gpt_model]:
    available_clients.put(AzureOpenAI(
        api_version="2024-02-01",
        azure_endpoint=key["GPT_ENDPOINT"],
        api_key=key["GPT_KEY"],
        timeout=10
    ))


def generate_system_message(vector_format: str, qtype: str):
    if vector_format == "tikz":
        if qtype == "concept":
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
                    Do not add any additional character including \"`\". Your output should start with \"{\" and end with \"}\"" % json.dumps(json_example)
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
                The understanding of those relationships should be required to answer the question correctly.\
                The relation could be relation in positions or the relation in logic.\
                Ensuring that the correct answer is straightforward to identify for someone who actually view this image.\
                You are NOT allowed to ask questions about any specific object in the image.\
                Do not add any additional character. Your output should start with \"{\" and end with \"}\"" % json.dumps(json_example)

        else:
            raise "Unknown type %s" % qtype
    elif vector_format == "graphviz":
        if qtype == "domain":
            json_example = {"q": "What is the main domain of this image?",
                            "o": ["A: Social Networks", "B: Knowledge Graphs", "C: State Machine", "D: Financial Networks"],
                            "a": "B"}
            return "Generate a JSON object containing a quiz question based on an image rendered from an Graphviz file. \
                    Your question should test the model's ability to recognize the domain or the main concept of the graph, do not ask about counting or orientation.\
                    The caption is also provided to help you better curate the question, but note that the caption is not leaked to the observer. \
                    If the caption does not clearly correspond to the image, just discard that caption, never over-rely on the it. \
                    The question should be designed to test a model's perception to the image by making the correct answer evident only upon seeing the image. \
                    Include four answer options, ensuring that the correct answer is straightforward to identify for someone who actually view this image. \
                    Provide the JSON structure with fields for the question, the four options (labeled A, B, C, D), and the correct answer indicated. \
                    Below is an example of how to structure the question, options and the answer within the JSON format. \
                    Example 1: you propose a question :\"%s\" with the following four options,\n \
                    %s\n \
                    %s\n \
                    %s\n \
                    %s\n \
                    If the correct answer is B, you should output: %s \
                    The example is just for illustrating the format, not for content.\
                    Ensuring that the correct answer is straightforward to identify for someone who actually view this image.\
                    You are NOT allowed to ask questions about any specific object in the image.\
                    Do not add any additional character. Your output should start with \"{\" and end with \"}\"" % (json_example['q'], json_example['o'][0], json_example['o'][1], json_example['o'][2], json_example['o'][3], json.dumps(json_example))
        elif qtype == "layout":
            json_example = {"q": "Which of the following best describes the overall layout of the vector graphic?",
                            "o": ["A: sequential top-to-bottom flow with nodes connected by arrows",
                                  "B: A circular layout with nodes connected in a loop",
                                  "C: A tree structure with branching nodes",
                                  "D: A grid layout with interconnected nodes"],
                            "a": "A"}
            return "Generate a JSON object containing a quiz question based on an image rendered from an Graphviz file. \
                    Your question should test the model's ability to describe the layout of the graph.\
                    You can ask about orientation, but do not ask about counting. \
                    Your question should be a general question, not those about any specific object in the image.\
                    The caption is also provided to help you better curate the question, but note that the caption is not leaked to the observer. \
                    If the caption does not clearly correspond to the image, just discard that caption, never over-rely on the it. \
                    The question should be designed to test a model's perception to the image by making the correct answer evident only upon seeing the image. \
                    Include four answer options, ensuring that the correct answer is straightforward to identify for someone who actually view this image. \
                    Provide the JSON structure with fields for the question, the four options (labeled A, B, C, D), and the correct answer indicated. \
                    Below is an example of how to structure the question, options and the answer within the JSON format. \
                    Example 1: you propose a question :\"%s\" with the following four options,\n \
                    %s\n \
                    %s\n \
                    %s\n \
                    %s\n \
                    If the correct answer is %s, you should output: %s \
                    The example is just for illustrating the format, not for content. You shouldn't ask question in the same format as that in the example.\
                    Ensuring that the correct answer is straightforward to identify for someone who actually view this image.\
                    Do not add any additional character. Your output should start with \"{\" and end with \"}\"" % (json_example['q'], json_example['o'][0], json_example['o'][1], json_example['o'][2], json_example['o'][3], json_example['a'], json.dumps(json_example))

    raise "Unknown type %s" % qtype


def generate_dummy_response() -> dict:
    response = {}
    response['q'] = "Not able to parse"
    response['a'] = "A"
    response['o'] = ["A", "B", "C", "D"]
    return response


def scale_image(image: PIL.Image, max_edge: int = 1024) -> PIL.Image:
    """
    Scale the image so that its longest edge is equal to `max_edge` pixels.

    :param image: PIL.Image object to be scaled.
    :param max_edge: The size of the longest edge in the scaled image.
    :return: Scaled PIL.Image object.
    """
    # Get current size of the image
    width, height = image.size

    # Calculate the scaling factor
    if width > height:
        new_width = max_edge
        new_height = int((max_edge / width) * height)
    else:
        new_height = max_edge
        new_width = int((max_edge / height) * width)

    # Resize the image
    scaled_image = image.resize((new_width, new_height), PIL.Image.LANCZOS)

    return scaled_image


def process_image(client: OpenAI, caption: str, img: PIL.Image, vector_format: str, q_type: str, vec_file_content: str):
    if img.size[0] > 1024 or img.size[1] > 1024:
        img = img.copy()
        img = scale_image(img, 1024)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    system_message = generate_system_message(vector_format, q_type)
    # print(system_message)

    messages = [
        {
            "role": "system",
            "content": system_message
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
    if vec_file_content != "":
        messages.append({
            "role": "user",
            "content": "The vector graphics file is %s" % vec_file_content
        })
    try:
        gpt_response = utils.ask_gpt(
            client=client, messages=messages, model=gpt_model)
    except Exception as e:
        print("[GPT FAILED]", client.base_url, str(e))
        if "ResponsibleAIPolicyViolation" in str(e):
            gpt_response = json.dumps(generate_dummy_response())
        else:
            return None
    if gpt_response.startswith("```json"):
        gpt_response_lines = gpt_response.split("\n")
        gpt_response = "\n".join(gpt_response_lines[1:-1])
    try:
        response = json.loads(gpt_response)
    except Exception as e:
        print("[PARSER FAILED]", gpt_response, e)
        response = generate_dummy_response()
    # print(response)
    result = {}
    result['q'] = response['q']
    result['a'] = response['a']
    result['o'] = response['o']
    # result['img'] = img
    if result['a'] not in "A" and result['a'] not in "B" and result['a'] not in "C" and result['a'] not in "D":
        return None
    return result


def process_image_wrapper(args):
    idx, caption, vec_file_content, img, vector_format, q_type = args
    result = None
    while result is None:
        client = available_clients.get()
        result = process_image(client, caption, img,
                               vector_format, q_type, vec_file_content)
        available_clients.put(client)
    result['idx'] = idx
    # print(result)
    return result


def data_loader(vector_format, q_type, limit, dataset: str, png_path: str, provide_vec: True):
    idx = 0
    cnt = 0
    dataset = json.load(open(dataset))
    while cnt < limit:
        img_path = os.path.join(png_path, "%d.png" % idx)
        if not os.path.exists(img_path):
            idx += 1
            continue
        caption = dataset[idx]['caption']
        code = ""
        if provide_vec:
            code = dataset[idx]['code']
        img = PIL.Image.open(img_path)
        yield (idx, caption, code, img, vector_format, q_type)
        idx += 1
        cnt += 1


def default_argument_parser():
    parser = argparse.ArgumentParser(description="generate questions")
    parser.add_argument(
        "--q-type", default="", required=True, help="the type of questions")
    parser.add_argument(
        "--dataset", default="", required=True, help="the path to the dataset's json file")
    parser.add_argument(
        "--png-path", default="", required=True, help="the path to the rastered png directory")
    parser.add_argument(
        "--format", choices=["tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")

    return parser


def main():
    args = default_argument_parser().parse_args()
    q_type = args.q_type
    # with concurrent.futures.ThreadPoolExecutor(max_workers=available_clients.qsize()) as executor:
    # with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    #     results = list(executor.map(
    #         process_image_wrapper, data_loader(args.format, q_type, limit=550, dataset=args.dataset, png_path=args.png_path, provide_vec=True)))
    results = []
    data_generator = data_loader(args.format, q_type, limit=550,
                                 dataset=args.dataset, png_path=args.png_path, provide_vec=False)
    # for data in tqdm.tqdm(data_generator):
    #     results.append(process_image_wrapper(data))
    results = process_map(process_image_wrapper,
                          data_generator, max_workers=16)
    print(results)
    with open("data/graphviz/questions_%s.json" % q_type, "w") as f:
        json.dump(results, f)


if __name__ == '__main__':
    main()
