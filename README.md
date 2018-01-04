# Dumbledraw plotting tool
The Dumbledraw module receives, processes and plots ROOT histograms (TH1F) according to the common style in the Higgs to tau tau analyses.

## Introduction
A basic introduction is given here. A detailed example showing most of the functionalities is given in `example_script.py`.

Every plot is created as an instance of the class `plot` containing one or more instances of the class `subplot`:
```bash
plot = dumbledraw.Plot([[0.5, 0.48]], <style args>)
```
This creates two subplots with a gap between 48% and 50% of the plotting area.
The subplots are defined via a list of split points (top down), which can be doublets in case of gaps.

Histograms can be registered in a (sub)plot under a given nickname and modified e.g. normalized to other histograms before plotting:
```bash
plot.subplot(0).add_hist(histogram1, "signal")
plot.subplot(0).add_hist(histogram2, "background")
plot.subplot(0).normalize("signal", "background")
```
Many methods of `subplot` are also implemented for `plot` calling the same method for all subplots, e.g.:
```bash
plot.add_hist(histogram1, "signal")
```
Apply individual graph styles optionally making use of the `Dumbledraw.styles` module and finally plot and save selected histograms:
```bash
plot.subplot(0).setGraphStyle("signal", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
plot.subplot(0).Draw(["signal"])
plot.save("plot.pdf")
```

## Dumbledraw/rootfile_parser.py
The `rootfile_parser` module is an independent module that can be used to easily extract the histograms from the CombineHarvester ROOT files.
