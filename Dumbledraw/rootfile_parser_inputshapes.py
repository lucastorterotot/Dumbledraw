#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import ROOT
import copy
logger = logging.getLogger(__name__)

mass_dict = {
    "heavy_mass": [320],
    "light_mass_fine": [60,100],
    "light_mass_coarse": [60],
}

class Rootfile_parser(object):

    _dataset_map = {
        "data": "data",
        "ZTT": "DY",
        "ZL": "DY",
        "ZJ": "DY",
        "TTT": "TT",
        "TTL": "TT",
        "TTJ": "TT",
        "VVT": "VV",
        "VVL": "VV",
        "VVJ": "VV",
        "W": "W",
        "EMB": "EMB",
        "QCDEMB": "QCD",
        "QCD": "QCDMC",
        "jetFakesEMB": "jetFakes",
        "jetFakes": "jetFakesMC",
        "ggH125": "ggH",
        "qqH125": "qqH",
        "HTT" : "HTT"
    }

    _process_map = {
        "data": "data",
        "ZTT": "DY-ZTT",
        "ZL": "DY-ZL",
        "ZJ": "DY-ZJ",
        "TTT": "TT-TTT",
        "TTL": "TT-TTL",
        "TTJ": "TT-TTJ",
        "VVT": "VV-VVT",
        "VVL": "VV-VVL",
        "VVJ": "VV-VVJ",
        "W": "W",
        "EMB": "Embedded",
        "QCDEMB": "QCD",
        "QCD": "QCDMC",
        "jetFakesEMB": "jetFakes",
        "jetFakes": "jetFakesMC",
        "ggH125": "ggH125",
        "qqH125": "qqH125",
        "HTT" : "HTT"
    }

    for heavy_mass in mass_dict["heavy_mass"]:
        light_masses = mass_dict["light_mass_coarse"] if heavy_mass > 1001 else mass_dict["light_mass_fine"]
        for light_mass in light_masses:
            if light_mass+125<heavy_mass:
                _dataset_map["NMSSM_{heavy_mass}_125_{light_mass}".format(heavy_mass=heavy_mass,light_mass=light_mass)] = "NMSSM_{heavy_mass}_125_{light_mass}".format(heavy_mass=heavy_mass,light_mass=light_mass)
                _process_map["NMSSM_{heavy_mass}_125_{light_mass}".format(heavy_mass=heavy_mass,light_mass=light_mass)] = "NMSSM"

    

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
