
<img src="static/img/cover.png" alt="MPADA" class="center" width="350">

Check out our [MPADA paper](https://arxiv.org/abs/2408.16850)!

**M**ulti**P**ort **A**ntenna **D**ata **A**cquisition (MPADA) is a tool for automating S parameter data collections from MIMO antennas.
The tool enables automatic testing and control to a set of RF switches and Vector Network Analyzer (VNA).

## Feature

- Web based VNA control (remote access possible)
- Single sweep across single/multiple antenna elements
- Time series S-parameter sweep concurrent with other modalities 
- Sequential S-parameter sweep concurrent with other modalities

## Installation

- Install required packages using command ```$ conda env create --file environment.yml```
  - if manual install is desired, please refer [Required Packages](#Required--Packages)
- Install VISA driver as required by [PyVISA](https://pyvisa.readthedocs.io/en/latest/introduction/configuring.html)
- Start sweeping!
  - ```$ flask run```
  - - navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Hardware Requirements

- Vector Network Analyzer
  - tested on Keysight PNA series but works on most VNAs support standard SCPI
- RF switch
  - e.g., [HMC321A](https://www.analog.com/en/products/hmc321a.html)
- Microcontroller
  - e.g., [FT232H](https://www.adafruit.com/product/2264), [C232HD](https://ftdichip.com/products/c232hd-ddhsp-0/), [RP2040](https://www.raspberrypi.com/documentation/microcontrollers/silicon.html) in u2if mode
- Antenna
  - aka your design!
- Cable, adapter, etc.

## Roadmap 

- add support to import/export antenna configurations
- add support to dynamic antenna port configuration

## Required Packages

- python
- gradio
- python-dotenv
- matplotlib
- numpy
- pandas
- pyvisa
- pyftdi

## About

License: MIT

If you use our tool in your research, we kindly ask you cite the following paper:

``` 
@article{chang2024mpada,
  title={MPADA: Open source framework for multimodal time series antenna array measurements},
  author={Chang, Yuyi and Zhang, Yingzhe and Kiourti, Asimina and Ertin, Emre},
  journal={arXiv preprint arXiv:2408.16850},
  year={2024}
}
```