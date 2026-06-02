[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![CI](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/actions/workflows/ci.yml?query=branch%3Amain)
[![CodeQL](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/actions/workflows/codeql.yml?query=branch%3Amain)

# AsdSte100Issue9TrainingData

Training datasets for ASD-STE100 Issue 9.

**WIP** no training data yet available!!

This training dataset let you fine-tune an LLM to better understand, what the words in the "ASD-STE100 Issue 9" standard mean.

## Datasets

Each dataset corresponds to a sub-command of the `create` CLI and a
GitHub issue that tracks its design and progress. The default output
file for every command is a JSON Lines file named
`taskNN.jsonl` in the current working directory; pass `--output` and
`--file` to override.

| Command | Task | Default output | Status |
| --- | --- | --- | --- |
| `ambiguity` | Task 1: Ambiguity ([#1](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/1)) | `task01.jsonl` | Stub |
| `lexicon` | Task 2: Explicit Lexicon Lookup (Word + POS Level) ([#2](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/2)) | `task02.jsonl` | Stub |
| `pos` | Task 3: POS Identification in Context ([#3](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/3)) | `task03.jsonl` | Stub |
| `rewrite` | Task 4: Sentence Rewriting for Compliance ([#4](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/4)) | `task04.jsonl` | Stub |
| `compliance` | Task 5: Compliance Verification of Correct Usage ([#5](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/5)) | `task05.jsonl` | Stub |
| `choice` | Task 6: Word Choice Between Approved Synonyms ([#6](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/6)) | `task06.jsonl` | Stub |
| `restriction` | Task 7: Restriction Reason Explanation ([#7](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/7)) | `task07.jsonl` | Stub |
| `paragraph` | Task 8: Full Paragraph Compliance Audit ([#8](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/8)) | `task08.jsonl` | Stub |
| `grammar` | Task 9: Internal Grammar Engine (POS Identification) ([#9](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/9)) | `task09.jsonl` | Stub |
| `verb` | Task 10: Approved Verb Lookup by Definition ([#10](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/10)) | `task10.jsonl` | Stub |
| `category` | Task 11: Category-Based Word Restrictions ([#11](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/11)) | `task11.jsonl` | Stub |
| `query` | Interactive ASD-STE100 query against a chat model | `response-<timestamp>.json` | **WIP** |

### Progress

At this time only the `query` command is implemented. It tokenises and
lemmatises an input string with spaCy, then runs a Pydantic AI agent
against a configured chat model. The agent has access to the
`get_word_status` and `get_word_alternative` tools, which look words
up in the ASD-STE100 vocabulary, and is required to return a JSON
response listing every word together with a short summary and its
ASD-STE100 status.

# Train the model

Here are the steps that I use to train the model with the training data on a system with NVIDIA GPUs:

* Dataset is on [HuggingFace](https://huggingface.co/)
* Model is on [HuggingFace](https://huggingface.co/)
* Preparation
* [NVIDIA-NeMo AutoModel](https://github.com/NVIDIA-NeMo/Automodel) fine-tunes the model to the HF format
* [llama.cpp](https://github.com/ggml-org/llama.cpp) convert the consolidated HF model to GGUF
* [llama.cpp](https://github.com/ggml-org/llama.cpp) quantises the GGUF model (examples: `Q4_K_M`, `Q5_K_M`, `Q6_K`, `Q8_0`)

## Requirements

This is the system configuration that I use (`SYS0`). There *may* be other or better configurations that work, too.

* Intel w9 x86_64, 60 cores, 512 GB RAM
* 4 * NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation (300 W), each 96 GB VRAM
* more than 1 TB of free disk space
* Docker, docker compose
* Ubuntu 24.04 LTS
* NVIDIA open-drivers, driver version v595.71.05, CUDA version v13.2

NOTE: This also works on my small NVIDIA DGX Spark system (`DGX`) - but much slower.

## Dataset

Because we use `AutoModel` you must create the dataset on [HuggingFace](https://huggingface.co/). A free account is sufficient. The dataset name has this format: `organisation/dataset-name`.

## Model

Again, because we use `AutoModel` you must use a model from [HuggingFace](https://huggingface.co/). For this example, use [`Qwen/Qwen3-8B`](https://huggingface.co/Qwen/Qwen3-8B).

## Preparation

### Docker and NVIDIA

* Install docker in `rootless` mode.
* Install the NVIDIA toolkit directly from the NVIDIA repository.
* Test the configuration with the [Hello, world! container](https://hub.docker.com/_/hello-world/) and the [Running a sample workload with Docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html#running-a-sample-workload-with-docker):

```
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

### HuggingFace API token

You must have an `HF_TOKEN` (an HuggingFace API token). We use it:

* inside the `AutoModel` container, when we download the dataset and the model
* on `SYS0`, when we upload the dataset

```
export HF_TOKEN=hf_your_token
```

NOTE: you *COULD* also set it as an environment variable in your `docker-compose.yaml`.

### NVIDIA NeMo AutoModel container

* The code for [NVIDIA-NeMo AutoModel](https://github.com/NVIDIA-NeMo/Automodel) is on GitHub, but it does not install on my system (not on `SYS0` and not on `DGX`). There are incompatibilities between `PyTorch`, CUDA and others that I cannot resolve. 

* Therefore, use the [nemo-automodel:26.04](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nemo-automodel/tags?version=26.04) container:

    ```
    docker pull nvcr.io/nvidia/nemo-automodel:26.04
    ```

* All `AutoModel` executables are already installed in `/opt/Automodel/`.

### Directories

* The most important directory in `AutoModel` for us is the `checkpoints` directory. `AutoModel` records the data of checkpoints here: `/opt/Automodel/checkpoints/`.

* `AutoModel` downloads the model and dataset when it does not find it in the cache file.

* Make sure that `Docker` (as `root`) and your `$USER` have access to the mapped directories. Use `chown -R ...` to get access without `sudo`.


### `docker-compose.yaml`

* On `SYS0` create a folder `automodel`:

    ```
    mkdir -p ~/docker/automodel
    ```

* Then, create the file `docker-compose.yaml`:

    ```
    nano ~/docker/automodel/docker-compose.yaml
    ```

* This is the content of the file `docker-compose.yaml`:

    ```
    services:
    automodel:
        image: nvcr.io/nvidia/nemo-automodel:26.04
        container_name: automodel
        user: "0:0"
        volumes:
        - /data/automodel/checkpoints:/opt/Automodel/checkpoints
        - /data/nvidia/workspace:/workspace
        # TODO - examine the volume mappings.
        - /data/nvidia/models:/models
        - /data/nvidia/datasets:/datasets
        - /data/nvidia/results:/results
        - /data/nvidia/hf_cache:/root/.cache/huggingface
        working_dir: /workspace
        ipc: host
        ulimits:
        memlock: -1
        stack: 67108864
        deploy:
        resources:
            reservations:
            devices:
                - driver: nvidia
                count: all
                capabilities: [gpu]
        tty: true
        stdin_open: true
        entrypoint: /usr/bin/bash
        environment:
        - TRANSFORMER_ENGINE_PTE=1
        - NVIDIA_VISIBLE_DEVICES=all
        # Optional, but then you have to restrict access to your configuration file:
        - HF_TOKEN=hf_your_token
    ```

* You find the configuration file [here](./configuration/docker-compose.yaml).

* Start the container in `~/docker/automodel` with:

    ```
    docker compose up -d
    ```

### Recipe

* `Automodel` has example recipes in `/opt/Automodel/examples`. We can copy our example to this folder or specify the location of the 

* You find the recipe for the example model [here](./configuration/qwen3_8b-asd-ste100.yaml).

### `llama.cpp`

* Install `cmake` if necessary:

    ```
    sudo apt-get install -y cmake
    ```

* Clone the `llama.cpp` repository in `~/src/`:

    ```
    mkdir -p ~/src
    cd ~/src
    git clone https://github.com/ggml-org/llama.cpp.git
    cd ~/src/llama.cpp
    git pull
    ```

* Install `requirements` for `the HF converter`:

    When you have no `pip` install it into your cloned folder with:
    ```
    cd ~/src/llama.cpp
    uv add pip
    ```

    Create a virtual environment:
    ```
    cd ~/src/llama.cpp
    uv venv
    ```

    ```
    uv pip install -r requirements/requirements-convert_hf_to_gguf.txt
    ```

    NOTE: on `DGX` I got this dependency error: `there is no version of transformers==5.5.1`. I used `--index-strategy unsafe-best-match` to override this and install from [`nightly`](https://download.pytorch.org/whl/nightly).

* Build `llama.cpp`:

    ```
    cd ~/src/llama.cpp
    rm -rf build
    cmake -B build
    cmake --build build --config Release -j$(nproc)
    ```

* If you only want to build the `quantizer`:

    ```
    cd ~/src/llama.cpp
    rm -rf build
    cmake -B build
    cmake --build build --config Release -j$(nproc) --target llama-quantize
    ```

## Fine-tune

Copy the recipe into the `/workspace` folder:

Do a full fine-tune of the model and start this command in the container:

```
cd /workspace
automodel qwen3_8b_asd-ste100_spark-asd-ste100.yaml \
  --nproc-per-node 4
```

NOTE: you can start a shell in the container with: `docker exec -it automodel bash`.

NOTE: This takes about 30 minutes on `SYS0`. The time to create a checkpoint is about 3 minutes. We get around 2900 tps (725 tps/GPU).

When the work step is complete, you find the consolidated model here:

```
/workspace/checkpoints/LOWEST_VAL/model/consolidated/
```

NOTE: `Automodel` *consolidates* the model from all 4 GPUs automatically.

## Convert from HF to GGUF

`AutoModel` creates a model in the HuggingFace format. On `SYS0` convert it to GGUF:

```
cd ~/src/llama.cpp/
python convert_hf_to_gguf.py \
  /workspace/checkpoints/LOWEST_VAL/model/consolidated \
  --outfile /workspace/checkpoints/qwen3-8b-asd-ste100-bf16.gguf \
  --outtype bf16
```

NOTE: This will convert the model and put it in the directory `/workspace/checkpoints/`

## Quantise the model (optional)

```
cd ~/src/llama.cpp/
```

### Quantise the model to `Q8_0`

```
./build/bin/llama-quantize \
  /workspace/checkpoints/qwen3-8b-asd-ste100-bf16.gguf \
  /workspace/checkpoints/qwen3-8b-asd-ste100-q8_0.gguf \
  Q8_0
```

### Quantise the model to `Q6_K`

```
./build/bin/llama-quantize \
  /workspace/checkpoints/qwen3-8b-asd-ste100-bf16.gguf \
  /workspace/checkpoints/qwen3-8b-asd-ste100-q6_k.gguf \
  Q6_K
```

### Quantise the model to `Q5_K_M`

```
./build/bin/llama-quantize \
  /workspace/checkpoints/qwen3-8b-asd-ste100-bf16.gguf \
  /workspace/checkpoints/qwen3-8b-asd-ste100-q5_k_m.gguf \
  Q5_K_M
```

### Quantise the model to `Q4_K_M`

```
./build/bin/llama-quantize \
  /workspace/checkpoints/qwen3-8b-asd-ste100-bf16.gguf \
  /workspace/checkpoints/qwen3-8b-asd-ste100-q4_k_m.gguf \
  Q4_K_M
```

### Size of the models:

```
15263 MB qwen3-8b-squad-bf16.gguf
 8307 MB qwen3-8b-squad-q8_0.gguf
 6415 MB qwen3-8b-squad-q6_k.gguf
 5581 MB qwen3-8b-squad-q5_k_m.gguf
 4683 MB qwen3-8b-squad-q4_k_m.gguf
```

## Create the `Modelfile`

You must adjust the name of the GGUF file in the line that starts with `FROM`.

```
FROM qwen3-8b-asd-ste100-q6_k.gguf

SYSTEM """You are a precise technical writer and requirements engineer specialised in ASD-STE100 (Simplified Technical English). Answer concisely based only on the provided context. /no_think"""

TEMPLATE """{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{- range .Messages }}<|im_start|>{{ .Role }}
{{ .Content }}<|im_end|>
{{ end }}<|im_start|>assistant
"""

PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.2
PARAMETER top_p 0.8
PARAMETER num_ctx 4096
PARAMETER num_predict 512
```

You find the `Modelfile` [here](./configuration/Modelfile).

When you use `Ollama` you can create a model in the directory with the GGUF file and Modelfile with this:

```
ollama create qwen3-8b-asd-ste100
```
