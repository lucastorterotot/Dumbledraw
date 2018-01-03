#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles

import argparse
from copy import deepcopy

import logging
logger = logging.getLogger("")


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def main():
    rootfile = rootfile_parser.Rootfile_parser("datacard_shapes_prefit.root")

    # create canvas:
    #   First argument defines subplot structure: List of splits from top to bottom (max. 1.0 to min. 0.0). A split can be a single position or a pair resulting in gap.
    #   Further arguments set general style.
    plot = dd.Plot(
        [0.65, [0.47, 0.45], [0.22, 0.20]], "ModTDR", r=0.04, l=0.14)

    bkg_processes = ["EWK", "QCD", "VV", "W", "TTT", "TTJ", "ZJ", "ZL", "ZTT"]

    # register histograms in the subplots (can be done globally or for specific subplots). regustered histograms are not necessarily plotted later.
    for process in bkg_processes:
        plot.add_hist(
            rootfile.get("mt", "qqh", process), process, "bkg"
        )  # get(channel, category, process) and assign specific name and group name to histogram. The group name is optional.
        plot.setGraphStyle(
            process, "hist", fillcolor=styles.color_dict[process])
    for i in range(2):
        plot.subplot(i + 1).add_hist(
            rootfile.get("mt", "qqh", "ggH"), "ggH"
        )  # signal histograms are used twice in order to realize a two color line style
        plot.subplot(i + 1).add_hist(
            rootfile.get("mt", "qqh", "ggH"), "ggH_top")
        plot.subplot(i + 1).add_hist(rootfile.get("mt", "qqh", "qqH"), "qqH")
        plot.subplot(i + 1).add_hist(
            rootfile.get("mt", "qqh", "qqH"), "qqH_top")
    plot.add_hist(rootfile.get("mt", "qqh", "data_obs"), "data_obs")
    plot.add_hist(rootfile.get("mt", "qqh", "TotalBkg"), "unc_band")

    # set some graph styles
    plot.subplot(1).setGraphStyle(
        "ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
    plot.subplot(1).setGraphStyle("ggH_top", "hist", linecolor=0)
    plot.subplot(1).setGraphStyle(
        "qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
    plot.subplot(1).setGraphStyle("qqH_top", "hist", linecolor=0)
    plot.setGraphStyle(
        "unc_band",
        "e2",
        markersize=0,
        fillcolor=styles.color_dict["unc"],
        linecolor=0)

    # in order to show S+B in the ratio plot, add total background to signal hists (get_hist returns a copy) and register the results
    bkg_ggH = plot.subplot(2).get_hist("ggH")
    bkg_qqH = plot.subplot(2).get_hist("qqH")
    bkg_ggH.Add(plot.subplot(2).get_hist("unc_band"))
    bkg_qqH.Add(plot.subplot(2).get_hist("unc_band"))
    plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH")
    plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH_top")
    plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH")
    plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH_top")
    plot.subplot(2).setGraphStyle(
        "bkg_ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
    plot.subplot(2).setGraphStyle("bkg_ggH_top", "hist", linecolor=0)
    plot.subplot(2).setGraphStyle(
        "bkg_qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
    plot.subplot(2).setGraphStyle("bkg_qqH_top", "hist", linecolor=0)

    # apply normalizations for the ratio and the background fractions plot:
    # First argument: Name of a single histogram or list of names / group names that shall be normalized
    # Second argument: Name of a single histogram or list of names / group names that shall be contained in the denominator
    plot.subplot(2).normalize([
        "unc_band", "bkg_ggH", "bkg_ggH_top", "bkg_qqH", "bkg_qqH_top",
        "data_obs"
    ], "unc_band")
    #plot.subplot(2).normalize(["unc_band", "bkg_ggH", "bkg_ggH_top", "bkg_qqH", "bkg_qqH_top", "data_obs"], "bkg") # would also work but add up the single bkg histograms in the background
    plot.subplot(3).normalize("bkg", "bkg")

    # stack background histograms for all subplots and assign a name
    plot.create_stack(bkg_processes, "stack")

    # set some axis options
    plot.subplot(0).setYlims(100, 2000)
    plot.subplot(1).setYlims(0.1, 100)
    plot.subplot(2).setYlims(0.81, 1.39)
    plot.subplot(3).setYlims(0.0, 1.0)
    plot.subplot(1).setLogY()
    plot.subplot(3).setXlabel("NN score")
    plot.subplot(0).setYlabel("N_{events}")
    plot.subplot(1).setYlabel(
        "")  # otherwise number labels are not drawn on axis
    plot.subplot(2).setYlabel("ratio to bkg")
    plot.subplot(3).setYlabel("bkg frac.")

    plot.scaleXTitleSize(0.8)
    plot.scaleXLabelSize(0.8)
    plot.scaleYTitleSize(0.8)
    plot.scaleYLabelSize(0.8)
    plot.scaleXLabelOffset(2.0)
    plot.scaleYTitleOffset(1.1)

    plot.subplot(2).setNYdivisions(3, 5)

    # draw subplots. Argument contains names of objects to be drawn in corresponding order.
    plot.subplot(0).Draw(["stack", "unc_band", "data_obs"])
    plot.subplot(1).Draw(
        ["stack", "unc_band", "ggH", "ggH_top", "qqH", "qqH_top", "data_obs"])
    plot.subplot(2).Draw([
        "unc_band", "bkg_ggH", "bkg_ggH_top", "bkg_qqH", "bkg_qqH_top",
        "data_obs"
    ])
    plot.subplot(3).Draw("stack")

    # create legends
    bkg_processes.reverse()
    suffix = ["", "_top"]
    for i in range(2):
        plot.add_legend(width=0.48, height=0.15)
        for process in bkg_processes:
            plot.legend(i).add_entry(0, process,
                                     styles.label_dict[process.replace(
                                         "EWK", "EWKZ")], 'f')
        plot.legend(i).add_entry(0, "unc_band", "Bkg. unc.", 'f')
        plot.legend(i).add_entry(1, "ggH%s" % suffix[i], "ggH", 'l')
        plot.legend(i).add_entry(1, "qqH%s" % suffix[i], "qqH", 'l')
        plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
        plot.legend(i).setNColumns(3)
    plot.legend(0).Draw()
    plot.legend(1).setAlpha(0.0)
    plot.legend(1).Draw()

    for i in range(2):
        plot.add_legend(reference_subplot=2, pos=1, width=0.4, height=0.03)
        plot.legend(i + 2).add_entry(0, "data_obs", "Data", 'PE')
        plot.legend(i + 2).add_entry(1, "ggH%s" % suffix[i], "ggH+bkg.", 'l')
        plot.legend(i + 2).add_entry(1, "qqH%s" % suffix[i], "qqH+bkg.", 'l')
        plot.legend(i + 2).setNColumns(3)
    plot.legend(2).Draw()
    plot.legend(3).setAlpha(0.0)
    plot.legend(3).Draw()

    # draw additional labels
    plot.DrawCMS()
    plot.DrawLumi("35.9 fb^{-1} (13 TeV)")
    plot.DrawChannelCategoryLabel("#mu#tau_{h}, VBF")

    # save plot
    plot.save("testoutput.pdf")


if __name__ == "__main__":
    setup_logging("plot_shapes.log", logging.INFO)
    main()
