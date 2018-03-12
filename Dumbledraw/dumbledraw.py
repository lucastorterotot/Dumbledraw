#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import copy
import ROOT as R
#import rootfile_parser
logger = logging.getLogger(__name__)

import styles


class Plot(object):
    def __init__(self, splitlist, style="none", **kwargs):
        styles.SetStyle(style, **kwargs)
        R.gROOT.SetBatch(True)  # don't disply canvas
        self._canvas = R.TCanvas()
        self._canvas.cd()
        self._subplots = []
        self._legends = []
        # evaluate splitlist and book
        if isinstance(splitlist, basestring):
            splitlist = [splitlist]
        lower = 1.0
        upper = 1.0
        for i, split in enumerate(splitlist):
            if not isinstance(split, float):
                lower = split[0]
                split = split[1]
            else:
                lower = split
            if not isinstance(lower, float):
                logger.fatal("Panel split is supposed to be of type float!")
                raise Exception
            self._subplots.append(Subplot(i, lower, upper))
            upper = split
            if not isinstance(upper, float):
                logger.fatal("Panel split is supposed to be of type float!")
                raise Exception
        lower = 0.0
        self._subplots.append(Subplot(len(splitlist), lower, upper))

    @property
    def nsubplots(self):
        return len(self._subplots)

    @property
    def nlegends(self):
        return len(self._legends)

    def subplot(self, index):
        if not isinstance(index, int):
            logger.fatal("Subplot index is supposed to be of type int!")
            raise Exception
        if index >= len(self._subplots):
            logger.fatal("Subplot index is out of range!")
            raise Exception
        return self._subplots[index]

    def legend(self, index):
        if not isinstance(index, int):
            logger.fatal("Legend index is supposed to be of type int!")
            raise Exception
        if index >= len(self._legends):
            logger.fatal("Legend index is out of range!")
            raise Exception
        return self._legends[index]

    def save(self, outputname):
        self._canvas.SaveAs(outputname)
        logger.info("Created %s" % outputname)

    def DrawChannelCategoryLabel(self, text):
        ypos = 0.960 if "_{" in text else 0.955
        latex2 = R.TLatex()
        latex2.SetNDC()
        latex2.SetTextAngle(0)
        latex2.SetTextColor(R.kBlack)
        latex2.SetTextSize(0.04)
        latex2.DrawLatex(0.145, 0.960, text)

    def DrawCMS(self):
        styles.DrawCMSLogo(self._subplots[0]._pad, 'CMS', 'Preliminary', 11,
                           0.045, 0.05, 1.0, '', 0.6)

    def DrawLumi(self, lumi):
        styles.DrawTitle(self._subplots[0]._pad, lumi, 3)

    def add_hist(self, hist, name, group_name="invisible"):
        for subplot in self._subplots:
            subplot.add_hist(hist=hist, name=name, group_name=group_name)

    def add_legend(self,
                   reference_subplot=0,
                   width=0.30,
                   height=0.20,
                   pos=3,
                   offset=0.03):
        self._legends.append(
            Legend(reference_subplot, width, height, pos, offset,
                   self._subplots))

    def setGraphStyle(self,
                      name,
                      markerstyle,
                      linecolor=1,
                      fillcolor=0,
                      linewidth=1,
                      markersize=1,
                      fillstyle=1001):
        for subplot in self._subplots:
            subplot.setGraphStyle(
                name=name,
                markerstyle=markerstyle,
                linecolor=linecolor,
                fillcolor=fillcolor,
                linewidth=linewidth,
                markersize=markersize,
                fillstyle=fillstyle)

    def create_stack(self, hist_names, name, group_name="invisible"):
        for subplot in self._subplots:
            subplot.create_stack(
                hist_names=hist_names, name=name, group_name=group_name)

    def scaleXLabelSize(self, val):
        for subplot in self._subplots:
            subplot.scaleXLabelSize(val)

    def scaleYLabelSize(self, val):
        for subplot in self._subplots:
            subplot.scaleYLabelSize(val)

    def scaleXTitleSize(self, val):
        for subplot in self._subplots:
            subplot.scaleXTitleSize(val)

    def scaleYTitleSize(self, val):
        for subplot in self._subplots:
            subplot.scaleYTitleSize(val)

    def setXlims(self, low, high):
        for subplot in self._subplots:
            subplot.setXlims(low, high)

    def setNXdivisions(self, nprimary, nsecondary):
        for subplot in self._subplots:
            subplot.setNXdivisions(nprimary, nsecondary)

    def scaleXTitleOffset(self, val):
        for subplot in self._subplots:
            subplot.scaleXTitleOffset(val)

    def scaleYTitleOffset(self, val):
        for subplot in self._subplots:
            subplot.scaleYTitleOffset(val)

    def scaleXLabelOffset(self, val):
        for subplot in self._subplots:
            subplot.scaleXLabelOffset(val)

    def scaleYLabelOffset(self, val):
        for subplot in self._subplots:
            subplot.scaleYLabelOffset(val)


