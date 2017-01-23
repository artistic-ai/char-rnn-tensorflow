# char-rnn-tensorflow
Multi-layer Recurrent Neural Networks (LSTM, RNN) for character-level language models in Python using Tensorflow.

Inspired from Andrej Karpathy's [char-rnn](https://github.com/karpathy/char-rnn).

# Requirements
- [Tensorflow 1.0](http://www.tensorflow.org)
- [PyYaml](http://pyyaml.org)

```sh
pip install -r requirements.txt
```

# Usage

## Setup datasets and models
 
To download all datasets and pretrained models described in `config.yaml` use

```sh
./main --datasets-all
```

To setup specific datasets
 
```sh
./main --datasets <dataset name> [<dataset name>...]
```

## Train models

To train default model for dataset

```sh
./main --train dataset
```

For specific model

```sh
./main --train <dataset name> --model <model name> 
```

Both `dataset name` and `model name` should be specified in `config.yaml`.  

## Print samples

To sample from a checkpointed model

```sh
./main.py --sample <dataset name> --model <model name>
```

Or simply omit model name for default model

```sh
./main.py --sample <dataset name>
```

# Roadmap
- Add explanatory comments
- Expose more command-line arguments
- Compare accuracy and performance with char-rnn
