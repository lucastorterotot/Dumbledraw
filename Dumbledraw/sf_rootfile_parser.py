#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import ROOT
import copy
logger = logging.getLogger(__name__)


class ScaleFactor_Rootfile_parser(object):
    def __init__(self, inputrootfilename):
        self._rootfilename = inputrootfilename
        self._rootfile = ROOT.TFile(self._rootfilename, "READ")
        content = [entry.GetName() for entry in self._rootfile.GetListOfKeys()]
        self.Nbins = len(content)
        logger.debug("Identified {} histograms in rootfile {} ".format(len(content), inputrootfilename))
        self._hist_hash = "{variable}_projx_{etabin}"

    @property
    def rootfile(self):
        return self._rootfile



    def get(self, variable, etabin):
        hist_hash = self._hist_hash.format(
            variable=variable,
            etabin=etabin)
        logger.debug(
            "Try to access %s in %s" % (hist_hash, self._rootfilename))
        return self._rootfile.Get(hist_hash)


    def get_bins(self, variable, etabin):
        hist = self.get(self, variable, etabin)
        nbins = hist.GetNbinsX()
        bins = []
        for i in range(nbins):
            bins.append(hist.GetBinLowEdge(i + 1))
        bins.append(hist.GetBinLowEdge(i + 1) + hist.GetBinWidth(i + 1))
        return bins

    def get_values(self, variable, etabin):
        hist = self.get(self, variable, etabin)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinContent(i + 1))
        return values

    def get_values_up(self, variable, etabin):
        hist = self.get(self, variable, etabin)
        nbins=hist.GetNbinsX()
        values=[]
        for i in range(nbins):
            values.append(hist.GetBinErrDown(i + 1))
        return values

    def get_values_down(self, variable, etabin):
        hist = self.get(self, variable, etabin)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinErrDown(i + 1))
        return values

    def __del__(self):
        logger.debug("Closing rootfile %s" % (self._rootfilename))
        self._rootfile.Close()
