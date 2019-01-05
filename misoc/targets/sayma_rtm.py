#!/usr/bin/env python3

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer
from migen.build.platforms.sinara import sayma_rtm

from misoc.integration.soc_core import *
from misoc.integration.builder import *


class CRG(Module):
    def __init__(self,  platform):
        self.clock_domains.cd_sys = ClockDomain()
        pll_fb = Signal()
        pll_locked = Signal()
        pll_clk625 = Signal()
        self.specials += [
            Instance("PLLE2_BASE",
                p_CLKIN1_PERIOD=20.0,
                i_CLKIN1=platform.request("clk50"),

                i_CLKFBIN=pll_fb,
                o_CLKFBOUT=pll_fb,
                o_LOCKED=pll_locked,

                # VCO @ 1GHz
                p_CLKFBOUT_MULT=20, p_DIVCLK_DIVIDE=1,
                p_CLKOUT0_DIVIDE=16, p_CLKOUT0_PHASE=0.0, o_CLKOUT0=pll_clk625,
            ),
            Instance("BUFG", i_I=pll_clk625, o_O=self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_sys, ~pll_locked)
        ]


class BaseSoC(SoCCore):
    def __init__(self, platform, **kwargs):
        SoCCore.__init__(self, platform,
            clk_freq=62.5e6,
            integrated_rom_size=32*1024,
            integrated_main_ram_size=16*1024,
            **kwargs)
        self.submodules.crg = CRG(platform)


def main():
    parser = argparse.ArgumentParser(description="MiSoC port to the Sayma RTM")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    platform = sayma_rtm.Platform()
    soc = BaseSoC(platform, **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()