
<img src="static/img/cover.png" alt="MPADA" class="center" width="350">

**M**ulti**P**ort **A**ntenna **D**ata **A**cquisition (MPADA) is a tool for automating S parameter data collections from MIMO antennas.
The tool enables automatic testing and control to a set of RF switches and Vector Network Analyzer (VNA).

## Feature

- Config number of port and RF switch
- Automatic generate hardware wiring map
- Config sweep setting
  - start/end frequency, number of points, antenna pairs, etc.
- Sweep control and real-time visualization
- Data export

## Installation

- Install required packages using command ```$ conda env create --file environment.yml```
  - if manual install is desired, please refer [Required Packages](#Required--Packages)
- Install VISA driver as required by [PyVISA](https://pyvisa.readthedocs.io/en/latest/introduction/configuring.html)
- Start sweeping!
  - ```$ flask run```
  - - navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Hardware Requirements

- Vector Network Analyzer
  - tested on Keysight PNA series
- RF switch
  - e.g., [HMC321A](https://www.analog.com/en/products/hmc321a.html)
- Microcontroller
  - e.g., [FT232H](https://www.adafruit.com/product/2264), [C232HD](https://ftdichip.com/products/c232hd-ddhsp-0/)
- Antenna
  - aka your design!
- Cable, adapter, etc.

## Roadmap 

- add support to import/export antenna configurations
- add support to dynamic antenna port configuration

## Required Packages

- python
- flask
- python-dotenv
- matplotlib
- numpy
- pandas
- pyvisa
- pyftdi

## About

License: MIT