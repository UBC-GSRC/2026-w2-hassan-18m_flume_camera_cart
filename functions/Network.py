# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 13:26:29 2024

@author: Katrin Tanner
"""

class Controller:
    def __init__(self, IP:str):
        self.ip= IP
        
class Axis(Controller):
    def __init__(self, IP, Number, AxleName):
        super().__init__(AxleName)
        self.Number = Number
        self.AxleName = AxleName
        self.PPU = None