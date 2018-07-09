#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser_inputshapes as rootfile_parser
import Dumbledraw.styles as styles
import ROOT as R

import argparse
from copy import deepcopy

from root_numpy import hist2array
import numpy as np
import matplotlib.pyplot as plt
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

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for 2016 Standard Model analysis.")
    parser.add_argument(
        "--channels",
        default=[],
        nargs='+',
        type=str,
        help="Channels to be considered.")
    parser.add_argument(
        "--categories",
        default=[],
        nargs='+',
        type=str,
        help="Categories to be considered.")
    parser.add_argument(
        "--variables",
        default=[],
        nargs='+',
        type=str,
        help="Variables to be considered.")
    return parser.parse_args()

xlabels = { "pt": r'Reconstructed p_{T}^{H} (GeV)', "eta":r'Reconstructed #eta',"phi": r' Reconstructed #phi',"m":r'Reconstructed mass m_{H} (GeV)'}

def main(args):
	hack = []
	roc = {}
	shapes = {}
	for channel in args.channels:
		roc[channel] = {}
		shapes[channel] = {}
		for category in args.categories:
			roc[channel][category] = {}
			shapes[channel][category] = {}
	for variable in args.variables:
		for channel in args.channels:
			for category in args.categories:
				rootfile = rootfile_parser.Rootfile_parser("shapes.root", "smhtt", "Run2016", variable, 125)
				#print rootfile.list_contents()
				name = "_".join([channel, category])
				out_name = "_".join([channel, category, variable])
				print name	
	
				# create canvas:
				#   First argument defines subplot structure: List of splits from top to bottom (max. 1.0 to min. 0.0). A split can be a single position or a pair resulting in gap.
				#   Further arguments set general style.
				plot = dd.Plot(
					[0.05], "ModTDR", r=0.04, l=0.14)
	
				#bkg_processes = ["EWK", "QCD", "VV", "W", "TTT", "TTJ", "ZJ", "ZL", "ZTT"]
				bkg_processes = ["EWK", "QCD", "VV", "W", "TTT", "TTJ", "ZL", "ZJ", "ZTT"]
				if channel == 'tt':
					bkg_processes = ["QCD", "VV", "W", "TTT", "TTJ", "ZL", "ZJ", "ZTT"]
	
				# register histograms in the subplots (can be done globally or for specific subplots). regustered histograms are not necessarily plotted later.
				for process in bkg_processes:
					plot.add_hist(
						rootfile.get(channel, name, process), process, "bkg"
					)  # get(channel, category, process) and assign specific name and group name to histogram. The group name is optional.
					plot.setGraphStyle(
						process, "hist", fillcolor=styles.color_dict[process])

				for i in range(1):
					plot.add_hist(
						rootfile.get(channel, name, "ggH"), "ggH"
						)  # signal histograms are used twice in order to realize a two color line style
					plot.add_hist(
						rootfile.get(channel, name, "ggH"), "ggH_top")
					plot.add_hist(rootfile.get(channel, name, "qqH"), "qqH")
					plot.add_hist(
						rootfile.get(channel, name, "qqH"), "qqH_top")
