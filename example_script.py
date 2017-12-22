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
    plot = dd.Plot([0.65, [0.47, 0.45], [0.22, 0.20]], "ModTDR", r=0.04, l=0.14)
    
    bkg_processes = ["ZTT", "ZL", "ZJ", "TTT", "TTJ", "W", "VV", "QCD", "EWK"]
    bkg_processes.reverse()
    for process in bkg_processes:
        plot.add_hist(rootfile.get("mt", "qqh", process), process, "bkg")
        plot.setGraphStyle(process, "hist", fillcolor=styles.color_dict[process])
    plot.subplot(3).normalize("bkg", "bkg")
    plot.create_stack(bkg_processes, "stack", "stacks")
    
    for i in range(2):
        plot.subplot(i+1).add_hist(rootfile.get("mt", "qqh", "ggH"), "ggH")
        plot.subplot(i+1).add_hist(rootfile.get("mt", "qqh", "ggH"), "ggH_top")
        plot.subplot(i+1).add_hist(rootfile.get("mt", "qqh", "qqH"), "qqH")
        plot.subplot(i+1).add_hist(rootfile.get("mt", "qqh", "qqH"), "qqH_top")
    plot.subplot(1).setGraphStyle("ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
    plot.subplot(1).setGraphStyle("ggH_top", "hist", linecolor=0)
    plot.subplot(1).setGraphStyle("qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
    plot.subplot(1).setGraphStyle("qqH_top", "hist", linecolor=0)
    
    plot.add_hist(rootfile.get("mt", "qqh", "data_obs"), "data_obs")
    plot.add_hist(rootfile.get("mt", "qqh", "TotalBkg"), "unc_band")
    plot.setGraphStyle("unc_band", "e2", markersize=0, fillcolor=styles.color_dict["unc"])
    
    bkg_ggH = plot.subplot(2).get_hist("ggH")
    bkg_qqH = plot.subplot(2).get_hist("qqH")
    bkg_ggH.Add(plot.subplot(2).get_hist("unc_band"))
    bkg_qqH.Add(plot.subplot(2).get_hist("unc_band"))
    plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH")
    plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH_top")
    plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH")
    plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH_top")
    plot.subplot(2).setGraphStyle("bkg_ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
    plot.subplot(2).setGraphStyle("bkg_ggH_top", "hist", linecolor=0)
    plot.subplot(2).setGraphStyle("bkg_qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
    plot.subplot(2).setGraphStyle("bkg_qqH_top", "hist", linecolor=0)
    
    plot.subplot(2).normalize(["unc_band", "bkg_ggH", "bkg_ggH_top", "bkg_qqH", "bkg_qqH_top", "data_obs"], "unc_band")
    #plot.subplot(2).normalize(["unc_band", "bkg_ggH", "bkg_ggH_top", "bkg_qqH", "bkg_qqH_top", "data_obs"], "bkg") # would also work but add up the single bkg histograms in the background
    
    plot.subplot(0).setYlims(100,2000)
    plot.subplot(1).setYlims(0.1, 100)
    plot.subplot(2).setYlims(0.81, 1.39)
    plot.subplot(3).setYlims(0.0, 1.0)
    plot.subplot(1).setLogY()
    plot.subplot(3).setXlabel("NN score")
    plot.subplot(0).setYlabel("N_{events}")
    plot.subplot(1).setYlabel("") # otherwise number labels are not drawn on axis
    plot.subplot(2).setYlabel("ratio to bkg")
    plot.subplot(3).setYlabel("bkg frac.")
    
    plot.scaleXTitleSize(0.8)
    plot.scaleXLabelSize(0.8)
    plot.scaleYTitleSize(0.8)
    plot.scaleYLabelSize(0.8)
    plot.scaleXLabelOffset(2.0)
    plot.scaleYTitleOffset(1.1)
    
    plot.subplot(2).setNYdivisions(3, 5)
    
    plot.subplot(0).Draw(["stack", "unc_band", "data_obs"])
    plot.subplot(1).Draw(["stack", "unc_band", "ggH", "ggH_top", "qqH", "qqH_top", "data_obs"])
    plot.subplot(2).Draw(["unc_band", "bkg_ggH", "bkg_ggH_top", "bkg_qqH", "bkg_qqH_top", "data_obs"])
    plot.subplot(3).Draw("stack")
    plot.DrawCMS()
    plot.DrawLumi("35.9 fb^{-1} (13 TeV)")
    plot.DrawChannelCategoryLabel("#mu#tau_{h}, VBF")
    plot.save("testoutput.pdf")
    

if __name__ == "__main__":
    setup_logging("plot_shapes.log", logging.INFO)
    main()
