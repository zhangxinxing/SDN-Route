# In The Name Of God
# ========================================
# [] File Name : sw.py
#
# [] Creation Date : 10/24/15
#
# [] Created By : Parham Alvani (parham.alvani@gmail.com)
# =======================================
__author__ = 'Parham Alvani'

from ryu.controller.controller import Datapath


class Switch:
    def __init__(self, datapath):
        self.datapath = datapath  # type: Datapath

    def add_lldp_flow(self, port):
        ofp = self.datapath.ofproto
        parser = self.datapath.ofproto_parser

        # install LLDP flow entry
        match = parser.OFPMatch(eth_type=0x88CC)
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        msg = parser.OFPFlowMod(self.datapath, command=ofp.OFPFC_ADD, match=match, instructions=inst)
        self.datapath.send_msg(msg)