#				plot.add_hist(rootfile.get(channel, name, "data_obs"), "data_obs", "data_obs")
				# set some graph styles
				plot.setGraphStyle(
					"ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
				plot.setGraphStyle("ggH_top", "hist", linecolor=0)
				plot.setGraphStyle(
					"qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)

				plot.setGraphStyle("qqH_top", "hist", linecolor=0)
#				plot.setGraphStyle(
#					"data_obs",
#					"e0",
#					markersize=1,
#					fillcolor=styles.color_dict["unc"],
#					linecolor=1)
				plot.create_stack(bkg_processes, "stack")
#				plot.subplot(1).normalize(["data_obs"], bkg_processes) # would also work but add up the single bkg histograms in the background
				if channel == 'tt':
					plot.subplot(0).setYlims(1, 1e5)
					plot.DrawChannelCategoryLabel("#tau_{h}#tau_{h}")
				elif channel == 'mt':
					plot.subplot(0).setYlims(1, 1e7)
					plot.DrawChannelCategoryLabel("#mu#tau_{h}")
				elif channel == 'et':
					plot.subplot(0).setYlims(0.1, 1e7)
					plot.DrawChannelCategoryLabel("e#tau_{h}")

	#			plot.subplot(0).setXlims(-200, 200)
	#			plot.subplot(1).setXlims(-200, )
				plot.subplot(1).setYlims(0, 2)
				plot.subplot(0).setLogY()
				plot.subplot(0).setXlabel(xlabels[variable.split("_")[0]])
				plot.subplot(0).setYlabel("N_{events}")
				plot.subplot(1).setYlabel("ratio to bkg")
	
				plot.scaleXTitleSize(0.8)
				plot.scaleXLabelSize(0.8)
				plot.scaleYTitleSize(0.8)
				plot.scaleYLabelSize(0.8)
				plot.scaleXLabelOffset(2.0)
				plot.scaleYTitleOffset(1.1)
				plot.subplot(0).Draw(['stack', #"data_obs", 
										"ggH", "qqH", "ggH_top", "qqH_top", ])
	#			plot.subplot(1).add_hist(R.TF1("line", "1", 0, 1000), "line")
#				plot.subplot(1).Draw(["data_obs", "line"])
	
				# create legends
				bkg_processes.reverse()
				suffix = ["", "_top"]
				for i in range(2):
					plot.add_legend(width=0.5, height=0.08)
					for process in bkg_processes:
						plot.legend(i).add_entry(0, process,
												 styles.label_dict[process], 'f')
					plot.legend(i).add_entry(1, "ggH%s" % suffix[i], "ggH", 'l')
					plot.legend(i).add_entry(1, "qqH%s" % suffix[i], "qqH", 'l')
#					plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
					plot.legend(i).setNColumns(3)
				plot.legend(0).Draw()
				plot.subplot(1)._pad.SetGrid()
	
				# draw additional labels
				plot.DrawCMS()
				#plot.DrawLumi("35.9 fb^{-1} (13 TeV)")
	
				# save plot
				plot.save(out_name + ".png")
				plot.save(out_name + ".pdf")
				hack.append(plot)
				# ROC-Curves
				ztt = hist2array(plot.subplot(1)._hists["ZTT"][0])
				ggH = hist2array(plot.subplot(1)._hists["ggH"][0])
				qqH = hist2array(plot.subplot(1)._hists["qqH"][0])
				ztt_all = np.sum(ztt)
				ggH_all = np.sum(ggH)
				qqH_all = np.sum(qqH)
				bkg_rej = []
				ggH_eff = []
				qqH_eff = []
				ztt_sum = 0#ztt_all
				ggH_sum = 0#ggH_all
				qqH_sum = 0#qqH_all
				for i in range(ztt.shape[0]-1, 0, -1):
					ztt_sum = ztt_sum+ ztt[i]
					ggH_sum = ggH_sum+ ggH[i]
					qqH_sum = qqH_sum+ qqH[i]
					bkg_rej.append( (ztt_all - ztt_sum) / ztt_all)
					ggH_eff.append( ggH_sum / ggH_all)
					qqH_eff.append( qqH_sum / qqH_all)
				roc[channel][category][variable] = [bkg_rej, ggH_eff, qqH_eff]
				shapes[channel][category][variable] =  [hist2array(plot.subplot(1)._hists["ZTT"][0], return_edges=True),
														hist2array(plot.subplot(1)._hists["ggH"][0], return_edges=True),
														hist2array(plot.subplot(1)._hists["qqH"][0], return_edges=True)]
				

	for channel in args.channels:
		for category in args.categories:
			fig = plt.figure(figsize=(3,3))
			ax = fig.add_subplot(111)
		
			names = {'m_N' : 'N.mass', 'm_sv': 'SVFit'}
			colors = ['red','blue']
			for i, v in enumerate(["m_N", "m_sv"]):
			#for v in ["pt_nn", "pt_sv"]:
				plt.plot(roc[channel][category][v][1], roc[channel][category][v][0], '--s', label = names[v]+ ", ggH", color = colors[i], markersize=3)
				plt.plot(roc[channel][category][v][2], roc[channel][category][v][0], '-o', label = names[v] + ", VBF", color=colors[i], markersize=3)
			ax.set_xlabel("Higgs Efficiency")
			ax.set_ylabel("$Z\\rightarrow \\tau \\tau$ rejection")
			#ax.set_title("Tau mass (" + channel + ")")
			plt.legend(ncol=1)
			plt.tight_layout()
			plt.savefig("ROC"+channel+"_"+category+".png")
			plt.savefig("ROC"+channel+"_"+category+".pdf")
			plt.close()

	for channel in args.channels:
		for category in args.categories:
			fig = plt.figure(figsize=(3,3))
			ax = fig.add_subplot(111)
		
			names = {'m_N' : 'N.mass', 'm_sv': 'SVFit'}
			colors = ['red','blue']
			for i, v in enumerate(["m_N", "m_sv"]):
			#for v in ["pt_nn", "pt_sv"]:
				print shapes[channel][category][v][0][0]
				print shapes[channel][category][v][0][1][0]
				plt.plot(x=np.array(shapes[channel][category][v][0][0]), y=shapes[channel][category][v][0][1][0], label = names[v]+ ", DY")
#				plt.hist(shapes[channel][category][v][1], label = names[v]+ ", ggH",   normed = True)
#				plt.hist(shapes[channel][category][v][2], label = names[v]+ ", qqH",   normed = True)
			ax.set_xlabel("Mass")
			ax.set_ylabel("rel. number of Events")
			#ax.set_title("Tau mass (" + channel + ")")
			plt.legend(ncol=1)
			plt.tight_layout()
			plt.savefig("shape_"+channel+"_"+category+".png")
			plt.savefig("shape_"+channel+"_"+category+".pdf")
			plt.close()



if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("plot_shapes.log", logging.INFO)
    main(args)
