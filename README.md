# Nervana Graph

Nervana graph is Nervana's library for developing frameworks that can efficiently run deep
learning computations on a variety of compute platforms. It consists of three primary API
components:

- An API for creating computational `Nervana Graphs`.
- Two higher level frontend APIs (TensorFlow and Neon) utilizing the `Nervana Graph` API for common deep learning workflows
- A transformer API for compiling these graphs and executing them.

For more information, please see the [blog
post](https://www.nervanasys.com/intel-nervana-graph-preview-release/) announcing our
preview release!

## Installation

Installation documentation can be found
[here](https://ngraph.nervanasys.com/docs/latest/installation.html).

We recommend installing Nervana Graph inside a virtual environment.

To create and activate a Python 2.7 virtualenv:
```
virtualenv -p python2.7 .venv
. .venv/bin/activate
```

To, instead, create and activate a Python 3 virtualenv:
```
python3 -m venv .venv
. .venv/bin/activate
```

To install Nervana Graph:
```
make install
```

To uninstall Nervana Graph:
```
make uninstall
```

To run the tests:
```
make [test_cpu|test_gpu|test_integration]
```

Before checking in code, ensure no "make style" errors:
```
make style
```

To fix style errors:
```
make fixstyle
```

To generate the documentation as html files:
```
make doc
```

## Examples

* ``examples/walk_through/`` contains several code walk throughs.
* ``examples/mnist/mnist_mlp.py`` uses the neon front-end to define and train a MLP model on MNIST data.
* ``examples/cifar10/cifar10_conv.py`` uses the neon front-end to define and train a CNN model on CIFAR10 data.
* ``examples/cifar10/cifar10_mlp.py`` uses the neon front-end to define and train a MLP model on CIFAR10 data.
* ``examples/ptb/char_rnn.py`` uses the neon front-end to define and train a character-level RNN model on Penn Treebank data.

## Overview

### Frontends
- The neon frontend offers an improved interface for increased composability/flexibility
  while leaving common use cases easy. We demonstrate this with MLP, convolutional, and
  RNN network examples on MNIST, CIFAR10, and Penn Treebank datasets.
- The tensorflow importer allows users to import existing tensorflow graphs and execute
  them using Nervana Graph transformers/runtimes. This importer currently only supports a
  subset of the tensorflow API, but this will be expanded over time.

### Nervana Graph API
- The Nervana Graph API consists of a collection of graph building functions all exposed
  in the `ngraph` module/namespace. (eg: `ngraph.sum(...)`)
- We include walkthrough examples to use this API for logistic regression and multilayer
  perceptron classification of MNIST digit images.
- With the introduction of named `Axes` we lay the foundation for frontend writers to
  reason about tensor axis without concern of memory layout or order (for future
  optimization against hardware targets which often have differing and specific
  requirements for batch axis orderings for example).

### Transformer API
- This release ships with two example transformers targetting CPU and GPU hardware targets. 
- Both transformers support memory usage optimization passes.
- The GPU transformer also includes preliminary support for automatic kernel
  fusion/compounding for increased performance.
- Transformers allow users to register an included set of optional compiler passes for
  debug and visualization.
- The compiler pass infrastructure is slated to offer frontends/users similar flexibility
  to what LLVM library offers for general purpose compilation.

### Known Issues
These are known issues which are being addressed:

- The transformer fusion and memory sharing optimizations are currently hampered by some
  of the tensor dimension reshaping introduced by the existing lowering passes. Thus both
  are turned off by default.
- RNNs don't work well with longer sequences (longer than 30).

## Highlighted Future Work

- Nervana Graph serialization/deserialization.
- Further improvements/abstractions to graph composability for usability/optimization.
- Distributed, heterogeneous backend target support.
- C APIs for interoperability to enable other languages to create/execute graphs.
- Better debugging
- Support for model deployment

## Join Us
Please feel free to [contribute](CONTRIBUTING.rst) in shaping the future of Nervana Graph.
