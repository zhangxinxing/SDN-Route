# In The Name Of God
# ========================================
# [] File Name : dijkstra.py
#
# [] Creation Date : 30-05-2015
#
# [] Created By : Parham Alvani (parham.alvani@gmail.com)
# =======================================

__author__ = 'Parham Alvani'

from ryu import utils
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller import dpset
from typing import Dict

from sdnr import sw


class Dijkstra(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'dpset': dpset.DPSet}

    def __init__(self, *args, **kwargs):
        super(Dijkstra, self).__init__(*args, **kwargs)
        self.dpset = kwargs['dpset']  # type: dpset.DPSet
        self.switches = {}  # type: Dict[int, sw.Switch]

    @set_ev_cls(dpset.EventDP, MAIN_DISPATCHER)
    def switch_handler(self, ev):
        if ev.enter:
            switch = sw.Switch(self.dpset.get(ev.dp.id))
            self.switches.setdefault(switch.datapath.id, switch)

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
