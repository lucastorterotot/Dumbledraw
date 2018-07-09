#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import ROOT
import copy
logger = logging.getLogger(__name__)


class Rootfile_parser(object):
    def __init__(self, inputrootfilename, analysis, epoch, variable, mass):
        self._rootfilename = inputrootfilename
        self._rootfile = ROOT.TFile(self._rootfilename, "READ")
        self._type = "control"
        self._analysis = analysis
        self._epoch = epoch
        self._variable = variable
        self._mass = mass

    @property
    def rootfile(self):
        return self._rootfile

    def get(self, channel, category, process):
        hist_hash = "#{channel}#{category}#{process}#{analysis}#{epoch}#{variable}#{mass}#".format(
            channel=channel,
            category=category,
            process=process,
            analysis=self._analysis,
            epoch=self._epoch,
            variable=self._variable,
            mass=self._mass)
        logger.debug("Try to access %s in %s" % (hist_hash,
                                                 self._rootfilename))
        print "rootfile: " , self._rootfile.Get(hist_hash), " hash: ", hist_hash

        return self._rootfile.Get(hist_hash)

    def list_contents(self):
        return [key.GetTitle() for key in self._rootfile.GetListOfKeys()]

    def get_bins(self, channel, category):
        hist = self.get(channel, category)
        nbins = hist.GetNbinsX()
        bins = []
        for i in range(nbins):
            bins.append(hist.GetBinLowEdge(i + 1))
        bins.append(hist.GetBinLowEdge(i + 1) + hist.GetBinWidth(i + 1))
        return bins

    def get_values(self, channel, category):
        hist = self.get(channel, category)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinContent(i + 1))
        return values

    def __del__(self):
        logger.debug("Closing rootfile %s" % (self._rootfilename))
        self._rootfile.Close()
