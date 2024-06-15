from openai import OpenAI, AzureOpenAI
import typing
import uuid
import os
import subprocess
import pdf2image
import PIL.Image
import PIL.ImageChops
import re
import typing
import queue
import io
import multiprocessing


def render_graphviz(code: str) -> PIL.Image.Image:
    command = ['dot', '-Tpng']
    p = subprocess.Popen(command, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        stdout, stderr = p.communicate(input=code.encode(), timeout=10)
    except:
        p.terminate()
        return None
    if p.returncode != 0:
        return None
    buffer = io.BytesIO(stdout)
    try:
        image = PIL.Image.open(buffer)
        if image.mode == 'RGBA':
            bg = PIL.Image.new('RGB', image.size, (255, 255, 255))
            bg.paste(image, (0, 0), image)
            image = bg
    except:
        return None
    return image


def render_tikz(code: str) -> PIL.Image.Image:
    # print(code)
    pattern = r'(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\})'
    matches = re.findall(pattern, code, re.DOTALL)
    if len(matches) > 1:
        print("Error: more than 1 tikz picture is found")
        return None
    elif len(matches) == 0:
        print("Error: no tikz picture is found")
        return None
    trimed_code = matches[0]
    # trimed_code = re.search(pattern, code, re.DOTALL).group(1).strip()
    # trimed_code = '\n'.join(trimed_code.split("\n")[1:])
    template = """
    \\documentclass[11pt]{article}
    \\usepackage[active,tightpage]{preview}
    \\usepackage{amsfonts,amsmath,amssymb,amsthm}
    \\usepackage{pgfplots}
    \\usepackage{tikz}
    \\usepackage{tkz-berge}
    
    \\usetikzlibrary{automata}
    \\usetikzlibrary{arrows}
    \\usetikzlibrary{decorations.text}
    \\usetikzlibrary{fit}
    \\usetikzlibrary{matrix}
    \\usetikzlibrary{plotmarks}
    \\usetikzlibrary{positioning}
    \\usetikzlibrary{shapes}
    \\usetikzlibrary{snakes}
    \\usetikzlibrary{trees}
    

    \\begin{document}

    \\begin{preview}
    %s
    \\end{preview}
    \\end{document}
    """ % trimed_code
    # print(template)
    tmp_output = str(uuid.uuid4())
    temp_output_path = os.path.join(tmp_output, "texput.pdf")
    os.makedirs(tmp_output)
    command = ['tectonic', '-o', tmp_output, '-']
    p = subprocess.Popen(command, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.communicate(input=template.encode())
    if p.returncode != 0:
        print("Error!")
        os.removedirs(tmp_output)
        return None
    try:
        img = pdf2image.convert_from_path(temp_output_path)
    except:
        return None
    os.remove(temp_output_path)
    os.removedirs(tmp_output)
    assert (len(img) == 1)
    return img[0]


def ask_gpt(client: OpenAI, messages: typing.List[typing.Dict[str, str]], model: typing.Literal["gpt-35-turbo", "gpt-4", "gpt-4-32k", "gpt-4v"]):
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=4096,
        temperature=0
    )
    assert (completion.choices[0].finish_reason == "stop"), "Context length exceeded"
    return completion.choices[0].message.content


def multi_ask(available_keys: multiprocessing.Queue, messages, model):
    success = False
    while not success:
        key = available_keys.get()
        if "GPT_ENDPOINT" in key.keys():
            client = AzureOpenAI(
                api_version="2024-02-01",
                azure_endpoint=key["GPT_ENDPOINT"],
                api_key=key["GPT_KEY"],
                timeout=40
            )
        else:
            client = OpenAI(
                api_key=key["GPT_KEY"],
                base_url=key["BASE_URL"]
            )
        # print("Querying", client.base_url)
        try:
            if "ALT_NAME" in key.keys():
                model = key["ALT_NAME"]
            if "NO_SYSTEM" in key.keys():
                if messages[0]['role'] == "system":
                    assert(messages[1]['role']=="user")
                    messages[1]['content'] = messages[0]['content'] + messages[1]['content']
                    del messages[0]
                    # print(messages)
            response = ask_gpt(client, messages, model=model)
            success = True
        except Exception as e:
            print("[GPT FAILED]", client.base_url, str(e))
            if "ResponsibleAIPolicyViolation" in str(e) or "Context length exceeded" in str(e) or "This model's maximum context length " in str(e):
                response = None
                success = True  # we shouldn't try this sample again
        # print("Complete", client.base_url, response)
        client.close()
        available_keys.put(key)
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