class Subplot(object):
    def __init__(self, name, lower_bound=0.0, upper_bound=1.0):
        logger.debug(
            "Booking subplot with lower boundary at %f and upper boundary at %f"
            % (lower_bound, upper_bound))
        self._pad = R.TPad("pad_" + str(name), "pad_" + str(name), 0., 0., 1.,
                           1.)
        '''
        if lower_bound==0.0:
            lower_bound+=self._pad.GetBottomMargin()
        if upper_bound==1.0:
            upper_bound-=self._pad.GetTopMargin()
        '''
        drawspaceheight = 1.0 - self._pad.GetBottomMargin(
        ) - self._pad.GetTopMargin()
        lower_margin = self._pad.GetBottomMargin(
        ) + lower_bound * drawspaceheight
        upper_margin = self._pad.GetTopMargin() + (
            1 - upper_bound) * drawspaceheight
        self._pad.SetBottomMargin(lower_margin)
        self._pad.SetTopMargin(upper_margin)
        self._pad.SetFillStyle(4000)
        self._pad.Draw()

        self._hists = {}
        self._xlabel = None
        self._ylabel = None
        self._logx = False
        self._logy = False
        self._xlims = None
        self._ylims = None
        self._xlabelsize = None
        self._ylabelsize = None
        self._xtitlesize = None
        self._ytitlesize = None
        self._nxdivisions = None
        self._nydivisions = None
        self._xtitleoffsetscale = 1.0
        self._ytitleoffsetscale = 1.0
        self._xlabeloffsetscale = 1.0
        self._ylabeloffsetscale = 1.0
        self._height = 1 - upper_margin - lower_margin

    @property
    def hists(self):
        return self._hists

    # adds histogram to subplot and assign individual name and group name. Default group name = "invisible" which is ignored by DrawAll function.
    def add_hist(self, hist, name, group_name="invisible"):
        if name in self._hists.keys():
            logger.fatal("Histogram name %s already used!")
            raise Exception
        if not isinstance(hist, R.TH1F):
            logger.fatal(
                "add_hist expects a TH1F with name {}, got object {}".format(
                    name, hist))
            raise Exception
        self._hists[name] = [
            copy.deepcopy(hist), group_name, ""
        ]  # last entry is used to save the markerstyle and set in a different function

    # returns histogram with given name or sum of histograms with given group name
    def get_hist(self, name):
        if name in self._hists.keys():
            if isinstance(self._hists[name][0], R.THStack):
                logger.fatal("get_hist does not accept names of stacks!")
                raise Exception
            return self._hists[name][0]
        else:
            empty = True
            for entry in self._hists.values():
                if entry[1] == name:
                    if isinstance(entry[0], R.THStack):
                        logger.fatal(
                            "get_hist does not accept names of stacks!")
                        raise Exception
                    if empty:
                        hist = copy.deepcopy(entry[0])
                        hist.SetName(name)
                        empty = False
                    else:
                        hist.Add(entry[0])
            if empty:
                logger.fatal("No histograms matching to name %s" % name)
                raise Exception
            else:
                return hist

    # draws all histograms assigned to the subplot except those with group name "invisible"
    def DrawAll(self):
        isFirst = True
        for hist in self._hists.values():
            if not hist[1] == "invisible":
                self.DrawSingle(hist, isFirst)
                isFirst = False
        R.gPad.RedrawAxis()

    # draws specific histograms assigned to the subplot selected via a list of individual names and/or group names
    def Draw(self, names):
        if isinstance(names, basestring):
            names = [names]
        isFirst = True
        for name in names:
            if name in self._hists.keys():
                self.DrawSingle(self._hists[name], isFirst)
                isFirst = False
            else:
                for entry in self._hists.values():
                    if entry[1] == name:
                        self.DrawSingle(entry, isFirst)
                        isFirst = False
        R.gPad.RedrawAxis()

    # draws single ROOT histogram. If isFirst is True, formatting is applied and histogram overwrites existing drawings, else it is added
    def DrawSingle(self, hist, isFirst):
        self._pad.cd()
        if isFirst:
            hist[0].Draw()  # needed for stacks
            self.setAxisStyles(hist[0])
            hist[0].Draw(
                hist[2] + " ")  # looks stupid, but if it works it ain't stupid
        else:
            hist[0].Draw(hist[2] + "SAME")

    def setXlabel(self, label):
        self._xlabel = label

    def setYlabel(self, label):
        self._ylabel = label

    def setXlims(self, low, high):
        self._xlims = [low, high]

    def setYlims(self, low, high):
        self._ylims = [low, high]

    def setLogX(self):
        self._logx = True

    def setLogY(self):
        self._logy = True

    def scaleXLabelSize(self, val):
        self._xlabelsize = val

    def scaleYLabelSize(self, val):
        self._ylabelsize = val

    def scaleXTitleSize(self, val):
        self._xtitlesize = val

    def scaleYTitleSize(self, val):
        self._ytitlesize = val

    def setNXdivisions(self, nprimary, nsecondary):
        self._nxdivisions = [nprimary, nsecondary, 0, True]

    def setNYdivisions(self, nprimary, nsecondary):
        self._nydivisions = [nprimary, nsecondary, 0, True]

    def scaleXTitleOffset(self, val):
        self._xtitleoffsetscale = val

    def scaleYTitleOffset(self, val):
        self._ytitleoffsetscale = val

    def scaleXLabelOffset(self, val):
        self._xlabeloffsetscale = val

    def scaleYLabelOffset(self, val):
        self._ylabeloffsetscale = val

    # internal method to apply formatting to initial histograms
    def setAxisStyles(self, hist):
        # set axis labels
        if self._xlabel == None:
            hist.GetXaxis().SetTitleSize(0)
            hist.GetXaxis().SetLabelSize(0)
            #hist.GetXaxis().SetTickLength(0)
        else:
            hist.GetXaxis().SetTitle(self._xlabel)
            hist.GetXaxis().SetTitleOffset(
                self._xtitleoffsetscale * hist.GetXaxis().GetTitleOffset())
            hist.GetXaxis().SetLabelOffset(
                self._xlabeloffsetscale * hist.GetXaxis().GetLabelOffset())
        if self._ylabel == None:
            hist.GetYaxis().SetTitleSize(0)
            hist.GetYaxis().SetLabelSize(0)
            #hist.GetYaxis().SetTickLength(0)
        else:
            hist.GetYaxis().SetTitle(self._ylabel)
            hist.GetYaxis().SetTitleOffset(
                self._ytitleoffsetscale * hist.GetYaxis().GetTitleOffset())
            hist.GetYaxis().SetLabelOffset(
                self._ylabeloffsetscale * hist.GetYaxis().GetLabelOffset())

        # set label sizes
        if self._xlabelsize != None:
            hist.GetXaxis().SetLabelSize(
                self._xlabelsize * hist.GetXaxis().GetLabelSize())
        if self._ylabelsize != None:
            hist.GetYaxis().SetLabelSize(
                self._ylabelsize * hist.GetYaxis().GetLabelSize())
        if self._xtitlesize != None:
            hist.GetXaxis().SetTitleSize(
                self._xtitlesize * hist.GetXaxis().GetTitleSize())
        if self._ytitlesize != None:
            hist.GetYaxis().SetTitleSize(
                self._ytitlesize * hist.GetYaxis().GetTitleSize())

        # set log scale and fix customized range if necessary
        if self._logx:
            self._pad.SetLogx()
            if self._xlims != None and self._xlims[0] <= 0.0:
                self._xlims[0] = 0.00001
        if self._logy:
            self._pad.SetLogy()
            if self._ylims != None and self._ylims[0] <= 0.0:
                self._ylims[0] = 0.00001

        # set axis ranges
        if self._xlims != None:
            hist.GetXaxis().SetRangeUser(*self._xlims)
        if self._ylims != None:
            if isinstance(hist, R.THStack):
                hist.SetMinimum(self._ylims[0])
                hist.SetMaximum(self._ylims[1] / 1.05)
            else:
                hist.GetYaxis().SetRangeUser(*self._ylims)

        # set axis ticks#
        self._pad.SetTicks()  # ticks are drawn on all sides of the pad
        if self._nxdivisions != None:
            hist.GetXaxis().SetNdivisions(*self._nxdivisions)
        if self._nydivisions != None:
            hist.GetYaxis().SetNdivisions(*self._nydivisions)
        hist.GetYaxis().SetTickLength(0.02 / self._height)

    # sets style for specific histogram or group
    def setGraphStyle(self,
                      name,
                      markerstyle,
                      linecolor=1,
                      fillcolor=0,
                      linewidth=1,
                      markersize=1,
                      fillstyle=1001):
        markerstyledict = {}
        if markerstyle in markerstyledict.values():
            markerstyle = markerstyledict[markerstyle]
        if name in self._hists.keys():
            if isinstance(self._hists[name][0], R.THStack):
                logger.warning(
                    "Adressed object is stack. Style cannot be set!")
                return
            self._hists[name][2] = markerstyle
            self._hists[name][0].SetLineColor(linecolor)
            self._hists[name][0].SetFillColor(fillcolor)
            self._hists[name][0].SetLineWidth(linewidth)
            self._hists[name][0].SetMarkerSize(markersize)
            self._hists[name][0].SetFillStyle(fillstyle)
        else:
            for hist in self._hists.values():
                if hist[1] == name:
                    if isinstance(hist[0], R.THStack):
                        logger.warning(
                            "Adressed object is stack. Style cannot be set!")
                        return
                    hist[2] = markerstyle
                    hist[0].SetLineColor(linecolor)
                    hist[0].SetFillColor(fillcolor)
                    hist[0].SetLineWidth(linewidth)
                    hist[0].SetMarkerSize(markersize)
                    hist[0].SetFillStyle(fillstyle)

    # creates stack from registered histograms defined via name or group name
    def create_stack(self, hist_names, name, group_name="invisible"):
        if name in self._hists.keys():
            logger.fatal("Stack name %s already used!" % name)
            raise Exception
        stack = R.THStack("hs", "")
        # regularize inputs
        if isinstance(hist_names, basestring):
            hist_names = [hist_names]
        for hist_name in hist_names:
            if hist_name in self._hists.keys():
                stack.Add(self._hists[hist_name][0])
                logger.debug("Added histogram %s to stack %s" % (hist_name,
                                                                 name))
            else:
                for key, hist in self._hists.iteritems():
                    if hist_name == hist[1]:
                        if isinstance(hist[0], R.THStack):
                            logger.fatal(
                                "Tried to import a stack into a stack, which is impossible!"
                            )
                            raise Exception
                        stack.Add(hist[0])
                        logger.debug("Added histogram %s to stack %s" % (key,
                                                                         name))
        self._hists[name] = [stack, group_name, "hist"]

    # normalizes one or more histograms to a given denominator
    def normalize(self, nominator_names, denominator_names):
        # regularize inputs
        if isinstance(nominator_names, basestring):
            nominator_names = [nominator_names]
        if isinstance(denominator_names, basestring):
            denominator_names = [denominator_names]

        # sum up denominator
        isFirst = True
        for name in denominator_names:
            if isFirst:
                denominator = copy.deepcopy(self.get_hist(name))
                isFirst = False
            else:
                denominator.Add(self.get_hist(name))
        # do not propagate denominator errors
        for i in xrange(1, denominator.GetNbinsX() + 1):
            denominator.SetBinError(i, 0.)

        # normalize all nominator inputs
        for name in nominator_names:
            if name in self._hists.keys():
                if isinstance(self._hists[name][0], R.THStack):
                    logger.fatal("Stacks cannot be normalized!")
                    raise Exception
                self._hists[name][0].Divide(denominator)
            else:
                for hist in self._hists.values():
                    if hist[1] == name:
                        if isinstance(hist[0], R.THStack):
                            logger.fatal("Stacks cannot be normalized!")
                            raise Exception
                        hist[0].Divide(denominator)

    # normalizes bin contents of all histograms in the subplot to their bin width
    def normalizeByBinWidth(self):
        for hist in self._hists.values():
            if not isinstance(hist[0], R.THStack):
                denominator = copy.deepcopy(hist[0])
                for i in range(denominator.GetNbinsX()):
                    denominator.SetBinContent(i + 1,
                                              denominator.GetBinWidth(i + 1))
                    denominator.SetBinError(i + 1, 0.0)
                hist[0].Divide(denominator)


