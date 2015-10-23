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
    """
    :type datapath: Datapath
    :type ports: list[]
    """

    def __init__(self, datapath):
        self.datapath = datapath
        self.ports = []

    def add_port(self, port):
        self.ports.append(port)
