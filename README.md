# CVD-Agent-Based-Model

This repository contains the implementation of an agent-based-model of behaviour spread and its impact on cardiovascular disease developed by the project "Modelling the spread of multiple behavioural risk factors for cardiovascular disease in social networks using an agent-based model", N. Griffiths, O. Oyebode and J. Archbold, funded by MRC as part of the Population Health Agent-based Simulation nEtwork (PHASE).

The paper describing the model is under preparation, and if you use our model in your own publications we would appreciate you citing our paper (details to be added here on publication). There is also a webinar describing the model here (see 58:40 onwards): https://www.youtube.com/watch?v=lD6Y1LcjxXE

The code has been tested on Mac and Linux using Python3, but is untested on Windows. The following directory structure is assumed (note that you may need to manually create the results and plots directories):

* documentation/ - Contains more detail of the algorithms/methods used in the simulation. More details can be found in the paper mentioned above.
* scenarios/ - Contains the configurations which can be used to run the simulation. By default this contains two example sub-directories, namely baseline_workplaceContacts4 and baseline_workplaceContacts21, with mean workplace close contact sizes of 4 and 21 respectively. These configurations are calibrated to UK data as described in the paper mentioned above. Additional experiment can be added to this directory.
* results/ - The simulation stores results here. Two files are stored directly by the simulator, namely <config>_all.pkl and <config>_latest.csv which contain summary data for all runs of a given config (i.e., latest run results are appended) and the latest run respectively. To generate a csv of summary data for all runs use process_results.py with a .pkl filename as a argument, which will create <config>_all.pkl.
* plots/ - network.py, if run with the --plots argument, can generate a plot of the age distribution and friendship degree distribution for the given configuration, with pdf plots of these stored in this folder. Note that for the friendship degree distribution some lines in network.py need uncommenting (they are currently commented to reduce memory overhead when the distribution plot is not needed).

To see the possible arguments run spread.py with the -h argument:

```
python3 spread.py -h
```
which should give the following output:
```
usage: spread.py [-h] [-n SIZE] [-t TIMESTEP] parameter_folder

spread - create a network and run spread for CVD simulation.

positional arguments:
  parameter_folder      folder of csv files with parameter specifications

optional arguments:
  -h, --help            show this help message and exit
  -n SIZE, --size SIZE  target population size
  -t TIMESTEP, --timestep TIMESTEP
                        select number of timesteps for simulation
```
