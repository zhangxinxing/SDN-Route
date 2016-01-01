# In The Name Of God
# ========================================
# [] File Name : dijkstra.py
#
# [] Creation Date : 30-05-2015
#
# [] Created By : Parham Alvani (parham.alvani@gmail.com)
# =======================================

__author__ = 'Parham Alvani'

from ryu.lib import packet
from ryu import utils
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.dpset import EventDP
import array


class Dijkstra(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Dijkstra, self).__init__(*args, **kwargs)
        self.switchs = []

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto

        if msg.reason == ofp.OFPPR_ADD:
            reason = 'ADD'
        elif msg.reason == ofp.OFPPR_DELETE:
            reason = 'DELETE'
        elif msg.reason == ofp.OFPPR_MODIFY:
            reason = 'MODIFY'
        else:
            reason = 'unknown'

        self.logger.debug('### OFPPortStatus received: reason=%s desc=%s',
                          reason, msg.desc)

    @set_ev_cls(EventDP, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        switch = ev.dp
        self.switchs.append(switch)

        parser = switch.ofproto_parser

        # install LLDP flow entry
        ofproto = switch.ofproto
        match = parser.OFPMatch(eth_type=0x88CC)
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        msg = parser.OFPFlowMod(switch, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        switch.send_msg(msg)

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        # The Output action forwards a packet to a specific OpenFlow port.
        # CONTROLLER is a OpenFlow reserved port that represents the controller
        # channel with the OpenFlow controller.

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto

        if msg.reason == ofp.OFPR_NO_MATCH:
            reason = 'NO MATCH'
        elif msg.reason == ofp.OFPR_ACTION:
            reason = 'ACTION'
        elif msg.reason == ofp.OFPR_INVALID_TTL:
            reason = 'INVALID TTL'
        else:
            reason = 'unknown'

        self.logger.debug('OFPPacketIn received: '
                          'buffer_id=%x total_len=%d reason=%s '
                          'table_id=%d cookie=%d match=%s data=%s',
                          msg.buffer_id, msg.total_len, reason,
                          msg.table_id, msg.cookie, msg.match,
                          utils.hex_array(msg.data))

    @staticmethod
    def add_flow(datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Each flow entry contains a set of instructions that are executed when packet
        # matches the entry. These instructions result in changes to the packet,
        # action set and/or pipeline processing.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)
