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
            self._hist_hash = "htt_{channel}_{category}_13TeV{plottype}/{process}{unc}"
        else:
            logger.fatal("Cannot detect mode to open file {}.".format(mode))
            raise Exception
        logger.debug("Use mode {} to read file.".format(mode))

    @property
    def rootfile(self):
        return self._rootfile

    def get(self, channel, category, process, syst=None):
        if syst != None and self._type != "control":
            logger.fatal(
                "Uncertainty shapes are only available in control plots!")
            raise Exception
        hist_hash = self._hist_hash.format(
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
        return self._rootfile.Get(hist_hash)

    def get_bins(self, channel, category, process, syst=None):
        hist = self.get(channel, category, process, syst)
        nbins = hist.GetNbinsX()
        bins = []
        for i in range(nbins):
            bins.append(hist.GetBinLowEdge(i + 1))
        bins.append(hist.GetBinLowEdge(i + 1) + hist.GetBinWidth(i + 1))
        return bins

    def get_values(self, channel, category, process, syst=None):
        hist = self.get(channel, category, process, syst)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinContent(i + 1))
        return values

    def get_values_up(self, channel, category, process, syst=None):
        hist = self.get(channel, category, process, syst)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinErrDown(i + 1))
        return values

    def get_values_down(self, channel, category, process, syst=None):
        hist = self.get(channel, category, process, syst)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinErrDown(i + 1))
        return values

    def __del__(self):
        logger.debug("Closing rootfile %s" % (self._rootfilename))
        self._rootfile.Close()
