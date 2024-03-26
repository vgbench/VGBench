from openai import OpenAI
import typing
import uuid
import os
import subprocess
import pdf2image
import PIL.Image
import PIL.ImageChops
import re


def render_tikz(code) -> PIL.Image.Image:
    print(code)
    pattern = r'(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\})'
    matches = re.findall(pattern, code, re.DOTALL)
    if len(matches)>1:
        print("Error: more than 1 tikz picture is found")
        return None
    elif len(matches) ==0:
        print("Error: no tikz picture is found")
        return None
    trimed_code = matches[0]
    #trimed_code = re.search(pattern, code, re.DOTALL).group(1).strip()
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


def ask_gpt(client: OpenAI, messages: typing.List[typing.Dict[str, str]]):
    completion = client.chat.completions.create(
        model="gpt-4v",
        messages=messages,
        max_tokens=4096
    )
    assert (completion.choices[0].finish_reason == "stop")
    return completion.choices[0].message.content
