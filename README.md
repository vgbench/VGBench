<div align="center">

## VGBench: Evaluating Large Language Models on Vector Graphics Understanding and Generation 

[Bocheng Zou*](https://www.linkedin.com/in/bocheng-zou/), [Mu Cai*](https://pages.cs.wisc.edu/~mucai/), [Jianrui Zhang](https://pages.cs.wisc.edu/~harrisz/), [Yong Jae Lee](https://pages.cs.wisc.edu/~yongjaelee/)

</div>

<div align="center">

[![Project Page](https://img.shields.io/badge/Project-Page-green.svg)](https://vgbench.github.io/) [![arXiv Paper](https://img.shields.io/badge/arxiv-2407.10972-ECA8A8?logo=arxiv)](https://arxiv.org/abs/2407.10972) [![Code License](https://img.shields.io/badge/Code%20License-Apache_2.0-blue.svg)](https://github.com/vgbench/VGBench/blob/master/LICENSE)

[[🌐 Project Page](https://vgbench.github.io/)] [[📖 Paper](https://arxiv.org/abs/2407.10972)] [[🤗 VGQA](https://huggingface.co/datasets/vgbench/VGQA)] [[🤗 VGen](https://huggingface.co/datasets/vgbench/VGen)]

</div>

## 💥 News

- **[2024.07.15]** 🔥 We released the [VGQA](https://huggingface.co/datasets/vgbench/VGen) dataset.

## 🛠️ Install 

1. Clone this repository and navigate to VGBench folder
``` bash
git clone https://github.com/vgbench/VGBench.git
cd VGBench
```

2. Create the file `keys.py` to load your API Keys into the program. The file `keys.py` should be formated as below.

For each type of model, you can put as many of keys as you want to speed up the evaluation process. Be careful that there is a difference in syntax between the Azure OpenAI and the official OpenAI keys.

```python
keys = {
    "gpt-4v": [
        dict(
            GPT_KEY='SAMPLE-AZURE-API-KEY',
            GPT_ENDPOINT='https://sample-azure-endpoint.openai.azure.com/'
        ),
        dict(
            GPT_KEY='SAMPLE-OPENAI-KEY',
            BASE_URL='https://api.openai.com/v1/'
        )
    "gpt-4": [
        dict(
            GPT_KEY='SAMPLE-AZURE-API-KEY',
            GPT_ENDPOINT='https://sample-azure-endpoint.openai.azure.com/'
        ),
        dict(
            GPT_KEY='SAMPLE-OPENAI-KEY',
            BASE_URL='https://api.openai.com/v1/'
        )
    ],
    "gpt-35-turbo": [
        dict(
            GPT_KEY='SAMPLE-AZURE-API-KEY',
            GPT_ENDPOINT='https://sample-azure-endpoint.openai.azure.com/'
        ),
        dict(
            GPT_KEY='SAMPLE-OPENAI-KEY',
            BASE_URL='https://api.openai.com/v1/'
        )
    ]}
```

You can use [vllm](https://github.com/vllm-project/vllm) to host various open source large language model in a OpenAI compatible API and then add their endpoints to the list above.

3. Download the dataset. You can download the whole dataset from [🤗 VGQA](https://huggingface.co/datasets/vgbench/VGQA). They should be converted to json format and put into `data/{VECTOR_GRAPHICS_FORMAT}/final_dataset_{QUESTION_TYPE}.json`, where `VECTOR_GRAPHICS_FORMAT` should be replaced with one of `svg`, `tikz`, `graphviz` and `QUESTION_TYPE` should be replaced with the name of a specific question type, such as `color`.

## VGQA

Run `evaluate.py`.

```bash
$ python3 evaluate.py -h
usage: evaluate.py [-h] --q-type Q_TYPE --prompt-type {zero-shot,few-shot,zero-shot-cot} --format {svg,tikz,graphviz} --model
                   {gpt-4,gpt-35-turbo,Mixtral-8x7B-Instruct-v0.1,Llama-3-8B-Instruct-262k,Llama-3-70B-Instruct-Gradient-262k} [--min MIN] [--max MAX] [--single]

Evaluate VGQA Dataset

options:
  -h, --help            show this help message and exit
  --q-type Q_TYPE       the type of questions
  --prompt-type {zero-shot,few-shot,zero-shot-cot}
  --format {svg,tikz,graphviz}
                        the format of the vector graphics
  --model {gpt-4,gpt-35-turbo,Mixtral-8x7B-Instruct-v0.1,Llama-3-8B-Instruct-262k,Llama-3-70B-Instruct-Gradient-262k}
                        the model used to evaluate
  --min MIN             filter the lower bound of the lenght of the vector graphics
  --max MAX             filter the upper bound of the lenght of the vector graphics
  --single
```

## VGen

1. Download the [🤗 VGen](https://huggingface.co/datasets/vgbench/VGen) dataset and put it into `data` folder.

1. Run `generate.py` to generate vector graphics using the large language model of your interest.

```bash
$ python3 generate.py -h
usage: generate.py [-h] --format {svg,tikz,graphviz} --model {gpt-4,gpt-35-turbo,Mixtral-8x7B-Instruct-v0.1}

Generate Vector Graphics

options:
  -h, --help            show this help message and exit
  --format {svg,tikz,graphviz}
                        the format of the vector graphics
  --model {gpt-4,gpt-35-turbo,Mixtral-8x7B-Instruct-v0.1}
                        the model used to generate
```

2. Run `render_all_generated.py` with the same parameter to get all generated vector graphics rendered

3. Use `evaluate_clip_score.py` and `evaluate_fid_score.py` to evaluate the generated results.


## Citation

If you find VGBench useful for your research and applications, please cite using this BibTeX:

```bibtex
@article{zou2024vgbench,
    title={VGBench: Evaluating Large Language Models on Vector Graphics Understanding and Generation},
    author={Zou, Bocheng and Cai, Mu and Zhang, Jianrui and Lee, Yong Jae},
    journal={arXiv},
    year={2024}
}
```
