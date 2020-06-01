# Dutch FrameNet annotations on SoNaR corpus

We extended the PropBank annotation of the SoNaR corpus with FrameNet1.7 frames and frame-elements. The annotation was funded through the Vossen-Spinoza project [Understanding-Language-By-Machines][http://www.understandinglanguagebymachines.org].

The goal of this repository is load the FrameNet annotations on the Dutch corpus SoNaR into Python classes.

### Prerequisites

Python 3.7 was used to create this project. It might work with older versions of Python.

### Installing

A number of external modules need to be installed, which are listed in **requirements.txt**.
Depending on how you installed Python, you can probably install the requirements using one of following commands:
```bash
pip install -r requirements.txt
```

## Contents
* **corpus**: the annotation from each annotator
* **lexicon**: the derived FrameNet lexicon from the annotations
* **report**: the annotation report
* **scripts**: Python modules to load annotations into Python classes

## How to use
Please call **python main.py -h** in **scripts** for information on how to use.

This creates for the annotation of one annotator a dictionary mapping:
* **key**: (document name, event mention id)
* **value**: a instance of the **Frame** class (see *sonar_classes.py)

## Authors
* **Piek Vossen** (p.t.j.m.vossen@vu.nl)
* **Isa Maks** (isa.maks@vu.nl)
* **Chantal van Son** (c.m.van.son@vu.nl)
* **Marten Postma** (m.c.postma@vu.nl)

## TODO
* the mapping in **utils.cat_pos2fn_pos** is done on a practical basis, it can be expanded.
## License
This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