class Legend(object):
    def __init__(self, reference_subplot, width, height, pos, offset,
                 subplots):
        if not isinstance(reference_subplot, int):
            logger.fatal("Subplot index is supposed to be of type int!")
            raise Exception
        if reference_subplot >= len(subplots):
            logger.fatal("Subplot index is out of range!")
            raise Exception
        o = offset
        w = width
        h = height
        l = subplots[reference_subplot]._pad.GetLeftMargin()
        t = subplots[reference_subplot]._pad.GetTopMargin()
        b = subplots[reference_subplot]._pad.GetBottomMargin()
        r = subplots[reference_subplot]._pad.GetRightMargin()
        if pos == 1:
            self._legend = R.TLegend(l + o, 1 - t - o - h, l + o + w,
                                     1 - t - o, '', 'NBNDC')
        if pos == 2:
            c = l + 0.5 * (1 - l - r)
            self._legend = R.TLegend(c - 0.5 * w, 1 - t - o - h, c + 0.5 * w,
                                     1 - t - o, '', 'NBNDC')
        if pos == 3:
            self._legend = R.TLegend(1 - r - o - w, 1 - t - o - h, 1 - r - o,
                                     1 - t - o, '', 'NBNDC')
        if pos == 4:
            self._legend = R.TLegend(l + o, b + o, l + o + w, b + o + h, '',
                                     'NBNDC')
        if pos == 5:
            c = l + 0.5 * (1 - l - r)
            self._legend = R.TLegend(c - 0.5 * w, b + o, c + 0.5 * w,
                                     b + o + h, '', 'NBNDC')
        if pos == 6:
            self._legend = R.TLegend(1 - r - o - w, b + o, 1 - r - o,
                                     b + o + h, '', 'NBNDC')
        self._subplots = subplots
        self._textsizescale = 1.
        self._ncolumns = 1
        self._FillColor = 0
        self._alpha = 1.0

    def add_entry(self, subplot_index, histname, label, style):
        if not isinstance(subplot_index, int):
            logger.fatal("Subplot index is supposed to be of type int!")
            raise Exception
        if subplot_index >= len(self._subplots):
            logger.fatal("Subplot index is out of range!")
            raise Exception
        if not histname in self._subplots[subplot_index]._hists.keys():
            logger.fatal("Requested histogram for legend does not exist!")
            raise Exception
        self._legend.AddEntry(
            self._subplots[subplot_index]._hists[histname][0], label, style)

    def scaleTextSize(self, scale):
        self._textsizescale = scale

    def setNColumns(self, number):
        self._legend.SetNColumns(number)

    def setFillColor(self, val):
        self._FillColor = val

    def setAlpha(self, val):
        self._alpha = val

    def Draw(self):
        self._legend.SetTextFont(42)
        self._legend.SetTextSize(0.025 * self._textsizescale)
        self._legend.SetFillColorAlpha(self._FillColor, self._alpha)
        self._legend.SetColumnSeparation(0)
        self._legend.Draw("same")
