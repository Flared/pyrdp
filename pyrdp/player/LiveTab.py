#
# This file is part of the PyRDP project.
# Copyright (C) 2018 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

import asyncio

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QHBoxLayout, QWidget

from pyrdp.core import Directory
from pyrdp.player.AttackerBar import AttackerBar
from pyrdp.player.BaseTab import BaseTab
from pyrdp.player.LiveEventHandler import LiveEventHandler
from pyrdp.player.PlayerLayerSet import AsyncIOPlayerLayerSet
from pyrdp.player.RDPMITMWidget import RDPMITMWidget
from pyrdp.ui import FileSystemWidget


class LiveTab(BaseTab):
    """
    Tab playing a live RDP connection as data is being received over the network.
    """

    connectionClosed = Signal(object)

    def __init__(self, parent: QWidget = None):
        layers = AsyncIOPlayerLayerSet()
        rdpWidget = RDPMITMWidget(1024, 768, layers.player)

        super().__init__(rdpWidget, parent)
        self.layers = layers
        self.rdpWidget = rdpWidget
        self.fileSystem = Directory("")
        self.eventHandler = LiveEventHandler(self.widget, self.text, self.fileSystem)
        self.attackerBar = AttackerBar()

        self.attackerBar.controlTaken.connect(lambda: self.rdpWidget.setControlState(True))
        self.attackerBar.controlReleased.connect(lambda: self.rdpWidget.setControlState(False))

        self.fileSystemWidget = FileSystemWidget(self.fileSystem)
        self.fileSystemWidget.setWindowTitle("Client drives")

        self.attackerLayout = QHBoxLayout()
        self.attackerLayout.addWidget(self.fileSystemWidget, 20)
        self.attackerLayout.addWidget(self.text, 80)

        self.tabLayout.insertWidget(0, self.attackerBar)
        self.tabLayout.removeWidget(self.text)
        self.tabLayout.addLayout(self.attackerLayout)

        self.layers.player.addObserver(self.eventHandler)

    def getProtocol(self) -> asyncio.Protocol:
        return self.layers.tcp

    def onDisconnection(self):
        self.connectionClosed.emit()

    def onClose(self):
        self.layers.tcp.disconnect(True)

    def sendKeySequence(self, keys: [Qt.Key]):
        self.rdpWidget.sendKeySequence(keys)

    def sendText(self, text: str):
        self.rdpWidget.sendText(text)