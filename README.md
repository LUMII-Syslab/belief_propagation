# Belief Propagation-based SAT solver

[Belief Propagation](https://en.wikipedia.org/wiki/Belief_propagation) is a message-passing algorithm that can be used to solve SAT instances.

# Prerequisites

```bash
sudo apt install python3-networkx python3-matplotlib
```

# Run
See file `TestBeliefPropagation.py` to find out how to invoke the Belief Propagation algorithm.

There are two implementations:
* bp.py - the traditional belief propagation
* bpV.py - vertex-based belief propagation suitable for Graph Neural Networks, GNNs

