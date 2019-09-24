#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import ROOT
import copy
logger = logging.getLogger(__name__)


class Rootfile_parser(object):
    def __init__(self, inputrootfilename, mode="CombineHarvester"):
        self._rootfilename = inputrootfilename
        self._rootfile = ROOT.TFile(self._rootfilename, "READ")
        self._type = "control"
        content = [entry.GetName() for entry in self._rootfile.GetListOfKeys()]
        for entry in content:
            if entry.endswith("prefit"):
                self._type = "prefit"
        for entry in content:
            if entry.endswith("postfit"):
                self._type = "postfit"
        logger.debug("Identified rootfile %s as %s shapes" %
                     (inputrootfilename, self._type))
        if mode == "standard":
            self._hist_hash = "{channel}_{category}{plottype}/{process}{unc}"
        elif mode == "CombineHarvester":
            self._hist_hash = "htt_{channel}_{category}_{era}{plottype}/{process}{unc}"
        else:
            logger.fatal("Cannot detect mode to open file {}.".format(mode))
            raise Exception
        logger.debug("Use mode {} to read file.".format(mode))

    @property
    def rootfile(self):
        return self._rootfile

    def get(self, era, channel, category, process, syst=None):
        if syst != None and self._type != "control":
            logger.fatal(
                "Uncertainty shapes are only available in control plots!")
            raise Exception
        hist_hash = self._hist_hash.format(
            era=era,
            channel=channel,
            category=category,
            process=process,
            plottype="{plottype}",
            unc="{unc}")
        if self._type == "control":
            syst = "" if syst == None else "_" + syst
            hist_hash = hist_hash.format(plottype="", unc=syst)
        else:
            hist_hash = hist_hash.format(plottype="_" + self._type, unc="")
        logger.debug(
            "Try to access %s in %s" % (hist_hash, self._rootfilename))
        # perform check if file is available and otherwise return some dummy TH1F
        available_processes = [entry.GetName() for entry in self._rootfile.Get(hist_hash.split('/')[0]).GetListOfKeys()]
        if hist_hash.split('/')[1] in available_processes:
            return self._rootfile.Get(hist_hash)
        elif len(available_processes) != 0:
            hist_nbins = self._rootfile.Get('{}/{}'.format(hist_hash.split('/')[0],available_processes[0])).GetNbinsX()
            hist_range = [self._rootfile.Get('{}/{}'.format(hist_hash.split('/')[0],available_processes[0])).GetBinLowEdge(1), 
                self._rootfile.Get('{}/{}'.format(hist_hash.split('/')[0],available_processes[0])).GetBinLowEdge(hist_nbins+1)]
            logger.warning("%s in %s does not exist !" % (hist_hash, self._rootfilename))
            logger.debug(" Available Histograms are: %s" % available_processes)
            logger.debug(" Returning a dummy histogram for %s with %s bins in %s " % (process, hist_nbins, hist_range))
            return ROOT.TH1F(hist_hash,process,hist_nbins,hist_range[0],hist_range[1])
        else:
            logger.fatal(" None of the requested Histograms are available in %s. Aborting." % hist_hash.split('/')[0])
            raise Exception


    def get_bins(self, era, channel, category, process, syst=None):
        hist = self.get(era, channel, category, process, syst)
        nbins = hist.GetNbinsX()
        bins = []
        for i in range(nbins):
            bins.append(hist.GetBinLowEdge(i + 1))
        bins.append(hist.GetBinLowEdge(i + 1) + hist.GetBinWidth(i + 1))
        return bins

    def get_values(self, era, channel, category, process, syst=None):
        hist = self.get(era, channel, category, process, syst)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinContent(i + 1))
        return values

    def get_values_up(self, era, channel, category, process, syst=None):
        hist = self.get(era, channel, category, process, syst)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinErrDown(i + 1))
        return values

    def get_values_down(self, era, channel, category, process, syst=None):
        hist = self.get(era, channel, category, process, syst)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinErrDown(i + 1))
        return values

    def __del__(self):
        logger.debug("Closing rootfile %s" % (self._rootfilename))
        self._rootfile.Close()
