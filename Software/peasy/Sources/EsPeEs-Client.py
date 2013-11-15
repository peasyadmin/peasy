#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 EsPeEs <espees.plc@googlemail.com>
# EsPeEs is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# EsPeEs is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import base64
import EsPeEs
import getopt
import os
import psutil
import signal
import subprocess
import socket
import sys
import time
import wx
import wx.html
import wx.grid
from wx import xrc
from wx import stc

class UserInterface(object):
    def __init__(self, client, serverInformation):
        if client == None:
            self.__Client = None
        else:
            self.__Client = client
        if serverInformation == None:
            self.__ServerInformation = None
        else:
            self.__ServerInformation = serverInformation
            
    def hasClient(self):
        if self.__Client == None:
            return False
        else:
            return True
            
    def hasServerInformation(self):
        if self.__ServerInformation == None:
            return False
        else:
            return True
            
    def getClient(self):
        return self.__Client
        
    def getServerInformation(self):
        return self.__ServerInformation
        
    def setClient(self, client):
        self.__Client = client
        
    def setServerInformation(self, serverInformation):
        self.__ServerInformation = serverInformation
        
    def isConnected(self):
        if self.hasClient() == False:
            return False
        else:
            return self.__Client.isConnected()
            
    def closingAllowed(self):
        return True
                   
    def __refresh__(self):
        pass

class GUI(UserInterface):
    TrayIcon = None
    
    @staticmethod
    def run():
        app = wx.App()
        get_resources()
        TrayIcon = GUI()
        app.MainLoop()     
        
    @staticmethod
    def quit(evt):
        if not (TrayIcon == None):
            TrayIcon.OnQuit(None)
            
    def __init__(self):
        self.__TaskBarIcon = wx.TaskBarIcon()
        self.__Icon = wx.EmptyIcon()
        self.__Icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.__TaskBarIcon.SetIcon(self.__Icon, 'EsPeEs')
        self.__TaskBarIcon.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.OnLeftDown)
        self.__TaskBarIconBlocked = False
        self.__ProjectsMode = False
        self.__DriversMode = False
        self.__EsPeEsServerProcess = None
        self.__EsPeEsCoderProcess = None
        self.__EsPeEsCoderProcess_StopEvent = None
        self.__ConnectionDialog = None
        self.__ProjectsFrame = None
        self.__DriverFrame = None
        self.__RunProjectDialog = None
        UserInterface.__init__(self, None, None)
        
    def CreatePopupMenu(self):
        action = -1
        menu = wx.Menu()
        noAction = True
        if self.isConnected() == True:
            pir = self.getClient().plcIsRunning()
            if pir == 1:
                self.getClient().stopPLC()
                action = 1
                noAction = False
            if pir == 0:
                action = 1
                noAction = False
            if (pir == 2):
                action = 3
                noAction = False
            if EsPeEs.ProcessManagement.Instance().espeesCoderRunning() == True:
                action = 2
                noAction = False
        else:
            action = 0
            noAction = False
        if self.getDriversMode() == True:
            action = 4
            
        if action == 0:
            connectionItem = self.__createMenuItem__(menu, 'Connection', self.OnConnection)
            menu.AppendSeparator()
            projectsItem = self.__createMenuItem__(menu, 'Projects', self.OnProjects)
            projectsItem.Enable(False)
            runProjectItem = self.__createMenuItem__(menu, 'Run project', self.OnRunProject)
            runProjectItem.Enable(False)
            driverItem = self.__createMenuItem__(menu, 'Drivers', self.OnDriver)
            menu.AppendSeparator()
            #localPLCItem = self.__createMenuItem__(menu, 'Local PLC', self.OnLocalPLC)
            aboutItem = self.__createMenuItem__(menu, 'About', self.OnAbout)
            menu.AppendSeparator()
            quitItem = self.__createMenuItem__(menu, 'Quit', self.OnQuit)
            
        if action == 1:
            connectionItem = self.__createMenuItem__(menu, 'Connection', self.OnConnection)
            menu.AppendSeparator()
            projectsItem = self.__createMenuItem__(menu, 'Projects', self.OnProjects)
            runProjectItem = self.__createMenuItem__(menu, 'Run project', self.OnRunProject)
            if len(self.getServerInformation().getRunableProjects()) > 0:
                runProjectItem.Enable(True)
            else:
                runProjectItem.Enable(False)
            driverItem = self.__createMenuItem__(menu, 'Drivers', self.OnDriver)
            menu.AppendSeparator()
            aboutItem = self.__createMenuItem__(menu, 'About', self.OnAbout)
            menu.AppendSeparator()
            quitItem = self.__createMenuItem__(menu, 'Quit', self.OnQuit)
            
        if action == 2:
            connectionItem = self.__createMenuItem__(menu, 'Close EsPeEs-Coder', self.OnCloseEsPeEsCoder)
            menu.AppendSeparator()
            quitItem = self.__createMenuItem__(menu, 'Quit', self.OnQuit)
            
        if action == 3:
            connectionItem = self.__createMenuItem__(menu, 'Connection', self.OnConnection)
            menu.AppendSeparator()
            projectsItem = self.__createMenuItem__(menu, 'Projects', self.OnProjects)
            projectsItem.Enable(False)
            runProjectItem = self.__createMenuItem__(menu, 'Run project', self.OnRunProject)
            driverItem = self.__createMenuItem__(menu, 'Drivers', self.OnDriver)
            menu.AppendSeparator()
            aboutItem = self.__createMenuItem__(menu, 'About', self.OnAbout)
            menu.AppendSeparator()
            quitItem = self.__createMenuItem__(menu, 'Quit', self.OnQuit)
            
        if action == 4:
            connectionItem = self.__createMenuItem__(menu, 'Close EsPeEs-Driver', self.OnCloseEsPeEsDriver)
            menu.AppendSeparator()
            quitItem = self.__createMenuItem__(menu, 'Quit', self.OnQuit)
            
        if noAction == True:
            menu = None
            
        return menu

    def OnLeftDown(self, event):
        if (self.getProjectsMode() == True) and (EsPeEs.ProcessManagement.Instance().espeesCoderRunning() == False):
            return 
        menu = self.CreatePopupMenu()
        if not (menu == None):
            self.__TaskBarIcon.PopupMenu(menu)

    def OnConnection(self, event):
        self.__ConnectionDialog = ConnectionDialog(None, self.getClient(), self.getServerInformation(), self)
        self.__ConnectionDialog.ShowModal()
        if self.__ConnectionDialog.isConnected() == True:
            self.setClient(self.__ConnectionDialog.getClient())
            self.setServerInformation(self.__ConnectionDialog.getServerInformation())
        self.__ConnectionDialog.Destroy()
        self.__ConnectionDialog = None
        
    def OnProjects(self, event):
        self.setProjectsMode()
        self.__ProjectsFrame = ProjectsFrame(None, self.getClient(), self.getServerInformation(), self)
        self.__ProjectsFrame.Centre()
        self.__ProjectsFrame.Show()
        
    def OnRunProject(self, event):
        self.__RunProjectDialog = RunProjectDialog(None, self.getClient(), self.getServerInformation(), self)
        self.__RunProjectDialog.ShowModal()
        self.__RunProjectDialog.Destroy()
        self.__RunProjectDialog = None
        
    def OnDriver(self, event):
        self.__DriverFrame = DriverFrame(None, self)
        self.__DriverFrame.Centre()
        self.__DriverFrame.Show()
        
    def OnAbout(self, event):
        aboutDialog = AboutDialog(None)
        aboutDialog.ShowModal()
        aboutDialog.Destroy()

    def OnQuit(self, event):
        if self.isConnected() == True:
            if (self.getClient().plcIsRunning() == 1):
                self.getClient().stopPLC()
            self.getClient().disconnect()    
        if EsPeEs.ProcessManagement.Instance().espeesCoderRunning() == True:
            EsPeEs.ProcessManagement.Instance().stopEsPeEsCoder()
        self.__TaskBarIcon.RemoveIcon()
        wx.CallAfter(self.__TaskBarIcon.Destroy)
        sys.exit()
        
    def OnCloseEsPeEsCoder(self, event):
        EsPeEs.ProcessManagement.Instance().stopEsPeEsCoder()
        
    def OnCloseEsPeEsDriver(self, event):
        self.__DriverFrame.OnClose(None)
        
    def TransmissionBroked(self, event):
        #print 'Broked: ' + event
        #if not (self.__ProjectsFrame == None):
        #    self.__ProjectsFrame.Destroy()
        #    self.__ProjectsFrame = None
        if not (self.__RunProjectDialog == None):
            self.__RunProjectDialog.Destroy()
            self.__RunProjectDialog = None
        
    def __createMenuItem__(self, menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item
        
    def setProjectsMode(self):
        self.__ProjectsMode = True
        
    def getProjectsMode(self):
        return self.__ProjectsMode
        
    def resetProjectsMode(self):
        self.__ProjectsMode = False
        
    def setDriversMode(self):
        self.__DriversMode = True
        
    def getDriversMode(self):
        return self.__DriversMode
        
    def resetDriversMode(self):
        self.__DriversMode = False
        
class ConnectionDialog(wx.Dialog, UserInterface):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, client, serverInformation, trayIcon):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "ConnectionDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        UserInterface.__init__(self, client, serverInformation)
        
        self.__Panel = ConnectionPanel(self, client, serverInformation, trayIcon)
        self.SetSize((420, 320))

    def OnClose(self, evt):
        if self.__Panel.closingAllowed() == True:
            self.EndModal(0)
        
    def getClient(self):
        return self.__Panel.getClient()
        
    def getServerInformation(self):
        return self.__Panel.getServerInformation()
        
    def isConnected(self):
        return self.__Panel.isConnected()
        
class ProjectsFrame(wx.Frame, UserInterface):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, client, serverInformation, trayIcon):
        pre = wx.PreFrame()
        self.PreCreate(pre)
        get_resources().LoadOnFrame(pre, parent, "ProjectsFrame")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        UserInterface.__init__(self, client, serverInformation)
        
        self.__TrayIcon = trayIcon
        self.__Panel = ProjectsPanel(self, client, serverInformation, trayIcon)
        
        self.SetSize((500, 400))

    def OnClose(self, evt):
        if self.__Panel.closingAllowed() == True:
            self.__TrayIcon.setServerInformation(self.getServerInformation())
            if self.isConnected() == True:
                self.getClient().stopPLC()
            self.__TrayIcon.resetProjectsMode()
            self.Destroy()
            
    def getClient(self):
        return self.__Panel.getClient()
        
    def getServerInformation(self):
        return self.__Panel.getServerInformation()
        
    def isConnected(self):
        return self.__Panel.isConnected()

class RunProjectDialog(wx.Dialog, UserInterface):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, client, serverInformation, trayIcon):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "RunProjectDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        UserInterface.__init__(self, client, serverInformation)
       
        self.__Panel = RunProjectPanel(self, client, serverInformation, trayIcon)
        
        self.SetSize((300, 120))

    def OnClose(self, evt):
        self.EndModal(0)

class DeviceDialog(wx.Dialog, UserInterface):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, client, serverInformation, device, project):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DeviceDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        UserInterface.__init__(self, client, serverInformation)

        self.__Panel = DevicePanel(self, client, serverInformation, device, project)
        
        self.SetSize((350, 330))
        
    def OnClose(self, evt):
        self.EndModal(0)
        
    def showModbus(self, add = False, edit = False):
        self.__Panel.showModbus(add = add,  edit = edit)
        self.ShowModal()
        
    def showSPI(self, add = False, edit = False):
        self.__Panel.showSPI(add = add,  edit = edit)
        self.ShowModal()
        
    def showI2C(self, add = False, edit = False):
        self.__Panel.showI2C(add = add,  edit = edit)
        self.ShowModal()

class AboutDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "AboutDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.__Panel = AboutPanel(self)
        self.__Panel.Show()
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        self.Fit()
        
    def OnClose(self, evt):
        self.EndModal(0)

class ConnectionPanel(wx.Panel, UserInterface):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, client, serverInformation, trayIcon):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "ConnectionPanel")
        self.PostCreate(pre)

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.ComboBox = xrc.XRCCTRL(self, "ComboBox")
        self.Connect_Button = xrc.XRCCTRL(self, "Connect_Button")
        self.Disconnect_Button = xrc.XRCCTRL(self, "Disconnect_Button")
        self.Error_Label = xrc.XRCCTRL(self, "Error_Label")
        self.StaticLine = xrc.XRCCTRL(self, "StaticLine")
        self.Gauge = xrc.XRCCTRL(self, "Gauge")
        self.BrowserPanel = xrc.XRCCTRL(self, "BrowserPanel")
        self.BrowserSizer = wx.BoxSizer(wx.VERTICAL)
        self.Browser = wx.html.HtmlWindow(self.BrowserPanel, style = wx.SUNKEN_BORDER)
        self.BrowserSizer.Add(self.Browser, 1, wx.EXPAND)
        self.BrowserPanel.SetSizer(self.BrowserSizer)
        
        self.Bind(wx.EVT_COMBOBOX, self.OnCombobox_ComboBox, self.ComboBox)
        self.Bind(wx.EVT_TEXT, self.OnCombobox_Text, self.ComboBox)
        self.Bind(wx.EVT_BUTTON, self.OnButton_Connect_Button, self.Connect_Button)
        self.Bind(wx.EVT_BUTTON, self.OnButton_Disconnect_Button, self.Disconnect_Button)
        
        UserInterface.__init__(self, client, serverInformation)
        self.__LoadingTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.__refreshLoadingGauge__, self.__LoadingTimer)
        
        self.__Processing = False
        self.__TrayIcon = trayIcon
        self.__selectLastUsedPLCs__()
        if not (serverInformation == None):
            self.Browser.SetPage(serverInformation.getInfoText())
            
        self.__refresh__()

    def OnCombobox_ComboBox(self, evt):
        self.__check__()
        self.Layout()
        
    def OnCombobox_Text(self, evt):
        self.__check__()
        self.Layout()

    def OnButton_Connect_Button(self, evt):
        #self.__connect__()
        EsPeEs.executeFunctionAsyncron(self.__connect__, self.__connectFailed__, self.__connectSuccess__, useWx = True)
        self.__showLoadingGauge__()

    def OnButton_Disconnect_Button(self, evt):
        EsPeEs.executeFunctionAsyncron(self.__disconnect__, self.__disconnectFailed__, self.__disconnectSuccess__, useWx = True)
        self.__showLoadingGauge__()
        
    def __selectLastUsedPLCs__(self):
        plcs = EsPeEs.Preferences.loadUsedPLCs()
        plcs.sort()
        plc = EsPeEs.Preferences.loadLastUsedPLC()
        plc_index = 0
        self.ComboBox.Clear()
        for i in range(len(plcs)):
            self.ComboBox.Append(plcs[i])
            if plcs[i] == plc:
                plc_index = i
        if len(plcs) > 0:
            self.ComboBox.SetSelection(plc_index)
        else:
            self.ComboBox.Append('127.0.0.1')
            self.ComboBox.SetSelection(0)
        
    def __showLoadingGauge__(self):
        self.__Processing = True
        self.__refresh__()
        self.__LoadingTimer.Start(30)
        
    def __hideLoadingGauge__(self):
        self.__Processing = False
        self.__LoadingTimer.Stop()
        self.__refresh__()
        
    def __refreshLoadingGauge__(self, evt):
        self.Gauge.Pulse()
        
    def __connect__(self):
        if self.ComboBox.GetValue().find(':') == -1:
            self.setClient(EsPeEs.Client(self.ComboBox.GetValue(), EsPeEs.Preferences.DefaultPort, self.__TrayIcon.TransmissionBroked, useWx = True))
        else:
            args = self.ComboBox.GetValue().split(':')
            ip = args[0]
            port = EsPeEs.Preferences.DefaultPort
            try:
                print type(args[1])
                port = str(args[1])
            except ValueError, e:
                print e
                return None
            self.setClient(EsPeEs.Client(ip, port))
        if self.getClient().connect() == True:
            plc = self.ComboBox.GetValue()
            plc_exist = False
            plcs = EsPeEs.Preferences.loadUsedPLCs()
            for i in range(len(plcs)):
                if plcs[i] == plc:
                    plc_exist = True
                    break;
            if not (plc_exist == True):
                plcs.append(self.ComboBox.GetValue())
                EsPeEs.Preferences.saveUsedPLCs(plcs)
            EsPeEs.Preferences.saveLastUsedPLC(self.ComboBox.GetValue())
            try:
                serverInformation = self.getClient().getServerInformation()
                if serverInformation == None:
                    return None
                return serverInformation.clone()
            except TypeError, e:
                return None
        else:
            return None
        
    def __connectSuccess__(self, evt):
        if evt == None:
            print 'None evt'
        else:
            pass
        self.setServerInformation(evt)
        self.Browser.SetPage(self.getServerInformation().getInfoText())
        self.__hideLoadingGauge__()
        if self.getServerInformation().getTarget().startswith('Linux') and (sys.platform == 'win32'):
            dialog = wx.MessageDialog(self, 'I\'m sorry, no Linux target support, because of missing compiler.\n\nI didn\'t figured out, how to build a gcc with kernel-headers in cygwin.\nIf you have a clue or a working toolchain for Linux,\nmail me: "espees.plc@gmail.com".' ,  caption = 'No Linux compiler in Windows', style=wx.OK|wx.ICON_INFORMATION)
            dialog.ShowModal()
            dialog.Destroy()
        
    def __connectFailed__(self, evt):
        self.__hideLoadingGauge__()
        
    def __disconnect__(self):
        if self.hasClient() == True:
            self.getClient().disconnect()
            self.setClient(None)
            return True
        return None
            
    def __disconnectSuccess__(self, evt):
        self.__hideLoadingGauge__()
        
    def __disconnectFailed__(self, evt):
        self.__hideLoadingGauge__()
        
    def __check__(self):
        ok = True

        if EsPeEs.legalTCPAdress(self.ComboBox.GetValue()) == False:
            self.Error_Label.SetLabel('Illegal adress.')
            ok = False
            port = EsPeEs.extractPort(self.ComboBox.GetValue())
            if not (port == None):
                if EsPeEs.legalPort(port) == False:
                    self.Error_Label.SetLabel('Allowed port range: 49152 - 65535.')
                    ok = False
                
        if ok == True:
            self.Error_Label.Hide()
            self.Connect_Button.Enable()
        else:
            self.Error_Label.Show()
            self.Connect_Button.Disable()
        return ok
    
    def __refresh__(self):
        action = -1
        if self.__Processing == True:
            action = 0
        else:
            if self.isConnected() == True:
                action = 1
            else:
                action = 2
                
        if action == 0:
            self.ComboBox.Disable()
            self.Connect_Button.Disable()
            self.Disconnect_Button.Disable()
            self.StaticLine.Show()
            self.Gauge.Show()
            
        if action == 1:
            self.ComboBox.Disable()
            self.Disconnect_Button.Enable()
            self.Connect_Button.Hide()
            self.Disconnect_Button.Show()
            self.StaticLine.Hide()
            self.Gauge.Hide()
            
        if action == 2:
            self.ComboBox.Enable()
            self.Connect_Button.Enable()
            self.Connect_Button.Show()
            self.Disconnect_Button.Hide()
            self.Browser.SetPage('Not connected.')
            self.StaticLine.Hide()
            self.Gauge.Hide()
            self.__check__()
                
        self.Layout()
        
    def closingAllowed(self):
        if self.__Processing == True:
            return False
        else:
            return True

class ProjectsPanel(wx.Panel, UserInterface):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, client, serverInformation, trayIcon):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "ProjectsPanel")
        self.PostCreate(pre)

        self.titleLabel = xrc.XRCCTRL(self, "titleLabel")
        self.Projects_ListBox = xrc.XRCCTRL(self, "Projects_ListBox")
        self.Projects_Add_Button = xrc.XRCCTRL(self, "Projects_Add_Button")
        self.Projects_Remove_Button = xrc.XRCCTRL(self, "Projects_Remove_Button")
        self.Projects_Edit_Button = xrc.XRCCTRL(self, "Projects_Edit_Button")
        self.Projects_Beremiz_Button = xrc.XRCCTRL(self, "Project_Beremiz_Button")
        self.ProjectInformation_Name_Label = xrc.XRCCTRL(self, "ProjectInformation_Name_Label")
        self.ProjectInformation_Name_TextCtrl = xrc.XRCCTRL(self, "ProjectInformation_Name_TextCtrl")
        self.ProjectInformation_Company_Label = xrc.XRCCTRL(self, "ProjectInformation_Company_Label")
        self.ProjectInformation_Company_TextCtrl = xrc.XRCCTRL(self, "ProjectInformation_Company_TextCtrl")
        self.ProjectInformation_Product_Label = xrc.XRCCTRL(self, "ProjectInformation_Product_Label")
        self.ProjectInformation_Product_TextCtrl = xrc.XRCCTRL(self, "ProjectInformation_Product_TextCtrl")
        self.ProjectInformation_Version_Label = xrc.XRCCTRL(self, "ProjectInformation_Version_Label")
        self.ProjectInformation_Version_TextCtrl = xrc.XRCCTRL(self, "ProjectInformation_Version_TextCtrl")
        self.ProjectInformation_Error_Label = xrc.XRCCTRL(self, "ProjectInformation_Error_Label")
        self.SelectShield_TreeCtrl = xrc.XRCCTRL(self, "SelectShield_TreeCtrl")
        self.SelectTarget_TreeCtrl = xrc.XRCCTRL(self, "SelectTarget_TreeCtrl")
        self.AddDevices_AvailableDevices_Label = xrc.XRCCTRL(self, "AddDevices_AvailableDevices_Label")
        self.AddDevices_TreeCtrl = xrc.XRCCTRL(self, "AddDevices_TreeCtrl")
        self.AddDevices_Add_Button = xrc.XRCCTRL(self, "AddDevices_Add_Button")
        self.AddDevices_Remove_Button = xrc.XRCCTRL(self, "AddDevices_Remove_Button")
        self.AddDevices_Preferences_Button = xrc.XRCCTRL(self, "AddDevices_Preferences_Button")
        self.AddDevices_Devices_Label = xrc.XRCCTRL(self, "AddDevices_Devices_Label")
        self.AddDevices_Devices_ListBox = xrc.XRCCTRL(self, "AddDevices_Devices_ListBox")
        self.ProjectTree_TreeCtrl = xrc.XRCCTRL(self, "ProjectTree_TreeCtrl")
        self.backwardButton = xrc.XRCCTRL(self, "backwardButton")
        self.forwardButton = xrc.XRCCTRL(self, "forwardButton")
        self.finishButton = xrc.XRCCTRL(self, "finishButton")
        self.StaticLine = xrc.XRCCTRL(self, "StaticLine")
        self.Gauge = xrc.XRCCTRL(self, "Gauge")

        self.Bind(wx.EVT_LISTBOX, self.OnListbox_Projects_ListBox, self.Projects_ListBox)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListbox_dclick_Projects_ListBox, self.Projects_ListBox)
        self.Bind(wx.EVT_BUTTON, self.OnButton_Projects_Add_Button, self.Projects_Add_Button)
        self.Bind(wx.EVT_BUTTON, self.OnButton_Projects_Remove_Button, self.Projects_Remove_Button)
        self.Bind(wx.EVT_BUTTON, self.OnButton_Projects_Edit_Button, self.Projects_Edit_Button)
        self.Bind(wx.EVT_BUTTON, self.OnButton_Project_Beremiz_Button, self.Projects_Beremiz_Button)
        self.Bind(wx.EVT_TEXT, self.OnText_ProjectInformation_Name_TextCtrl, self.ProjectInformation_Name_TextCtrl)
        self.Bind(wx.EVT_TEXT, self.OnText_ProjectInformation_Company_TextCtrl, self.ProjectInformation_Company_TextCtrl)
        self.Bind(wx.EVT_TEXT, self.OnText_ProjectInformation_Product_TextCtrl, self.ProjectInformation_Product_TextCtrl)
        self.Bind(wx.EVT_TEXT, self.OnText_ProjectInformation_Version_TextCtrl, self.ProjectInformation_Version_TextCtrl)
        self.Bind(wx.EVT_BUTTON, self.OnButton_AddDevices_Add_Button, self.AddDevices_Add_Button)
        self.Bind(wx.EVT_BUTTON, self.OnButton_AddDevices_Remove_Button, self.AddDevices_Remove_Button)
        self.Bind(wx.EVT_BUTTON, self.OnButton_AddDevices_Preferences_Button, self.AddDevices_Preferences_Button)
        self.Bind(wx.EVT_LISTBOX, self.OnListbox_AddDevices_Devices_ListBox, self.AddDevices_Devices_ListBox)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListbox_dclick_AddDevices_Devices_ListBox, self.AddDevices_Devices_ListBox)
        self.Bind(wx.EVT_BUTTON, self.OnButton_backwardButton, self.backwardButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_forwardButton, self.forwardButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_finishButton, self.finishButton)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTree_sel_changed_SelectShield_TreeCtrl, self.SelectShield_TreeCtrl)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTree_sel_changed_SelectTarget_TreeCtrl, self.SelectTarget_TreeCtrl)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTree_sel_changed_AddDevices_TreeCtrl, self.AddDevices_TreeCtrl)
        
        self.__ImageList = wx.ImageList(24,24)
        self.__ProjectImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'project_24.png', type=wx.BITMAP_TYPE_PNG))
        self.__ModuleImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'module_24.png', type=wx.BITMAP_TYPE_PNG))
        self.__DirectoryImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'folder_24.png', type=wx.BITMAP_TYPE_PNG))
        self.__DriverImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'driver_24.png', type=wx.BITMAP_TYPE_PNG))
        self.__CFileImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'cfile_24.png', type=wx.BITMAP_TYPE_PNG))
        self.SelectShield_TreeCtrl.SetImageList(self.__ImageList)
        self.SelectTarget_TreeCtrl.SetImageList(self.__ImageList)
        self.AddDevices_TreeCtrl.SetImageList(self.__ImageList)
        self.ProjectTree_TreeCtrl.SetImageList(self.__ImageList)
        
        UserInterface.__init__(self, client, serverInformation)
        self.__TrayIcon = trayIcon
        self.__LoadingTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.__refreshLoadingGauge__, self.__LoadingTimer)
        self.__Processing = False
        self.__Shield = None
        self.__Page = 0
        self.__ShieldPath = range(0,0)
        self.__TargetPath = range(0, 0)
        self.__Target = None
        self.__hideAllPages__()
        self.__refresh__()

    def OnListbox_Projects_ListBox(self, evt):
        if not (self.Projects_ListBox.GetSelection() == -1):
            self.Projects_Remove_Button.Enable()
            self.Projects_Beremiz_Button.Enable()
        else:
            self.Projects_Remove_Button.Disable()
            self.Projects_Beremiz_Button.Disable() 

    def OnListbox_dclick_Projects_ListBox(self, evt):
        self.OnButton_Project_Beremiz_Button(evt)

    def OnButton_Projects_Add_Button(self, evt):
        drivers = EsPeEs.DriverManager.Instance().listAvailablePLCs(self.getServerInformation().getTarget())
        if len(drivers) > 0:
            self.nextPage()
        else:
            dialog = wx.MessageDialog(self, 'Ooops, you\'re missing PLC drivers\n for the target platform.',  caption = 'No available PLC driver.', style=wx.OK|wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()

    def OnButton_Projects_Remove_Button(self, evt):
        if not (self.Projects_ListBox.GetSelection() == -1):
            EsPeEs.executeFunctionAsyncron(self.__removeProject__, self.__removeProjectFailed__, self.__removeProjectSuccess__, useWx = True)
            self.__showLoadingGauge__()

    def OnButton_Projects_Edit_Button(self, evt):
        pass

    def OnButton_Project_Beremiz_Button(self, evt):
        if not (self.Projects_ListBox.GetSelection() == -1):
            EsPeEs.executeFunctionAsyncron(self.__programProject__, self.__programProjectFailed__, self.__programProjectSuccess__, useWx = True)
            self.__showLoadingGauge__()

    def OnText_ProjectInformation_Name_TextCtrl(self, evt):
        ok = True
        if self.getServerInformation().existProject(self.ProjectInformation_Name_TextCtrl.GetValue()) == True:
            ok = False
            self.ProjectInformation_Error_Label.SetLabel('Name already been taken.')
            
        if EsPeEs.legalName(self.ProjectInformation_Name_TextCtrl.GetValue()) == False:
            ok = False
            self.ProjectInformation_Error_Label.SetLabel('Illegal name.')
            
        if ok == False:
            self.ProjectInformation_Error_Label.Show()
            self.forwardButton.Disable()
        else:
            self.ProjectInformation_Error_Label.Hide()
            self.forwardButton.Enable()
            
        self.Layout()

    def OnText_ProjectInformation_Company_TextCtrl(self, evt):
        pass

    def OnText_ProjectInformation_Product_TextCtrl(self, evt):
        pass

    def OnText_ProjectInformation_Version_TextCtrl(self, evt):
        pass

    def OnListbox_dclick_SelectShield_ListBox(self, evt):
         if not (self.SelectShield_ListBox.GetSelection() == -1):
            self.nextPage()

    def OnListbox_AddDevices_Available_ListBox(self, evt):
        if self.AddDevices_Available_ListBox.GetSelection() == -1:
            self.AddDevices_Add_Button.Disable()
        else:
            self.AddDevices_Add_Button.Enable()

    def OnListbox_dclick_AddDevices_Available_ListBox(self, evt):
        if not (self.AddDevices_Available_ListBox.GetSelection() == -1):
            self.OnButton_AddDevices_Add_Button(evt)

    def OnButton_AddDevices_Add_Button(self, evt):
        if self.__Page == 4:
            #if len(self.getServerInformation().getSerialPorts()) > 0:
            dialog = DeviceDialog(self.GetParent(), self.getClient(), self.getServerInformation(), EsPeEs.DriverManager.Instance().getDriver(self.__getPath__(self.AddDevices_TreeCtrl), self.__getCExtensionType__()), self.__Project)
            dialog.showModbus(add = True)
            if dialog.GetReturnCode() == 1:
                self.__showAddModbusDevices__()
                self.AddDevices_Add_Button.Disable()
            dialog.Destroy()
            #else:
            #    wx.MessageBox('No serial-port available.', 'Info', wx.OK | wx.ICON_INFORMATION)
                
        if self.__Page == 5:
            dialog = DeviceDialog(self.GetParent(), self.getClient(), self.getServerInformation(), EsPeEs.DriverManager.Instance().getDriver(self.__getPath__(self.AddDevices_TreeCtrl), self.__getCExtensionType__()), self.__Project)
            dialog.showSPI(add = True)
            if dialog.GetReturnCode() == 1:
                self.__showAddSPIDevices__()
                self.AddDevices_Add_Button.Disable()
            dialog.Destroy()
                
        if self.__Page == 6:
            dialog = DeviceDialog(self.GetParent(), self.getClient(), self.getServerInformation(), EsPeEs.DriverManager.Instance().getDriver(self.__getPath__(self.AddDevices_TreeCtrl), self.__getCExtensionType__()), self.__Project)
            dialog.showI2C(add = True)
            if dialog.GetReturnCode() == 1:
                self.__showAddI2CDevices__()
                self.AddDevices_Add_Button.Disable()
            dialog.Destroy()

    def OnButton_AddDevices_Remove_Button(self, evt):
        if self.__Page == 4:
            if not (self.AddDevices_Devices_ListBox.GetSelection() == -1):
                self.__Project.removeModbusDevice(self.__Project.getModbusDevices()[self.AddDevices_Devices_ListBox.GetSelection()].getName())
                self.__showAddModbusDevices__()
                
        if self.__Page == 5:
            if not (self.AddDevices_Devices_ListBox.GetSelection() == -1):
                self.__Project.removeSPIDevice(self.__Project.getSPIDevices()[self.AddDevices_Devices_ListBox.GetSelection()].getName())
                self.__showAddSPIDevices__()
                
        if self.__Page == 6:
            if not (self.AddDevices_Devices_ListBox.GetSelection() == -1):
                self.__Project.removeI2CDevice(self.__Project.getI2CDevices()[self.AddDevices_Devices_ListBox.GetSelection()].getName())
                self.__showAddI2CDevices__()

    def OnButton_AddDevices_Preferences_Button(self, evt):
        if self.__Page == 4:
            if not (self.AddDevices_Devices_ListBox.GetSelection() == -1):
                device = self.__Project.getModbusDevice(name = self.AddDevices_Devices_ListBox.GetString(self.AddDevices_Devices_ListBox.GetSelection()))
                dialog = DeviceDialog(self.GetParent(), self.getClient(), self.getServerInformation(), device, self.__Project)
                dialog.showModbus(edit = True)
                if dialog.GetReturnCode() == 1:
                    self.__showAddModbusDevices__()
                dialog.Destroy()
                
        if self.__Page == 5:
            if not (self.AddDevices_Devices_ListBox.GetSelection() == -1):
                device = self.__Project.getSPIDevice(name = self.AddDevices_Devices_ListBox.GetString(self.AddDevices_Devices_ListBox.GetSelection()))
                dialog = DeviceDialog(self.GetParent(), self.getClient(), self.getServerInformation(), device, self.__Project)
                dialog.showSPI(edit = True)
                if dialog.GetReturnCode() == 1:
                    self.__showAddSPIDevices__()
                dialog.Destroy()
                
        if self.__Page == 6:
            if not (self.AddDevices_Devices_ListBox.GetSelection() == -1):
                device = self.__Project.getI2CDevice(name = self.AddDevices_Devices_ListBox.GetString(self.AddDevices_Devices_ListBox.GetSelection()))
                dialog = DeviceDialog(self.GetParent(), self.getClient(), self.getServerInformation(), device, self.__Project)
                dialog.showI2C(edit = True)
                if dialog.GetReturnCode() == 1:
                    self.__showAddI2CDevices__()
                dialog.Destroy()

    def OnListbox_AddDevices_Devices_ListBox(self, evt):
        if self.AddDevices_Devices_ListBox.GetSelection() == -1:
            self.AddDevices_Remove_Button.Disable()
            self.AddDevices_Preferences_Button.Disable()
        else:
            self.AddDevices_Remove_Button.Enable()
            self.AddDevices_Preferences_Button.Enable()

    def OnListbox_dclick_AddDevices_Devices_ListBox(self, evt):
        if not (self.AddDevices_Devices_ListBox.GetSelection() == -1):
            self.OnButton_AddDevices_Preferences_Button(evt)

    def OnButton_backwardButton(self, evt):
        self.previousPage()

    def OnButton_forwardButton(self, evt):
        self.nextPage()

    def OnButton_finishButton(self, evt):
        #self.__finishProject__()
        EsPeEs.executeFunctionAsyncron(self.__finishProject__, self.__finishProjectFailed__, self.__finishProjectSuccess__, useWx = True)
        self.__showLoadingGauge__()
        
    def __removeProject__(self):
        if self.isConnected() == True:
            counter = 0
            removeProjectValue = self.getClient().removeProject(self.getServerInformation().getAvailableProjects()[self.Projects_ListBox.GetSelection()])
            while (removeProjectValue == None) and (counter < EsPeEs.Preferences.SOAP.Retries):
                removeProjectValue = self.getClient().removeProject(self.getServerInformation().getAvailableProjects()[self.Projects_ListBox.GetSelection()])
                counter = counter + 1
            if counter >= EsPeEs.Preferences.SOAP.Retries:
                return None
            counter = 0
            serverInformation = self.getClient().getServerInformation()
            while (serverInformation == None) and (counter < EsPeEs.Preferences.SOAP.Retries):
                serverInformation = self.getClient().getServerInformation()
                counter = counter + 1
            if counter >= EsPeEs.Preferences.SOAP.Retries:
                return None
            return serverInformation.clone()
        return None
            
    def __removeProjectSuccess__(self, evt):
        self.setServerInformation(evt)
        self.__hideLoadingGauge__()
        
    def __removeProjectFailed__(self, evt):
        self.__hideLoadingGauge__()
        
    def __finishProject__(self):
        if self.isConnected() == True:
            espees_client = os.path.join(EsPeEs.getSaveFolder(), 'Client')   #/home/USER/.EsPeEs/Client
            espees_project = os.path.join(espees_client, self.__Project.getName())   #/home/USER/.EsPeEs/Client
            if not os.path.exists(EsPeEs.getSaveFolder()):
                EsPeEs.Utilities.makeDirectory(EsPeEs.getSaveFolder())
            if not os.path.exists(espees_client):
                EsPeEs.Utilities.makeDirectory(espees_client)
            if os.path.exists(espees_project):
                EsPeEs.Utilities.removeDirectory(espees_project)
            self.__Project.setTarget(self.getServerInformation().getTarget())
            self.__Project.setTargetTCPAdress(self.getClient().getIPAdress())
            self.__Project.save(espees_project)
            projectData = EsPeEs.ProjectData(name = self.__Project.getName())
            projectData.load(espees_client)
            self.getClient().uploadProject(projectData)
            serverInformation = self.getClient().getServerInformation()
            return serverInformation.clone()
        return None
            
    def __finishProjectSuccess__(self, evt):
        self.setServerInformation(evt)
        self.__Page = 0
        self.__hideLoadingGauge__()
        
    def __finishProjectFailed__(self, evt):
        self.__Page = 0
        self.__hideLoadingGauge__()
        
    def __programProject__(self):
        try:
            if self.isConnected() == True:
                projectName = self.getServerInformation().getAvailableProjects()[self.Projects_ListBox.GetSelection()]
                espees_client = os.path.join(EsPeEs.getSaveFolder(), 'Client')   #/home/USER/.EsPeEs/Client
                espees_project = os.path.join(espees_client, projectName)
                if not os.path.exists(EsPeEs.getSaveFolder()):
                    EsPeEs.Utilities.makeDirectory(EsPeEs.getSaveFolder())
                if not os.path.exists(espees_client):
                    EsPeEs.Utilities.makeDirectory(espees_client)
                projectData = self.getClient().downloadProject(self.getServerInformation().getAvailableProjects()[self.Projects_ListBox.GetSelection()])
                projectData.save(espees_client)
                wx.CallAfter(self.GetParent().Show, False)
                self.getClient().startPLC_Beremiz()
                EsPeEs.ProcessManagement.Instance().startEsPeEsCoder(espees_project)
                wx.CallAfter(self.GetParent().Show, True)
                self.getClient().stopPLC()
                projectData2 = EsPeEs.ProjectData(name = projectName)
                projectData2.load(espees_client)
                projectData.remove(espees_client)
                self.getClient().uploadProject(projectData2)
                serverInformation = self.getClient().getServerInformation()
                return serverInformation.clone()               
        except Exception, e:
            return None       
            
    def __programProjectSuccess__(self, evt):
        self.setServerInformation(evt)
        self.__hideLoadingGauge__()
        self.GetParent().Show()
        
    def __programProjectFailed__(self, evt):
        self.__hideLoadingGauge__()
        self.GetParent().Show()
        dialog = wx.MessageDialog(self, 'Ooops, connection with the server lost.\nPlease check the connection from the PC\nand the PLC.',  caption = 'Connection Error', style=wx.OK|wx.ICON_ERROR)
        dialog.ShowModal()
        dialog.Destroy()
        self.GetParent().Destroy()
        
    def __showLoadingGauge__(self):
        self.__Processing = True
        self.__refresh__()
        self.__LoadingTimer.Start(30)
        
    def __hideLoadingGauge__(self):
        self.__Processing = False
        self.__LoadingTimer.Stop()
        self.__refresh__()
        
    def __refreshLoadingGauge__(self, evt):
        self.Gauge.Pulse()

    def closingAllowed(self):
        if self.__Processing == True:
            return False
        else:
            return True
            
    def __disableAllPages__(self):
        self.__disableProjects__()
        self.__disableProjectInformation__()
        self.__disableSelectShield__()
        self.__disableSelectTarget__()
        self.__disableAddModbusDevices__()
        self.__disableAddSPIDevices__()
        self.__disableAddI2CDevices__()
        self.__disableProjectTree__()
        self.backwardButton.Disable()
        self.forwardButton.Disable()
        self.finishButton.Disable()
            
    def __hideAllPages__(self):
        self.__hideProjects__()
        self.__hideProjectInformation__()
        self.__hideSelectShield__()
        self.__hideSelectTarget__()
        self.__hideAddModbusDevices__()
        self.__hideAddSPIDevices__()
        self.__hideAddI2CDevices__()
        self.__hideProjectTree__()
        self.finishButton.Hide()
        self.StaticLine.Hide()
        self.Gauge.Hide()
        
    def __disableProjects__(self):
        self.Projects_ListBox.Disable()
        self.Projects_Add_Button.Disable()
        self.Projects_Remove_Button.Disable()
        self.Projects_Edit_Button.Disable()
        self.Projects_Beremiz_Button.Disable() 
        
    def __disableProjectInformation__(self):
        self.ProjectInformation_Name_Label.Disable()
        self.ProjectInformation_Name_TextCtrl.Disable()
        self.ProjectInformation_Company_Label.Disable()
        self.ProjectInformation_Company_TextCtrl.Disable()
        self.ProjectInformation_Product_Label.Disable()
        self.ProjectInformation_Product_TextCtrl.Disable()
        self.ProjectInformation_Version_Label.Disable()
        self.ProjectInformation_Version_TextCtrl.Disable()
        self.ProjectInformation_Error_Label.Disable()
        
    def __disableSelectTarget__(self):
        self.SelectTarget_TreeCtrl.Disable()
        
    def __disableSelectShield__(self):
        self.SelectShield_TreeCtrl.Disable()
        
    def __disableAddModbusDevices__(self):
        self.AddDevices_AvailableDevices_Label.Disable()
        self.AddDevices_TreeCtrl.Disable()
        self.AddDevices_Add_Button.Disable()
        self.AddDevices_Remove_Button.Disable()
        self.AddDevices_Preferences_Button.Disable()
        self.AddDevices_Devices_Label.Disable()
        self.AddDevices_Devices_ListBox.Disable()
        
    def __disableAddSPIDevices__(self):
        self.AddDevices_AvailableDevices_Label.Disable()
        self.AddDevices_TreeCtrl.Disable()
        self.AddDevices_Add_Button.Disable()
        self.AddDevices_Remove_Button.Disable()
        self.AddDevices_Preferences_Button.Disable()
        self.AddDevices_Devices_Label.Disable()
        self.AddDevices_Devices_ListBox.Disable()
        
    def __disableAddI2CDevices__(self):
        self.AddDevices_AvailableDevices_Label.Disable()
        self.AddDevices_TreeCtrl.Disable()
        self.AddDevices_Add_Button.Disable()
        self.AddDevices_Remove_Button.Disable()
        self.AddDevices_Preferences_Button.Disable()
        self.AddDevices_Devices_Label.Disable()
        self.AddDevices_Devices_ListBox.Disable()
        
    def __disableProjectTree__(self):
        self.ProjectTree_TreeCtrl.Disable()
            
    def __enableProjects__(self):
        self.Projects_ListBox.Enable()
        self.Projects_Add_Button.Enable()
        self.Projects_Remove_Button.Disable()
        self.Projects_Beremiz_Button.Disable() 
        self.Projects_Edit_Button.Disable()
        self.backwardButton.Disable()
        self.forwardButton.Disable()
        self.finishButton.Disable()
        
    def __enableProjectInformation__(self):
        self.ProjectInformation_Name_Label.Enable()
        self.ProjectInformation_Name_TextCtrl.Enable()
        self.ProjectInformation_Company_Label.Enable()
        self.ProjectInformation_Company_TextCtrl.Enable()
        self.ProjectInformation_Product_Label.Enable()
        self.ProjectInformation_Product_TextCtrl.Enable()
        self.ProjectInformation_Version_Label.Enable()
        self.ProjectInformation_Version_TextCtrl.Enable()
        self.ProjectInformation_Error_Label.Enable()
        if self.getServerInformation().existProject(self.ProjectInformation_Name_TextCtrl.GetValue()) == True:
            self.forwardButton.Disable()
        else:
            self.forwardButton.Enable()
        self.backwardButton.Enable()
        self.finishButton.Disable()
        
    def __enableSelectTarget__(self):
        self.SelectTarget_TreeCtrl.Enable()
        self.backwardButton.Enable()
        
    def __enableSelectShield__(self):
        self.SelectShield_TreeCtrl.Enable()
        self.backwardButton.Enable()
        
    def __enableAddModbusDevices__(self):
        self.AddDevices_AvailableDevices_Label.Enable()
        self.AddDevices_TreeCtrl.Enable()
        self.AddDevices_Add_Button.Disable()
        self.AddDevices_Remove_Button.Disable()
        self.AddDevices_Preferences_Button.Disable()
        self.AddDevices_Devices_Label.Enable()
        self.AddDevices_Devices_ListBox.Enable()
        self.backwardButton.Enable()
        self.forwardButton.Enable()
        self.finishButton.Disable()
        
    def __enableAddSPIDevices__(self):
        self.AddDevices_AvailableDevices_Label.Enable()
        self.AddDevices_TreeCtrl.Enable()
        self.AddDevices_Add_Button.Enable()
        self.AddDevices_Remove_Button.Disable()
        self.AddDevices_Preferences_Button.Disable()
        self.AddDevices_Devices_Label.Enable()
        self.AddDevices_Devices_ListBox.Enable()
        self.backwardButton.Enable()
        self.forwardButton.Enable()
        self.finishButton.Disable()
        
    def __enableAddI2CDevices__(self):
        self.AddDevices_AvailableDevices_Label.Enable()
        self.AddDevices_TreeCtrl.Enable()
        self.AddDevices_Add_Button.Disable()
        self.AddDevices_Remove_Button.Disable()
        self.AddDevices_Preferences_Button.Disable()
        self.AddDevices_Devices_Label.Enable()
        self.AddDevices_Devices_ListBox.Enable()
        self.backwardButton.Enable()
        self.forwardButton.Enable()
        self.finishButton.Disable()
        
    def __enableProjectTree__(self):
        self.ProjectTree_TreeCtrl.Enable()
        self.backwardButton.Enable()
        self.forwardButton.Disable()
        self.finishButton.Enable()
            
    def __hideProjects__(self):
        self.Projects_ListBox.Hide()
        self.Projects_Add_Button.Hide()
        self.Projects_Remove_Button.Hide()
        self.Projects_Edit_Button.Hide()
        self.Projects_Beremiz_Button.Hide() 
        
    def __hideProjectInformation__(self):
        self.ProjectInformation_Name_Label.Hide()
        self.ProjectInformation_Name_TextCtrl.Hide()
        self.ProjectInformation_Company_Label.Hide()
        self.ProjectInformation_Company_TextCtrl.Hide()
        self.ProjectInformation_Product_Label.Hide()
        self.ProjectInformation_Product_TextCtrl.Hide()
        self.ProjectInformation_Version_Label.Hide()
        self.ProjectInformation_Version_TextCtrl.Hide()
        self.ProjectInformation_Error_Label.Hide()
        
    def __hideSelectTarget__(self):
        self.SelectTarget_TreeCtrl.Hide()
        
    def __hideSelectShield__(self):
        self.SelectShield_TreeCtrl.Hide()
        
    def __hideAddModbusDevices__(self):
        self.AddDevices_AvailableDevices_Label.Hide()
        self.AddDevices_TreeCtrl.Hide()
        self.AddDevices_Add_Button.Hide()
        self.AddDevices_Remove_Button.Hide()
        self.AddDevices_Preferences_Button.Hide()
        self.AddDevices_Devices_Label.Hide()
        self.AddDevices_Devices_ListBox.Hide()
        
    def __hideAddSPIDevices__(self):
        self.AddDevices_AvailableDevices_Label.Hide()
        self.AddDevices_TreeCtrl.Hide()
        self.AddDevices_Add_Button.Hide()
        self.AddDevices_Remove_Button.Hide()
        self.AddDevices_Preferences_Button.Hide()
        self.AddDevices_Devices_Label.Hide()
        self.AddDevices_Devices_ListBox.Hide()
        
    def __hideAddI2CDevices__(self):
        self.AddDevices_AvailableDevices_Label.Hide()
        self.AddDevices_TreeCtrl.Hide()
        self.AddDevices_Add_Button.Hide()
        self.AddDevices_Remove_Button.Hide()
        self.AddDevices_Preferences_Button.Hide()
        self.AddDevices_Devices_Label.Hide()
        self.AddDevices_Devices_ListBox.Hide()
        
    def __hideProjectTree__(self):
        self.ProjectTree_TreeCtrl.Hide()
            
    def __showProjects__(self):
        self.titleLabel.SetLabel('Projects')
        self.Projects_ListBox.Clear()
        if not (self.getServerInformation() == None):
            projects = self.getServerInformation().getAvailableProjects()
            for i in range(len(projects)):
                self.Projects_ListBox.Append(projects[i])
        self.Projects_ListBox.Show()
        self.Projects_Add_Button.Show()
        self.Projects_Remove_Button.Show()
        self.Projects_Edit_Button.Hide()
        self.Projects_Beremiz_Button.Show() 
        self.backwardButton.Hide()
        self.forwardButton.Hide()
        self.finishButton.Hide()
        
    def __showProjectInformation__(self):
        self.titleLabel.SetLabel('Project information')
        if self.getServerInformation().existProject(self.ProjectInformation_Name_TextCtrl.GetValue()) == True:
            self.ProjectInformation_Error_Label.Show()
        else:
            self.ProjectInformation_Error_Label.Hide()
        self.ProjectInformation_Name_Label.Show()
        self.ProjectInformation_Name_TextCtrl.Show()
        self.ProjectInformation_Company_Label.Show()
        self.ProjectInformation_Company_TextCtrl.Show()
        self.ProjectInformation_Product_Label.Show()
        self.ProjectInformation_Product_TextCtrl.Show()
        self.ProjectInformation_Version_Label.Show()
        self.ProjectInformation_Version_TextCtrl.Show()
        self.backwardButton.Show()
        self.forwardButton.Show()
        self.finishButton.Hide()
        
    def __showSelectTarget__(self):
        self.titleLabel.SetLabel('Select programmable logic controller')
        self.SelectTarget_TreeCtrl.Show()
        self.backwardButton.Show()
        self.forwardButton.Show()
        self.finishButton.Hide()
        
    def __showSelectShield__(self):
        self.titleLabel.SetLabel('Select Raspberry Pi module')
        self.SelectShield_TreeCtrl.Show()
        self.backwardButton.Show()
        self.forwardButton.Show()
        self.finishButton.Hide()
        
    def __showAddModbusDevices__(self):
        self.titleLabel.SetLabel('Add Modbus-devices')
        self.__refreshTreeCtrl__()
        self.AddDevices_Devices_ListBox.Clear()
        if not(self.__Project == None):
            usedModbusDevices = self.__Project.getModbusDevices()
            for i in range(len(usedModbusDevices)):
                self.AddDevices_Devices_ListBox.Append(usedModbusDevices[i].getName())
        self.AddDevices_AvailableDevices_Label.Show()
        self.AddDevices_TreeCtrl.Show()
        self.AddDevices_Add_Button.Show()
        self.AddDevices_Remove_Button.Show()
        self.AddDevices_Preferences_Button.Show()
        self.AddDevices_Devices_Label.Show()
        self.AddDevices_Devices_ListBox.Show()
        self.backwardButton.Show()
        self.forwardButton.Show()
        self.finishButton.Hide()
        
    def __showAddSPIDevices__(self):
        self.titleLabel.SetLabel('Add SPI-devices')
        self.__refreshTreeCtrl__()
        self.AddDevices_Devices_ListBox.Clear()
        if not(self.__Project == None):
            usedSPIDevices = self.__Project.getSPIDevices()
            for i in range(len(usedSPIDevices)):
                self.AddDevices_Devices_ListBox.Append(usedSPIDevices[i].getName())
        self.AddDevices_AvailableDevices_Label.Show()
        self.AddDevices_TreeCtrl.Show()
        self.AddDevices_Add_Button.Show()
        self.AddDevices_Remove_Button.Show()
        self.AddDevices_Preferences_Button.Show()
        self.AddDevices_Devices_Label.Show()
        self.AddDevices_Devices_ListBox.Show()
        self.backwardButton.Show()
        self.forwardButton.Show()
        self.finishButton.Hide()
        
    def __showAddI2CDevices__(self):
        self.titleLabel.SetLabel('Add I²C-devices')
        self.__refreshTreeCtrl__()
        self.AddDevices_Devices_ListBox.Clear()
        if not(self.__Project == None):
            usedI2CDevices = self.__Project.getI2CDevices()
            for i in range(len(usedI2CDevices)):
                self.AddDevices_Devices_ListBox.Append(usedI2CDevices[i].getName())
        self.AddDevices_AvailableDevices_Label.Show()
        self.AddDevices_TreeCtrl.Show()
        self.AddDevices_Add_Button.Show()
        self.AddDevices_Remove_Button.Show()
        self.AddDevices_Preferences_Button.Show()
        self.AddDevices_Devices_Label.Show()
        self.AddDevices_Devices_ListBox.Show()
        self.backwardButton.Show()
        self.forwardButton.Show()
        self.finishButton.Hide()
        
    def __showProjectTree__(self):
        self.titleLabel.SetLabel('Project-tree')
        self.ProjectTree_TreeCtrl.DeleteAllItems()  
        root = self.ProjectTree_TreeCtrl.AddRoot(self.__Project.getName(), self.__ProjectImage)
        if self.__Shield.isModbusCompatible() == True:
            modbus = self.ProjectTree_TreeCtrl.AppendItem(root, 'Modbus-Devices', self.__ModuleImage)
            modbusDevices = self.__Project.getModbusDevices()
            for i in range(len(modbusDevices)):
                self.ProjectTree_TreeCtrl.AppendItem(modbus, modbusDevices[i].getName(), self.__DriverImage)
        if self.__Shield.isSPICompatible() == True:
            spi = self.ProjectTree_TreeCtrl.AppendItem(root, 'SPI-Devices', self.__ModuleImage)
            spiDevices = self.__Project.getSPIDevices()
            for i in range(len(spiDevices)):
                self.ProjectTree_TreeCtrl.AppendItem(spi, spiDevices[i].getName(), self.__DriverImage)
        if self.__Shield.isI2CCompatible() == True:
            i2c = self.ProjectTree_TreeCtrl.AppendItem(root, 'I²C-Devices', self.__ModuleImage)
            i2cDevices = self.__Project.getI2CDevices()
            for i in range(len(i2cDevices)):
                self.ProjectTree_TreeCtrl.AppendItem(i2c, i2cDevices[i].getName(), self.__DriverImage)     
        self.ProjectTree_TreeCtrl.ExpandAll()
        self.ProjectTree_TreeCtrl.Show()
        self.backwardButton.Show()
        self.forwardButton.Hide()
        self.finishButton.Show()
            
    def __refresh__(self):
        if self.__Processing == False:
            self.__hideAllPages__()
            self.__disableAllPages__()
            if self.__Page == 0:
                self.__enableProjects__()
                self.__showProjects__()
            if self.__Page == 1:
                self.__enableProjectInformation__()
                self.__showProjectInformation__()
            if self.__Page == 2:
                self.__enableSelectTarget__()
                self.__showSelectTarget__()
            if self.__Page == 3:
                self.__enableSelectShield__()
                self.__showSelectShield__()
            if self.__Page == 4:
                self.__enableAddModbusDevices__()
                self.__showAddModbusDevices__()
            if self.__Page == 5:
                self.__enableAddSPIDevices__()
                self.__showAddSPIDevices__()
            if self.__Page == 6:
                self.__enableAddI2CDevices__()
                self.__showAddI2CDevices__()
            if self.__Page == 7:
                self.__enableProjectTree__()
                self.__showProjectTree__()
        else:
            self.__disableAllPages__()
            self.backwardButton.Hide()
            self.forwardButton.Hide()
            self.finishButton.Hide()
            self.StaticLine.Show()
            self.Gauge.Show()
        self.Layout()
            
    def nextPage(self):
        if self.__Page == 0:
            self.__Project = EsPeEs.Project('')
            self.__Page = 1
            self.ProjectInformation_Name_TextCtrl.SetValue('Unknown')
            self.ProjectInformation_Company_TextCtrl.SetValue('Unknown')
            self.ProjectInformation_Product_TextCtrl.SetValue('Unknown')
            self.ProjectInformation_Version_TextCtrl.SetValue('1.0')
            self.__Shield = None
            self.__ShieldPath = None
            self.__refresh__()
            return
            
        if self.__Page == 1:
            self.__Project.setName(self.ProjectInformation_Name_TextCtrl.GetValue())
            self.__Project.setCompanyName(self.ProjectInformation_Name_TextCtrl.GetValue())
            self.__Project.setProductName(self.ProjectInformation_Name_TextCtrl.GetValue())
            self.__Project.setProductVersion(self.ProjectInformation_Name_TextCtrl.GetValue())
            plcs = EsPeEs.DriverManager.Instance().listAvailablePLCs(self.getServerInformation().getTarget())
            
            if len(plcs) > 1:
                self.__Page = 2
                self.__refresh__()
                self.__refreshTreeCtrl__(self.__TargetPath)
            else:
                self.__TargetPath = plcs[0]
                target = EsPeEs.DriverManager.Instance().getDriver(self.__TargetPath, self.__getCExtensionType__())
                if not (self.__Target == None):
                    if not (self.__Target.getName() == target.getName()):
                        if target.isModbusCompatible() == False:
                            self.__Project.clearModbusDevices()
                        if target.isSPICompatible() == False:
                            self.__Project.clearSPIDevices()
                        if target.isI2CCompatible() == False:
                            self.__Project.clearI2CDevices()
                        self.__Target = target
                        self.__Project.setTargetDevice(self.__Target)
                else:
                    self.__TargetPath = plcs[0]
                    self.__Target = target
                    self.__Project.setTargetDevice(self.__Target)
                    
                if self.getServerInformation().isRaspberryPi() == True:
                    self.__Page = 3
                    self.__refresh__()
                    self.__refreshTreeCtrl__(self.__ShieldPath)
                    return
                else:
                    self.__Shield = EsPeEs.DriverManager.Instance().getPCShield()
                    self.__Project.setShield(self.__Shield)
                    if self.__Project.getShield().isModbusCompatible() == True:
                        self.__Page = 4
                        self.__refresh__()
                        return
                    else:
                        if self.__Project.getShield().isSPICompatible() == True:
                            self.__Page = 5
                            self.__refresh__()
                            return
                        else:
                            if self.__Project.getShield().isI2CCompatible() == True:
                                self.__Page = 6
                                self.__refresh__()
                                return
                            else:
                                self.__Page = 7
                                self.__refresh__()
                                return
            return
            
        if self.__Page == 2:
            self.__TargetPath = self.__getPath__(self.SelectTarget_TreeCtrl)
            target = EsPeEs.DriverManager.Instance().getDriver(self.__TargetPath, self.__getCExtensionType__())
            if not (self.__Target == None):
                if not (self.__Target.getName() == target.getName()):
                    if target.isModbusCompatible() == False:
                        self.__Project.clearModbusDevices()
                    if target.isSPICompatible() == False:
                        self.__Project.clearSPIDevices()
                    if target.isI2CCompatible() == False:
                        self.__Project.clearI2CDevices()
                    self.__Target = target
                    self.__Project.setTargetDevice(self.__Target)
            if self.getServerInformation().isRaspberryPi() == True:
                self.__Page = 3
                self.__refresh__()
                self.__refreshTreeCtrl__(self.__ShieldPath)
                return
            else:
                self.__Shield = EsPeEs.DriverManager.Instance().getPCShield()
                self.__Project.setShield(self.__Shield)
                if self.__Project.getShield().isModbusCompatible() == True:
                    self.__Page = 4
                    self.__refresh__()
                    return
                else:
                    if self.__Project.getShield().isSPICompatible() == True:
                        self.__Page = 5
                        self.__refresh__()
                        return
                    else:
                        if self.__Project.getShield().isI2CCompatible() == True:
                            self.__Page = 6
                            self.__refresh__()
                            return
                        else:
                            self.__Page = 7
                            self.__refresh__()
                            return
                     
        if self.__Page == 3:
            self.__ShieldPath = self.__getPath__(self.SelectShield_TreeCtrl)
            shield = EsPeEs.DriverManager.Instance().getDriver(self.__ShieldPath, self.__getCExtensionType__())
            if not (self.__Shield == None):
                if not (self.__Shield.getName() == shield.getName()):
                    if shield.isModbusCompatible() == False:
                        self.__Project.clearModbusDevices()
                    if shield.isSPICompatible() == False:
                        self.__Project.clearSPIDevices()
                    if shield.isI2CCompatible() == False:
                        self.__Project.clearI2CDevices()
                    self.__Shield = shield
                    self.__Project.setShield(self.__Shield)
            else:
                self.__Shield = shield
                self.__Project.setShield(self.__Shield)
            if self.__Project.getShield().isModbusCompatible() == True:
                self.__Page = 4
                self.__refresh__()
                return
            else:
                if self.__Project.getShield().isSPICompatible() == True:
                    self.__Page = 5
                    self.__refresh__()
                    return
                else:
                    if self.__Project.getShield().isI2CCompatible() == True:
                        self.__Page = 6
                        self.__refresh__()
                        return
                    else:
                        self.__Page = 7
                        self.__refresh__()
                        return
                        
        if self.__Page == 4:
            if self.__Project.getShield().isSPICompatible() == True:
                self.__Page = 5
                self.__refresh__()
                return
            else:
                if self.__Project.getShield().isI2CCompatible() == True:
                    self.__Page = 6
                    self.__refresh__()
                    return
                else:
                    self.__Page = 7
                    self.__refresh__()
                    return
                    
        if self.__Page == 5:
            if self.__Project.getShield().isI2CCompatible() == True:
                self.__Page = 6
                self.__refresh__()
                return
            else:
                self.__Page = 7
                self.__refresh__()
                return
                
        if self.__Page == 6:
            self.__Page = 7
            self.__refresh__()
            return
                    
    def previousPage(self):
        if self.__Page == 1:
            self.__Page =  0
            self.__refresh__()
            return
            
        if self.__Page == 2:
            self.__Page =  1
            self.__refresh__()
            return
            
        if self.__Page == 3:
            if len(EsPeEs.DriverManager.Instance().listAvailablePLCs(self.getServerInformation().getTarget())) > 1:
                self.__Page = 2
                self.__refresh__()
                self.__refreshTreeCtrl__(self.__TargetPath)
                return
            else:
                self.__Page = 1
                self.__refresh__()
            
        if self.__Page == 4:
            if self.getServerInformation().isRaspberryPi() == True:
                self.__Page = 3
                self.__refresh__()
                self.__refreshTreeCtrl__(self.__ShieldPath)
                return
            else:
                if len(EsPeEs.DriverManager.Instance().listAvailablePLCs(self.getServerInformation().getTarget())) > 1:
                    self.__Page = 2
                    self.__refresh__()
                    self.__refreshTreeCtrl__(self.__TargetPath)
                    return
                else:
                    self.__Page = 1
                    self.__refresh__()
    
        if self.__Page == 5:
            if self.__Project.getShield().isModbusCompatible() == True:
                self.__Page = 4
                self.__refresh__()
                return
            else:
                if self.getServerInformation().isRaspberryPi() == True:
                    self.__Page = 3
                    self.__refresh__()
                    self.__refreshTreeCtrl__(self.__ShieldPath)
                    return
                else:
                    if len(EsPeEs.DriverManager.Instance().listAvailablePLCs(self.getServerInformation().getTarget())) > 1:
                        self.__Page = 2
                        self.__refresh__()
                        self.__refreshTreeCtrl__(self.__TargetPath)
                        return
                    else:
                        self.__Page = 1
                        self.__refresh__()
                
        if self.__Page == 6:
            if self.__Project.getShield().isSPICompatible() == True:
                self.__Page = 5
                self.__refresh__()
                return
            else:
                if self.__Project.getShield().isModbusCompatible() == True:
                    self.__Page = 4
                    self.__refresh__()
                    return
                else:
                    if self.getServerInformation().isRaspberryPi() == True:
                        self.__Page = 3
                        self.__refresh__()
                        self.__refreshTreeCtrl__(self.__ShieldPath)
                        return
                    else:
                        if len(EsPeEs.DriverManager.Instance().listAvailablePLCs(self.getServerInformation().getTarget())) > 1:
                            self.__Page = 2
                            self.__refresh__()
                            self.__refreshTreeCtrl__(self.__TargetPath)
                            return
                        else:
                            self.__Page = 1
                            self.__refresh__()
                
        if self.__Page == 7:
            if self.__Project.getShield().isI2CCompatible() == True:
                self.__Page = 6
                self.__refresh__()
                return
            else:
                if self.__Project.getShield().isSPICompatible() == True:
                    self.__Page = 5
                    self.__refresh__()
                    return
                else:
                    if self.__Project.getShield().isModbusCompatible() == True:
                        self.__Page = 4
                        self.__refresh__()
                        return
                    else:
                        if self.getServerInformation().isRaspberryPi() == True:
                            self.__Page = 3
                            self.__refresh__()
                            self.__refreshTreeCtrl__(self.__ShieldPath)
                            return
                        else:
                            if len(EsPeEs.DriverManager.Instance().listAvailablePLCs(self.getServerInformation().getTarget())) > 1:
                                self.__Page = 2
                                self.__refresh__()
                                self.__refreshTreeCtrl__(self.__TargetPath)
                                return
                            else:
                                self.__Page = 1
                                self.__refresh__()
                                                
    def __refreshTreeCtrl__(self, selectionPath = None):
        if self.__Page == 4:
            self.AddDevices_TreeCtrl.DeleteAllItems()
            self.__RootItem = self.AddDevices_TreeCtrl.AddRoot('Modbus modules', self.__ModuleImage)
            self.__appendChildsToTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.ModbusDevice, self.AddDevices_TreeCtrl)
            self.AddDevices_TreeCtrl.ExpandAll()
            self.AddDevices_TreeCtrl.SelectItem(self.__RootItem)
            
        if self.__Page == 5:
            self.AddDevices_TreeCtrl.DeleteAllItems()
            self.__RootItem = self.AddDevices_TreeCtrl.AddRoot('SPI modules', self.__ModuleImage)
            self.__appendChildsToTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.SPIDevice, self.AddDevices_TreeCtrl)
            self.AddDevices_TreeCtrl.ExpandAll()
            self.AddDevices_TreeCtrl.SelectItem(self.__RootItem)
            
        if self.__Page == 6:
            self.AddDevices_TreeCtrl.DeleteAllItems()
            self.__RootItem = self.AddDevices_TreeCtrl.AddRoot('I2C modules', self.__ModuleImage)
            self.__appendChildsToTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.I2CDevice, self.AddDevices_TreeCtrl)
            self.AddDevices_TreeCtrl.ExpandAll()
            self.AddDevices_TreeCtrl.SelectItem(self.__RootItem)
            
        if self.__Page == 3:
            self.SelectShield_TreeCtrl.DeleteAllItems()
            self.__RootItem = self.SelectShield_TreeCtrl.AddRoot('Raspberry Pi modules', self.__ModuleImage)
            treeItem = self.__appendChildsToTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.Shield, self.SelectShield_TreeCtrl, selectionPath = selectionPath)
            self.SelectShield_TreeCtrl.ExpandAll()
            if not (treeItem == None):
                self.SelectShield_TreeCtrl.SelectItem(treeItem, True)
            else:
                self.OnTree_sel_changed_SelectShield_TreeCtrl(None)
                
        if self.__Page == 2:
            self.SelectTarget_TreeCtrl.DeleteAllItems()
            self.__RootItem = self.SelectTarget_TreeCtrl.AddRoot('Programmable logic controllers', self.__ModuleImage)
            treeItem = self.__appendChildsToTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.TargetDevice, self.SelectTarget_TreeCtrl, selectionPath = selectionPath, target = self.getServerInformation().getTarget())
            self.SelectTarget_TreeCtrl.ExpandAll()
            if not (treeItem == None):
                self.SelectTarget_TreeCtrl.SelectItem(treeItem, True)
            else:
                self.OnTree_sel_changed_SelectTarget_TreeCtrl(None)
        
    def __appendChildsToTreeCtrl__(self, parentTreeItem, path, cextensionType, treeCtrl, selectionPath = None, selectedTreeItem = None, target = None):
        throw = False
        childs = sorted(EsPeEs.DriverManager.Instance().listChilds(path, cextensionType))
        for i in range(len(childs)):
            throw = False
            childPath = EsPeEs.DriverManager.Instance().joinPath(path, childs[i])
            childEntryType = EsPeEs.DriverManager.Instance().getEntryType(childPath, cextensionType)
            if childEntryType == 'Directory':
                image = self.__DirectoryImage
            if childEntryType == 'Driver':
                image = self.__DriverImage
            if not ((cextensionType == EsPeEs.CExtension.Type.TargetDevice) and (childEntryType == 'Driver')):
                treeItem = treeCtrl.AppendItem(parentTreeItem, childs[i], image)
            else:
                
                if (EsPeEs.DriverManager.Instance().getDriver(childPath, cextensionType).getTarget() == target):
                    treeItem = treeCtrl.AppendItem(parentTreeItem, childs[i], image)
                else:
                    throw = True
            if not (throw):
                if not (selectionPath == None):
                    if EsPeEs.DriverManager.Instance().joinPath(path, childs[i]) == selectionPath:
                        selectedTreeItem = treeItem
                if (EsPeEs.DriverManager.Instance().hasChilds(childPath, cextensionType) == True) and not (childEntryType == 'Driver'):
                    selectedTreeItem = self.__appendChildsToTreeCtrl__(treeItem, childPath, cextensionType, treeCtrl, selectionPath = selectionPath, selectedTreeItem = selectedTreeItem, target = target)
        return selectedTreeItem
                
    def __getCExtensionType__(self):
        cextensionType = None
        if (self.__Page == 2) or (self.__Page == 1):
            cextensionType = EsPeEs.CExtension.Type.TargetDevice
        if self.__Page == 3:
            cextensionType = EsPeEs.CExtension.Type.Shield
        if self.__Page == 4:
            cextensionType = EsPeEs.CExtension.Type.ModbusDevice
        if self.__Page == 5:
            cextensionType = EsPeEs.CExtension.Type.SPIDevice
        if self.__Page == 6:
            cextensionType = EsPeEs.CExtension.Type.I2CDevice
        return cextensionType

    def __getPath__(self, treeCtrl):
        treeItem = treeCtrl.GetSelection()
        path = range(0, 0)
        if treeItem == self.__RootItem:
            return path
        else:
            return self.__getPathRecursive__(path, treeItem, treeCtrl)
            
    def __getPathRecursive__(self, path, treeItem, treeCtrl):
        parentItem = treeCtrl.GetItemParent(treeItem)
        if parentItem == self.__RootItem:
            newPath = range(0, 0)
            newPath.append(treeCtrl.GetItemText(treeItem))
            for i in range(len(path)):
                newPath.append(path[i])
            return newPath
        else:
            newPath = range(0, 0)
            newPath.append(treeCtrl.GetItemText(treeItem))
            for i in range(len(path)):
                newPath.append(path[i])
            return self.__getPathRecursive__(newPath, parentItem, treeCtrl)

    def OnTree_sel_changed_SelectShield_TreeCtrl(self, evt):
        path = self.__getPath__(self.SelectShield_TreeCtrl)
        entryType = EsPeEs.DriverManager.Instance().getEntryType(path, self.__getCExtensionType__()) 
        if entryType == 'Directory':
            self.forwardButton.Disable()
            
        if len(path) == 0:
            self.forwardButton.Disable()
                
        if entryType == 'Driver':
            self.forwardButton.Enable()
            
    def OnTree_sel_changed_SelectTarget_TreeCtrl(self, evt):
        try:
            path = self.__getPath__(self.SelectTarget_TreeCtrl)
            entryType = EsPeEs.DriverManager.Instance().getEntryType(path, self.__getCExtensionType__()) 
            if entryType == 'Directory':
                self.forwardButton.Disable()
            
            if len(path) == 0:
                self.forwardButton.Disable()
                
            if entryType == 'Driver':
                self.forwardButton.Enable()
        except:
            pass
            
    def OnTree_sel_changed_AddDevices_TreeCtrl(self, evt):
        path = self.__getPath__(self.AddDevices_TreeCtrl)
        entryType = EsPeEs.DriverManager.Instance().getEntryType(path, self.__getCExtensionType__()) 
        if entryType == 'Directory':
            self.AddDevices_Add_Button.Disable()
                           
        if entryType == 'Driver':
            self.AddDevices_Add_Button.Enable()
            
        if len(path) == 0:
            self.AddDevices_Add_Button.Disable()
        
class RunProjectPanel(wx.Panel, UserInterface):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, client, serverInformation, trayIcon):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "RunProjectPanel")
        self.PostCreate(pre)

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Choice = xrc.XRCCTRL(self, "Choice")
        self.Start_Button = xrc.XRCCTRL(self, "Start_Button")
        self.Stop_Button = xrc.XRCCTRL(self, "Stop_Button")
        self.TextCtrl = xrc.XRCCTRL(self, "TextCtrl")
        self.StaticLine = xrc.XRCCTRL(self, "StaticLine")
        self.Gauge = xrc.XRCCTRL(self, "Gauge")

        self.Bind(wx.EVT_CHOICE, self.OnChoice_Choice, self.Choice)
        self.Bind(wx.EVT_BUTTON, self.OnButton_Start_Button, self.Start_Button)
        self.Bind(wx.EVT_BUTTON, self.OnButton_Stop_Button, self.Stop_Button)
        self.Bind(wx.EVT_TEXT, self.OnText_TextCtrl, self.TextCtrl)
        
        UserInterface.__init__(self, client, serverInformation)
        self.__LoadingTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.__refreshLoadingGauge__, self.__LoadingTimer)
        
        self.__RunableProjects = self.getServerInformation().getRunableProjects()
        if len(self.__RunableProjects) > 0:
            for i in range(len(self.__RunableProjects)):
                self.Choice.Append(self.__RunableProjects[i])
            self.Choice.SetSelection(0)    
        
        self.__TrayIcon = trayIcon
        self.__Processing = False
        
        self.__refresh__()

    def OnChoice_Choice(self, evt):
        pass

    def OnButton_Start_Button(self, evt):
        self.getClient().startPLC_Project(self.__RunableProjects[self.Choice.GetSelection()])
        self.__refresh__()

    def OnButton_Stop_Button(self, evt):
        self.getClient().stopPLC()
        self.__refresh__()

    def OnText_TextCtrl(self, evt):
        print "OnText_TextCtrl()"
        
    def __refresh__(self):
        if self.__Processing == False:
            if self.getClient().plcIsRunning() == 0:
                self.Choice.Enable()
                self.Stop_Button.Hide()
                self.Start_Button.Show()
            if self.getClient().plcIsRunning() == 2:
                project = self.getClient().plcProject()
                for i in range(len(self.__RunableProjects)):
                    if self.__RunableProjects[i] == project:
                        self.Choice.SetSelection(i)
                self.Choice.Disable()
                self.Start_Button.Hide()
                self.Stop_Button.Show()
            self.TextCtrl.Hide()
            self.StaticLine.Hide()
            self.Gauge.Hide()
            self.Choice.Show()
            
        else:
            self.Choice.Hide()
            self.TextCtrl.Hide()
            self.Stop_Button.Hide()
            self.Start_Button.Hide()
            self.StaticLine.Show()
            self.Gauge.Show()
        
        self.Layout()
        
    def __showLoadingGauge__(self):
        self.__Processing = True
        self.__refresh__()
        self.__LoadingTimer.Start(30)
        
    def __hideLoadingGauge__(self):
        self.__Processing = False
        self.__LoadingTimer.Stop()
        self.__refresh__()
        
    def __refreshLoadingGauge__(self, evt):
        self.Gauge.Pulse()

class DevicePanel(wx.Panel, UserInterface):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, client, serverInformation, device, project):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "DevicePanel")
        self.PostCreate(pre)

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.DeviceName_Label = xrc.XRCCTRL(self, "DeviceName_Label")
        self.DeviceNameSet_Label = xrc.XRCCTRL(self, "DeviceNameSet_Label")
        self.Name_Label = xrc.XRCCTRL(self, "Name_Label")
        self.Name_TextCtrl = xrc.XRCCTRL(self, "Name_TextCtrl")
        self.nameAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "nameAlreadyBeenTaken_Label")
        self.illegalName_Label = xrc.XRCCTRL(self, "illegalName_Label")
        self.Interface_Label = xrc.XRCCTRL(self, "Interface_Label")
        self.Interface_Choice = xrc.XRCCTRL(self, "Interface_Choice")
        self.Adress_Label = xrc.XRCCTRL(self, "Adress_Label")
        self.Adress_SpinCtrl = xrc.XRCCTRL(self, "Adress_SpinCtrl")
        self.adressAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "adressAlreadyBeenTaken_Label")
        self.Modbus_Label = xrc.XRCCTRL(self, "Modbus_Label")
        self.Modbus_Choice = xrc.XRCCTRL(self, "Modbus_Choice")
        self.TCPAdress_Label = xrc.XRCCTRL(self, "TCPAdress_Label")
        self.TCPAdress_TextCtrl = xrc.XRCCTRL(self, "TCPAdress_TextCtrl")
        self.TCPError_Label = xrc.XRCCTRL(self, "TCPError_Label")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.addButton = xrc.XRCCTRL(self, "addButton")
        self.applyButton = xrc.XRCCTRL(self, "applyButton")

        self.Bind(wx.EVT_TEXT, self.OnText_Name_TextCtrl, self.Name_TextCtrl)
        self.Bind(wx.EVT_CHOICE, self.OnChoice_Interface_Choice, self.Interface_Choice)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinctrl_Adress_SpinCtrl, self.Adress_SpinCtrl)
        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_addButton, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_applyButton, self.applyButton)
        self.Bind(wx.EVT_TEXT, self.OnText_TCPAdress_TextCtrl, self.TCPAdress_TextCtrl)
        self.Bind(wx.EVT_CHOICE, self.OnChoice_Modbus_Choice, self.Modbus_Choice)
        
        UserInterface.__init__(self, client, serverInformation)
        
        self.__Project = project
        self.__Device = device
        self.__DeviceType = -1
        self.__EditOrAdd = False
        
        if not (self.__Device == None):
            self.DeviceNameSet_Label.SetLabel(self.__Device.getDeviceName())
            self.Name_TextCtrl.SetValue(self.__Device.getName())

    def OnText_Name_TextCtrl(self, evt):
        self.__check__()
        
    def OnText_TCPAdress_TextCtrl(self, evt):
        self.__check__()
        
    def OnChoice_Modbus_Choice(self, evt):
        i = self.Modbus_Choice.GetSelection()
        if i == 0:
            self.TCPAdress_TextCtrl.Hide()
            self.TCPError_Label.Hide()
            self.TCPAdress_Label.Hide()
            self.Interface_Label.Show()
            self.Interface_Choice.Show()
            self.Adress_Label.Show()
            self.Adress_SpinCtrl.Show()
        if i == 1:
            self.Interface_Label.Hide()
            self.Interface_Choice.Hide()
            self.Adress_Label.Hide()
            self.Adress_SpinCtrl.Hide()
            self.adressAlreadyBeenTaken_Label.Hide()
            self.TCPAdress_Label.Show()
            self.TCPAdress_TextCtrl.Show()
        self.__check__()

    def OnChoice_Interface_Choice(self, evt):
        self.__check__()

    def OnSpinctrl_Adress_SpinCtrl(self, evt):
        self.__check__()

    def OnButton_cancelButton(self, evt):
        self.GetParent().OnClose(evt)

    def OnButton_addButton(self, evt):
        if self.__check__() == True:
            if self.__DeviceType == 0:
                modbus = None
                self.__Device.setName(self.Name_TextCtrl.GetValue())
                if self.Modbus_Choice.GetSelection() == 0:
                    self.__Device.setAdress(self.Adress_SpinCtrl.GetValue())
                    modbus = EsPeEs.Modbus.Interface(serialport = self.Interface_Choice.GetString(self.Interface_Choice.GetSelection()))
                if self.Modbus_Choice.GetSelection() == 1:
                    modbus = EsPeEs.Modbus.Interface(ipadress = EsPeEs.extractAdress(self.TCPAdress_TextCtrl.GetValue()), port = EsPeEs.extractPort(self.TCPAdress_TextCtrl.GetValue()))
                if not (modbus == None):
                    self.__Device.setModbusInterface(modbus)
                    self.__Project.addModbusDevice(instance = self.__Device)
                self.GetParent().EndModal(1)
            
            if self.__DeviceType == 1:
                self.__Device.setName(self.Name_TextCtrl.GetValue())
                self.__Device.setAdress(self.Adress_SpinCtrl.GetValue())
                self.__Project.addSPIDevice(instance = self.__Device)
                self.GetParent().EndModal(1)
                
            if self.__DeviceType == 2:
                self.__Device.setName(self.Name_TextCtrl.GetValue())
                self.__Device.setSubAdress(self.Adress_SpinCtrl.GetValue())
                self.__Project.addI2CDevice(instance = self.__Device)
                self.GetParent().EndModal(1)

    def OnButton_applyButton(self, evt):
        if self.__check__() == True:
            if self.__DeviceType == 0:
                self.__Device.setName(self.Name_TextCtrl.GetValue())
                modbus = None
                if self.Modbus_Choice.GetSelection() == 0:
                    self.__Device.setAdress(self.Adress_SpinCtrl.GetValue())
                    modbus = EsPeEs.Modbus.Interface(serialport = self.Interface_Choice.GetString(self.Interface_Choice.GetSelection()))
                if self.Modbus_Choice.GetSelection() == 1:
                    modbus = EsPeEs.Modbus.Interface(ipadress = EsPeEs.extractAdress(self.TCPAdress_TextCtrl.GetValue()), port = EsPeEs.extractPort(self.TCPAdress_TextCtrl.GetValue()))
                if not (modbus == None):
                    self.__Device.setModbusInterface(modbus)
                self.GetParent().EndModal(1)
            
            if self.__DeviceType == 1:
                self.__Device.setName(self.Name_TextCtrl.GetValue())
                self.__Device.setAdress(self.Adress_SpinCtrl.GetValue())
                self.GetParent().EndModal(1)
                
            if self.__DeviceType == 2:
                self.__Device.setName(self.Name_TextCtrl.GetValue())
                self.__Device.setSubAdress(self.Adress_SpinCtrl.GetValue())
                self.GetParent().EndModal(1)
        
    def __refresh__(self):
        if self.__DeviceType == 0:
            if self.__EditOrAdd == True:
                self.TitleLabel.SetLabel('Edit Modbus-device')
                self.addButton.Hide()
                modbusInterface = self.__Device.getModbusInterface()
                if modbusInterface.getMode() == 'RTU':
                    self.Modbus_Choice.SetSelection(0)
                    self.TCPAdress_TextCtrl.Hide()
                    self.TCPError_Label.Hide()
                    self.TCPAdress_Label.Hide()
                    self.Interface_Label.Show()
                    self.Interface_Choice.Show()
                    self.Adress_Label.Show()
                    self.Adress_SpinCtrl.Show()
                    self.adressAlreadyBeenTaken_Label.Hide()
                    serialPorts = self.getServerInformation().getSerialPorts()
                    for i in range(len(serialPorts)):
                        if serialPorts[i] == self.__Device.getModbusInterface().getSerialPort():
                            self.Interface_Choice.SetSelection(i)
                            break;
                    self.Adress_SpinCtrl.SetValue(self.__Device.getAdress())
                    self.TCPAdress_TextCtrl.SetValue('127.0.0.1')
                if modbusInterface.getMode() == 'TCP':
                    if len(self.getServerInformation().getSerialPorts()) > 0:
                        self.Interface_Choice.SetSelection(0)
                    self.Modbus_Choice.SetSelection(1)
                    self.Interface_Label.Hide()
                    self.Interface_Choice.Hide()
                    self.Adress_Label.Hide()
                    self.Adress_SpinCtrl.Hide()
                    self.adressAlreadyBeenTaken_Label.Hide()
                    if self.__Device.getModbusInterface().getTCPPort() == EsPeEs.Preferences.Modbus.DefaultPort:
                        self.TCPAdress_TextCtrl.SetValue(self.__Device.getModbusInterface().getTCPAdress())
                    else:
                        self.TCPAdress_TextCtrl.SetValue(self.__Device.getModbusInterface().getTCPAdress() + ':' + str(self.__Device.getModbusInterface().getTCPPort()))
                    self.TCPAdress_Label.Show()
                    self.TCPAdress_TextCtrl.Show()
                self.Layout()
                self.__checkEdit__()
            else:
                self.TCPAdress_TextCtrl.SetValue('127.0.0.1')
                self.TitleLabel.SetLabel('Add Modbus-device')
                self.applyButton.Hide()
                self.Modbus_Choice.SetSelection(0)
                if len(self.getServerInformation().getSerialPorts()) > 0:
                    self.Interface_Choice.SetSelection(0)
                    self.TCPAdress_TextCtrl.Hide()
                    self.TCPAdress_Label.Hide()
                    self.TCPError_Label.Hide()
                    self.adressAlreadyBeenTaken_Label.Hide()
                    self.Interface_Label.Show()
                    self.Interface_Choice.Show()
                    self.Adress_Label.Show()
                    self.Adress_SpinCtrl.Show()
                else:
                    self.Modbus_Choice.SetSelection(1)
                    self.Modbus_Choice.Disable()
                    self.TCPAdress_TextCtrl.Show()
                    self.TCPAdress_Label.Show()
                    self.TCPError_Label.Hide()
                    self.adressAlreadyBeenTaken_Label.Hide()
                    self.Interface_Label.Hide()
                    self.Interface_Choice.Hide()
                    self.Adress_Label.Hide()
                    self.Adress_SpinCtrl.Hide()
                self.Layout()
                self.__checkAdd__()
                
        if self.__DeviceType == 1:
            if self.__EditOrAdd == True:
                self.TitleLabel.SetLabel('Edit SPI-device')
                self.addButton.Hide()
                self.Adress_SpinCtrl.SetValue(self.__Device.getAdress())
                self.__checkEdit__()
            else:
                self.TitleLabel.SetLabel('Add SPI-device')                   
                self.applyButton.Hide()
                self.__checkAdd__()
            self.Interface_Label.Hide()
            self.Interface_Choice.Hide()
            self.Modbus_Label.Hide()
            self.Modbus_Choice.Hide()
            self.TCPAdress_TextCtrl.Hide()
            self.TCPError_Label.Hide()
            
        if self.__DeviceType == 2:
            if self.__EditOrAdd == True:
                self.TitleLabel.SetLabel('Edit I²C-device')
                self.addButton.Hide()
                self.Adress_SpinCtrl.SetValue(self.__Device.getSubAdress()) 
                self.__checkEdit__()
            else:
                self.TitleLabel.SetLabel('Add I²C-device')
                self.applyButton.Hide()
                self.__checkAdd__()
            self.Interface_Label.Hide()
            self.Interface_Choice.Hide()
            self.Modbus_Label.Hide()
            self.Modbus_Choice.Hide()
            self.TCPAdress_TextCtrl.Hide()
            self.TCPError_Label.Hide()
            
        #self.Layout()
        
    def showModbus(self, add = False, edit = False):
        if edit == True:
            self.__EditOrAdd = True
        if add == True:
            self.__EditOrAdd = False
        self.__DeviceType = 0
        serialPorts = self.getServerInformation().getSerialPorts()
        for i in range(len(serialPorts)):
            self.Interface_Choice.Append(serialPorts[i])
        self.Modbus_Choice.Append('RTU')
        self.Modbus_Choice.Append('TCP')
        self.Adress_SpinCtrl.SetRange(1, 255)
        self.__refresh__()
        
    def showSPI(self, add = False, edit = False):
        if edit == True:
            self.__EditOrAdd = True
        if add == True:
            self.__EditOrAdd = False
        self.__DeviceType = 1
        self.Adress_SpinCtrl.SetRange(1, 255)
        self.__refresh__()
        
    def showI2C(self, add = False, edit = False):
        if edit == True:
            self.__EditOrAdd = True
        if add == True:
            self.__EditOrAdd = False
        self.__DeviceType = 2
        self.Adress_SpinCtrl.SetRange(0, 8)
        if self.__Device.hasSubAdress() == False:
            self.Adress_Label.Hide()
            self.Adress_SpinCtrl.Hide()
        self.__refresh__()
        
    def __checkEdit__(self):
        ok = True
            
        if ((self.__Project.existDevice(self.Name_TextCtrl.GetValue()) == True) and not (self.__Device.getName() == self.Name_TextCtrl.GetValue())):
            self.nameAlreadyBeenTaken_Label.Show()
            ok = False
                
        if self.__DeviceType == 0:
            if (self.__Project.modbusAdressAlreadyAssigned(self.Interface_Choice.GetString(self.Interface_Choice.GetSelection()), self.Adress_SpinCtrl.GetValue()) == True) and not ((self.__Device.getModbusInterface().getSerialPort() == self.Interface_Choice.GetString(self.Interface_Choice.GetSelection())) and (self.__Device.getAdress() == self.Adress_SpinCtrl.GetValue())) and (self.Modbus_Choice.GetSelection() == 0):
                self.adressAlreadyBeenTaken_Label.Show()
                ok = False
                
        if (self.__Project.modbusTCPAdressAlreadyAssigned(EsPeEs.extractAdress(self.TCPAdress_TextCtrl.GetValue()), EsPeEs.extractPort(self.TCPAdress_TextCtrl.GetValue())) == True) and (self.Modbus_Choice.GetSelection() == 1):
            if not ((self.__Device.getModbusInterface().getTCPAdress() == EsPeEs.extractAdress(self.TCPAdress_TextCtrl.GetValue())) and (self.__Device.getModbusInterface().getTCPPort() == EsPeEs.extractPort(self.TCPAdress_TextCtrl.GetValue()))):
                self.TCPError_Label.SetLabel('Hostname already assigned.')
                self.TCPError_Label.Show()
                ok = False
                
        if EsPeEs.legalTCPAdress(self.TCPAdress_TextCtrl.GetValue()) == False:
            self.TCPError_Label.SetLabel('Illegal adress.')
            ok = False
            port = EsPeEs.extractPort(self.TCPAdress_TextCtrl.GetValue())
            if not (port == None):
                if EsPeEs.legalPort(port) == False:
                    self.TCPError_Label.SetLabel('Allowed port range: 49152 - 65535.')
            self.TCPError_Label.Show()
                
        if self.__DeviceType == 1:
            if (self.__Project.spiAdressAlreadyAssigned(self.Adress_SpinCtrl.GetValue()) == True) and not (self.__Device.getAdress() == self.Adress_SpinCtrl.GetValue()):
                self.adressAlreadyBeenTaken_Label.Show()
                ok = False
            else:
                self.adressAlreadyBeenTaken_Label.Hide()
                
        if self.__DeviceType == 2:
            if (self.__Project.i2cAdressAlreadyAssigned(self.Adress_SpinCtrl.GetValue()) == True) and not (self.__Device.getSubAdress() == self.Adress_SpinCtrl.GetValue()):
                self.adressAlreadyBeenTaken_Label.Show()
                ok = False
            else:
                self.adressAlreadyBeenTaken_Label.Hide()
                
        if ok == True:
            self.TCPError_Label.Hide()
            self.adressAlreadyBeenTaken_Label.Hide() 
            self.nameAlreadyBeenTaken_Label.Hide()
            self.addButton.Enable()
            self.applyButton.Enable()
        else:
            self.addButton.Disable()
            self.applyButton.Disable()
        return ok
        
    def __checkAdd__(self):
        ok = True
        if self.__Project.existDevice(self.Name_TextCtrl.GetValue()) == True:
            self.nameAlreadyBeenTaken_Label.Show()
            ok = False
        else:
            self.nameAlreadyBeenTaken_Label.Hide()
            
        if self.__DeviceType == 0:
            if (self.__Project.modbusAdressAlreadyAssigned(self.Interface_Choice.GetString(self.Interface_Choice.GetSelection()), self.Adress_SpinCtrl.GetValue()) == True)  and (self.Modbus_Choice.GetSelection() == 0):
                self.adressAlreadyBeenTaken_Label.Show()
                ok = False
            
            if (self.__Project.modbusTCPAdressAlreadyAssigned(EsPeEs.extractAdress(self.TCPAdress_TextCtrl.GetValue()), EsPeEs.extractPort(self.TCPAdress_TextCtrl.GetValue())) == True) and (self.Modbus_Choice.GetSelection() == 1):
                self.TCPError_Label.SetLabel('Hostname already assigned.')
                self.TCPError_Label.Show()
                ok = False
                
            if EsPeEs.legalTCPAdress(self.TCPAdress_TextCtrl.GetValue()) == False:
                self.TCPError_Label.SetLabel('Illegal adress.')
                ok = False
                port = EsPeEs.extractPort(self.TCPAdress_TextCtrl.GetValue())
                if not (port == None):
                    if EsPeEs.legalPort(port) == False:
                        self.TCPError_Label.SetLabel('Allowed port range: 49152 - 65535.')
                self.TCPError_Label.Show()
                
        if self.__DeviceType == 1:
            if self.__Project.spiAdressAlreadyAssigned(self.Adress_SpinCtrl.GetValue()) == True:
                self.adressAlreadyBeenTaken_Label.Show()
                ok = False
        
        if self.__DeviceType == 2:
            if self.__Project.i2cAdressAlreadyAssigned(self.Adress_SpinCtrl.GetValue()) == True:
                self.adressAlreadyBeenTaken_Label.Show()
                ok = False
        
        if ok == True:
            self.addButton.Enable()
            self.applyButton.Enable()
            self.TCPError_Label.Hide()
            self.nameAlreadyBeenTaken_Label.Hide()
            self.adressAlreadyBeenTaken_Label.Hide()  
        else:
            self.addButton.Disable()
            self.applyButton.Disable()
                    
        return ok
        
    def __check__(self):
        ok = False
        if self.__EditOrAdd == True:
            ok = self.__checkEdit__()
        else:
            ok = self.__checkAdd__()
        if EsPeEs.legalName(self.Name_TextCtrl.GetValue()) == False:
            self.illegalName_Label.Show()
            ok = False
        else:
            self.illegalName_Label.Hide()
        self.Layout()
        return ok

class AboutPanel(wx.Panel):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "AboutPanel")
        self.PostCreate(pre)

        self.Title = xrc.XRCCTRL(self, "Title")
        self.Bitmap = xrc.XRCCTRL(self, "Bitmap")
        self.Description = xrc.XRCCTRL(self, "Description")
        self.Website = xrc.XRCCTRL(self, "Website")
        
class DriverFrame(wx.Frame):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, trayIcon):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PreFrame()
        self.PreCreate(pre)
        get_resources().LoadOnFrame(pre, parent, "DriverFrame")
        self.PostCreate(pre)
        
        self.__TrayIcon = trayIcon
        self.__TrayIcon.setDriversMode()

        # Define variables for the controls, bind event handlers
        self.Menubar = self.GetMenuBar()
        idx = self.GetMenuBar().FindMenu("Save\\tCtrl+S")
        #print self.Menubar
        #print self.GetMenuBar().FindItemById(xrc.XRCID("FileMenu"))
        #if idx != wx.NOT_FOUND:
            #self.FileMenu = self.GetMenuBar().GetMenu(idx)
        #else:
            #self.FileMenu = self.GetMenuBar().FindItemById(xrc.XRCID("FileMenu")).GetSubMenu() 
        #self.SaveMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("SaveMenuItem"))
        #self.CloseMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("CloseMenuItem"))
        #self.QuitMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("QuitMenuItem"))
        #idx = self.GetMenuBar().FindMenu("Undo\\tCtrl+Z")
        #if idx != wx.NOT_FOUND:
            #self.EditMenu = self.GetMenuBar().GetMenu(idx)
        #else:
            #self.EditMenu = self.GetMenuBar().FindItemById(xrc.XRCID("EditMenu")).GetSubMenu()
        #self.UndoMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("UndoMenuItem"))
        #self.RedoMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("RedoMenuItem"))
        #self.CopyMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("CopyMenuItem"))
        #self.CutMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("CutMenuItem"))
        #self.PasteMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("PasteMenuItem"))
        #self.DeleteMenuItem = self.GetMenuBar().FindItemById(xrc.XRCID("DeleteMenuItem"))

        self.Bind(wx.EVT_MENU, self.OnMenu_SaveMenuItem, id=xrc.XRCID("SaveMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnMenu_CloseMenuItem, id=xrc.XRCID("CloseMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnMenu_QuitMenuItem, id=xrc.XRCID("QuitMenuItem"))
        #self.Bind(wx.EVT_MENU, self.OnMenu_FileMenu, id=xrc.XRCID("FileMenu"))
        self.Bind(wx.EVT_MENU, self.OnMenu_UndoMenuItem, id=xrc.XRCID("UndoMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnMenu_RedoMenuItem, id=xrc.XRCID("RedoMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnMenu_CopyMenuItem, id=xrc.XRCID("CopyMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnMenu_CutMenuItem, id=xrc.XRCID("CutMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnMenu_PasteMenuItem, id=xrc.XRCID("PasteMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnMenu_DeleteMenuItem, id=xrc.XRCID("DeleteMenuItem"))
        #self.Bind(wx.EVT_MENU, self.OnMenu_EditMenu, id=xrc.XRCID("EditMenu"))
        #self.Bind(wx.EVT_MENU, self.OnMenu_Menubar, self.Menubar)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.__Panel = DriverPanel(self)
        self.__Panel.Show()
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        self.SetMinSize((600, 500))
        self.SetSize((600,500))
        
    def OnMenu_SaveMenuItem(self, evt):
        self.__Panel.OnMenu_SaveMenuItem(evt)

    def OnMenu_CloseMenuItem(self, evt):
        self.__Panel.OnMenu_CloseMenuItem(evt)

    def OnMenu_QuitMenuItem(self, evt):
        self.OnClose(None)

    def OnMenu_UndoMenuItem(self, evt):
        self.__Panel.OnMenu_UndoMenuItem(evt)

    def OnMenu_RedoMenuItem(self, evt):
        self.__Panel.OnMenu_RedoMenuItem(evt)

    def OnMenu_CopyMenuItem(self, evt):
        self.__Panel.OnMenu_CopyMenuItem(evt)

    def OnMenu_CutMenuItem(self, evt):
        self.__Panel.OnMenu_CutMenuItem(evt)

    def OnMenu_PasteMenuItem(self, evt):
        self.__Panel.OnMenu_PasteMenuItem(evt)

    def OnMenu_DeleteMenuItem(self, evt):
        self.__Panel.OnMenu_DeleteMenuItem(evt)

    def OnClose(self, evt):
        if self.__Panel.getView() == 'DriverSelection':
            self.__TrayIcon.resetDriversMode()
            self.Destroy()
        if self.__Panel.getView() == 'DriverEditor':
            self.__Panel.OnMenu_CloseMenuItem(None)

class DriverPanel(wx.Panel):
    def PreCreate(self, pre):
        pass
        
    def __init__(self, parent):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "DriverPanel")
        self.PostCreate(pre)

        self.StartPanel = xrc.XRCCTRL(self, "StartPanel")
        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Choice = xrc.XRCCTRL(self, "Choice")
        self.TreeCtrl = xrc.XRCCTRL(self, "TreeCtrl")
        self.AddDirectoryButton = xrc.XRCCTRL(self, "AddDirectoryButton")
        self.AddButton = xrc.XRCCTRL(self, "AddButton")
        self.RemoveButton = xrc.XRCCTRL(self, "RemoveButton")
        self.EditButton = xrc.XRCCTRL(self, "EditButton")
        self.VariablesPanel = xrc.XRCCTRL(self, "VariablesPanel")
        self.VariableAddToolButton = xrc.XRCCTRL(self, "VariableAddToolButton")
        self.VariableRemoveToolButton = xrc.XRCCTRL(self, "VariableRemoveToolButton")
        self.VariableEditToolButton = xrc.XRCCTRL(self, "VariableEditToolButton")
        self.VariableStaticLine = xrc.XRCCTRL(self, "VariableStaticLine")
        self.VariableUpToolButton = xrc.XRCCTRL(self, "VariableUpToolButton")
        self.VariableDownToolButton = xrc.XRCCTRL(self, "VariableDownToolButton")
        self.VariableEditorPanel = xrc.XRCCTRL(self, "VariableEditorPanel")
        self.VariableNameLabel = xrc.XRCCTRL(self, "VariableNameLabel")
        self.VariableNameTextCtrl = xrc.XRCCTRL(self, "VariableNameTextCtrl")
        self.VariableStatusLabel = xrc.XRCCTRL(self, "VariableStatusLabel")
        self.VariableClassLabel = xrc.XRCCTRL(self, "VariableClassLabel")
        self.VariableClassChoice = xrc.XRCCTRL(self, "VariableClassChoice")
        self.VariableTypeLabel = xrc.XRCCTRL(self, "VariableTypeLabel")
        self.VariableTypeChoice = xrc.XRCCTRL(self, "VariableTypeChoice")
        self.VariableCancelButton = xrc.XRCCTRL(self, "VariableCancelButton")
        self.VariableEditButton = xrc.XRCCTRL(self, "VariableEditButton")
        self.VariableAddButton = xrc.XRCCTRL(self, "VariableAddButton")
        self.VariablesGrid = xrc.XRCCTRL(self, "VariablesGrid")
        self.StaticLine = xrc.XRCCTRL(self, "StaticLine")
        self.CppEditorPanel = xrc.XRCCTRL(self, "CppEditorPanel")
        
        self.CppEditorSizer = wx.BoxSizer(wx.VERTICAL)
        self.CppEditor = CppEditor(self.CppEditorPanel)
        self.CppEditorSizer.Add(self.CppEditor, 1, wx.EXPAND)
        self.CppEditorPanel.SetSizer(self.CppEditorSizer)
        self.CppEditorPanel.Layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoice_Choice, self.Choice)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTree_sel_changed_TreeCtrl, self.TreeCtrl)
        self.Bind(wx.EVT_BUTTON, self.OnButton_AddDirectoryButton, self.AddDirectoryButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_AddButton, self.AddButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_RemoveButton, self.RemoveButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_EditButton, self.EditButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_VariableAddToolButton, self.VariableAddToolButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_VariableRemoveToolButton, self.VariableRemoveToolButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_VariableEditToolButton, self.VariableEditToolButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_VariableUpToolButton, self.VariableUpToolButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_VariableDownToolButton, self.VariableDownToolButton)
        self.Bind(wx.EVT_TEXT, self.OnText_VariableNameTextCtrl, self.VariableNameTextCtrl)
        self.Bind(wx.EVT_CHOICE, self.OnChoice_VariableClassChoice, self.VariableClassChoice)
        self.Bind(wx.EVT_CHOICE, self.OnChoice_VariableTypeChoice, self.VariableTypeChoice)
        self.Bind(wx.EVT_BUTTON, self.OnButton_VariableCancelButton, self.VariableCancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_VariableEditButton, self.VariableEditButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_VariableAddButton, self.VariableAddButton)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGrid_cell_left_click_VariablesGrid, self.VariablesGrid)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnGrid_cell_left_dclick_VariablesGrid, self.VariablesGrid)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnGrid_label_left_click_VariablesGrid, self.VariablesGrid)
           
        self.Choice.Append('Programmable logic controllers')
        self.Choice.Append('Modbus modules')
        self.Choice.Append('SPI modules')
        self.Choice.Append('I2C modules')
        self.Choice.Append('Raspberry Pi modules')
        self.Choice.SetSelection(0)
        
        self.__ImageList = wx.ImageList(24,24)
        self.__ModuleImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'module_24.png', type=wx.BITMAP_TYPE_PNG))
        self.__DirectoryImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'folder_24.png', type=wx.BITMAP_TYPE_PNG))
        self.__DriverImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'driver_24.png', type=wx.BITMAP_TYPE_PNG))
        self.__CFileImage = self.__ImageList.Add(wx.Bitmap('GUIs' + os.sep + 'Icons' + os.sep + 'cfile_24.png', type=wx.BITMAP_TYPE_PNG))
        self.TreeCtrl.SetImageList(self.__ImageList)
        
        self.VariableStaticLine.Hide()
        self.VariableUpToolButton.Hide()
        self.VariableDownToolButton.Hide()
        self.VariablesPanel.SetMinSize((-1, self.VariableEditorPanel.GetSize()[1]))
        self.VariablesPanel.Hide()
        self.StaticLine.Hide()
        self.CppEditorPanel.Hide()
        self.StartPanel.Show()
        self.__refeshStartPanelTreeCtrl__()
        
        self.TreeCtrl.ExpandAll()
        
        classTypes = EsPeEs.MemoryTypes.get()
        for ct in classTypes:
            self.VariableClassChoice.Append(ct)
            
        dataTypes = EsPeEs.DataTypes.get()
        for dt in dataTypes:
            self.VariableTypeChoice.Append(dt)
            
        self.VariablesGrid.CreateGrid(0, 3)
        self.VariablesGrid.SetColLabelValue(0, "Name")
        self.VariablesGrid.SetColLabelValue(1, "Type")
        self.VariablesGrid.SetColLabelValue(2, "Class")
        self.VariablesGrid.SetColSize(0, 100)
        self.VariablesGrid.SetColSize(1, 100)
        self.VariablesGrid.SetColSize(2, 100)
        self.VariablesGrid.SetRowLabelSize(0)
        self.VariablesGrid.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)
        
        self.__View = 'DriverSelection'
        
        self.__Row = -1
        self.__Col = -1
        self.__CFile = None
        self.__Driver = None
        self.__Path = None
        self.__Name = None
        self.__OldVariableName = None

        self.__VariableAddToolButtonState = True
        self.__VariableEditToolButtonState = False
        self.__VariableRemoveToolButtonnState = False

        self.GetParent().Fit()
        
    def __refreshVariablesGrid__(self):
        if not (self.__CFile == None) and not (self.__Driver == None):
            variables = self.__CFile.getVariables()
            if not (self.VariablesGrid.GetNumberRows() == 0):
                self.VariablesGrid.DeleteRows(pos = 0, numRows = self.VariablesGrid.GetNumberRows())
            self.VariablesGrid.ForceRefresh()
            self.VariablesGrid.AppendRows(len(variables))
                            
            for i in range(len(variables)):
                self.VariablesGrid.SetCellValue(i, 0, variables[i].getName())
                self.VariablesGrid.SetCellValue(i, 1, variables[i].getDataType())
                self.VariablesGrid.SetCellValue(i, 2, variables[i].getMemoryType())
            
            self.VariableRemoveToolButton.Disable()
            self.VariableEditToolButton.Disable()
                
            self.VariablesGrid.ForceRefresh()
                
    def __refeshStartPanelTreeCtrl__(self):
        self.TreeCtrl.DeleteAllItems()
        if self.Choice.GetSelection() == 0:
            self.__RootItem = self.TreeCtrl.AddRoot('Programmable logic controllers', self.__ModuleImage)
            self.__appendChildsToStartPanelTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.TargetDevice)
            
        if self.Choice.GetSelection() == 1:
            self.__RootItem = self.TreeCtrl.AddRoot('Modbus modules', self.__ModuleImage)
            self.__appendChildsToStartPanelTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.ModbusDevice)
            
        if self.Choice.GetSelection() == 2:
            self.__RootItem = self.TreeCtrl.AddRoot('SPI modules', self.__ModuleImage)
            self.__appendChildsToStartPanelTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.SPIDevice)
            
        if self.Choice.GetSelection() == 3:
            self.__RootItem = self.TreeCtrl.AddRoot('I2C modules', self.__ModuleImage)
            self.__appendChildsToStartPanelTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.I2CDevice)
            
        if self.Choice.GetSelection() == 4:
            self.__RootItem = self.TreeCtrl.AddRoot('Raspberry Pi modules', self.__ModuleImage)
            self.__appendChildsToStartPanelTreeCtrl__(self.__RootItem, range(0, 0), EsPeEs.CExtension.Type.Shield)
        self.TreeCtrl.SelectItem(self.__RootItem)
        self.OnTree_sel_changed_TreeCtrl(None)
                    
    def __appendChildsToStartPanelTreeCtrl__(self, parentTreeItem, path, cextensionType):
        childs = sorted(EsPeEs.DriverManager.Instance().listChilds(path, cextensionType))
        for i in range(len(childs)):
            childPath = EsPeEs.DriverManager.Instance().joinPath(path, childs[i])
            childEntryType = EsPeEs.DriverManager.Instance().getEntryType(childPath, cextensionType)
            if childEntryType == 'Directory':
                image = self.__DirectoryImage
            if childEntryType == 'Driver':
                image = self.__DriverImage
            if childEntryType == 'CFile':
                image = self.__CFileImage
            treeItem = self.TreeCtrl.AppendItem(parentTreeItem, childs[i], image)
            if EsPeEs.DriverManager.Instance().hasChilds(childPath, cextensionType) == True:
                self.__appendChildsToStartPanelTreeCtrl__(treeItem, childPath, cextensionType)
                               
    def __getCExtensionType__(self):
        cextensionType = None
        if self.Choice.GetSelection() == 0:
            cextensionType = EsPeEs.CExtension.Type.TargetDevice
        if self.Choice.GetSelection() == 1:
            cextensionType = EsPeEs.CExtension.Type.ModbusDevice
        if self.Choice.GetSelection() == 2:
            cextensionType = EsPeEs.CExtension.Type.SPIDevice
        if self.Choice.GetSelection() == 3:
            cextensionType = EsPeEs.CExtension.Type.I2CDevice
        if self.Choice.GetSelection() == 4:
            cextensionType = EsPeEs.CExtension.Type.Shield
        return cextensionType

    def __getPath__(self):
        treeItem = self.TreeCtrl.GetSelection()
        #self.TreeCtrl.GetItemText(treeItem)
        path = range(0, 0)
        if treeItem == self.__RootItem:
            return path
        else:
            return self.__getPathRecursive__(path, treeItem)
            
    def __getPathRecursive__(self, path, treeItem):
        parentItem = self.TreeCtrl.GetItemParent(treeItem)
        if parentItem == self.__RootItem:
            newPath = range(0, 0)
            newPath.append(self.TreeCtrl.GetItemText(treeItem))
            for i in range(len(path)):
                newPath.append(path[i])
            return newPath
        else:
            newPath = range(0, 0)
            newPath.append(self.TreeCtrl.GetItemText(treeItem))
            for i in range(len(path)):
                newPath.append(path[i])
            return self.__getPathRecursive__(newPath, parentItem)

    def OnChoice_Choice(self, evt):
        self.__refeshStartPanelTreeCtrl__()
        self.TreeCtrl.ExpandAll()

    def OnTree_sel_changed_TreeCtrl(self, evt):
        path = self.__getPath__()
        entryType = EsPeEs.DriverManager.Instance().getEntryType(path, self.__getCExtensionType__()) 
        if entryType == 'Directory':
            self.AddDirectoryButton.Enable()
            self.AddButton.Enable()
            self.EditButton.Enable()
            self.RemoveButton.Enable()
                
        if entryType == 'Driver':
            self.AddDirectoryButton.Disable()
            if self.__getCExtensionType__() == EsPeEs.CExtension.Type.TargetDevice:
                self.AddButton.Disable()
            else:
                self.AddButton.Enable()
            self.EditButton.Enable()
            self.RemoveButton.Enable()
            
        if entryType == 'CFile':
            self.AddDirectoryButton.Disable()
            if self.__getCExtensionType__() == EsPeEs.CExtension.Type.TargetDevice:
                self.AddButton.Disable()
            else:
                self.AddButton.Enable()
            self.EditButton.Enable()
            self.RemoveButton.Enable()
            
        if len(path) == 0:
            self.RemoveButton.Disable()
            self.EditButton.Disable()

    def OnButton_AddDirectoryButton(self, evt):
        path = self.__getPath__()
        cextensionType = self.__getCExtensionType__()
        dlg = DriverAddDirectoryDialog(self, path, cextensionType)
        dlg.ShowModal()
        if dlg.GetReturnCode() == 1:
            newPath = path
            newPath.append(dlg.getName())
            EsPeEs.DriverManager.Instance().createDirectory(newPath, cextensionType)
            treeItem = self.TreeCtrl.AppendItem(self.TreeCtrl.GetSelection(), dlg.getName(), self.__DirectoryImage)
            self.TreeCtrl.SortChildren(self.TreeCtrl.GetItemParent(treeItem))
            self.TreeCtrl.SelectItem(treeItem, True)

    def OnButton_AddButton(self, evt):
        path = self.__getPath__()
        cextensionType = self.__getCExtensionType__()
        entryType = EsPeEs.DriverManager.Instance().getEntryType(path, cextensionType)
        if (entryType == 'Directory') or (entryType == 'NotExist'):
            dlg = DriverAddDriverDialog(self, path, cextensionType)
            dlg.ShowModal()
            if dlg.GetReturnCode() == 1:
                newPath = path
                newPath.append(dlg.getName())
                EsPeEs.DriverManager.Instance().createDriver(newPath, cextensionType, registers = dlg.getRegisters(), isModbusCompatible = dlg.isModbusCompatible(), isSPICompatible = dlg.isSPICompatible(), isI2CCompatible = dlg.isI2CCompatible(), adress = dlg.getI2CAdress(), hasTenBitAdress = dlg.hasTenBitAdress(), hasSubAdress = dlg.hasSubAdress(), target = dlg.getTarget(), libraries = dlg.getLibraries())
                treeItem = self.TreeCtrl.AppendItem(self.TreeCtrl.GetSelection(), dlg.getName(), self.__DriverImage)
                self.TreeCtrl.SortChildren(self.TreeCtrl.GetItemParent(treeItem))
                if cextensionType == EsPeEs.CExtension.Type.TargetDevice:
                    newPath.append('Code')
                    EsPeEs.DriverManager.Instance().createCFile(newPath, cextensionType)
                    treeItem2 = self.TreeCtrl.AppendItem(treeItem, 'Code', self.__CFileImage)
                    self.TreeCtrl.SortChildren(self.TreeCtrl.GetItemParent(treeItem2))
                    self.TreeCtrl.SelectItem(treeItem2, True)
                else:
                    self.TreeCtrl.SelectItem(treeItem, True)
                    
        if entryType == 'Driver':
            dlg = DriverAddCFileDialog(self, path, cextensionType)
            dlg.ShowModal()
            if dlg.GetReturnCode() == 1:
                newPath = path
                newPath.append(dlg.getName())
                EsPeEs.DriverManager.Instance().createCFile(newPath, cextensionType)
                treeItem = self.TreeCtrl.AppendItem(self.TreeCtrl.GetSelection(), dlg.getName(), self.__CFileImage)
                self.TreeCtrl.SortChildren(self.TreeCtrl.GetItemParent(treeItem))
                self.TreeCtrl.SelectItem(treeItem, True)
        if entryType == 'CFile':
            del path[len(path) - 1]
            dlg = DriverAddCFileDialog(self, path, cextensionType)
            dlg.ShowModal()
            if dlg.GetReturnCode() == 1:
                newPath = path
                newPath.append(dlg.getName())
                EsPeEs.DriverManager.Instance().createCFile(newPath, cextensionType)
                treeItem = self.TreeCtrl.AppendItem(self.TreeCtrl.GetItemParent(self.TreeCtrl.GetSelection()), dlg.getName(), self.__CFileImage)
                self.TreeCtrl.SortChildren(self.TreeCtrl.GetItemParent(treeItem))
                self.TreeCtrl.SelectItem(treeItem, True)

    def OnButton_RemoveButton(self, evt):
        path = self.__getPath__()
        cextensionType = self.__getCExtensionType__()
        if len(path) > 0:
            entryType = EsPeEs.DriverManager.Instance().getEntryType(path, cextensionType)
            if entryType == 'Directory':
                dlg = DriverRemoveDialog(self, path, cextensionType, entryType)
                dlg.ShowModal()
                if dlg.GetReturnCode() == 1:
                    EsPeEs.DriverManager.Instance().removeDirectory(path, cextensionType)
                    treeItem = self.TreeCtrl.GetSelection()
                    self.TreeCtrl.Delete(treeItem)
                
            if entryType == 'Driver':
                dlg = DriverRemoveDialog(self, path, cextensionType, entryType)
                dlg.ShowModal()
                if dlg.GetReturnCode() == 1:
                    EsPeEs.DriverManager.Instance().removeDriver(path, cextensionType)
                    treeItem = self.TreeCtrl.GetSelection()
                    self.TreeCtrl.Delete(treeItem)
                
            if entryType == 'CFile':
                if cextensionType == EsPeEs.CExtension.Type.TargetDevice:
                    del path[len(path) - 1]
                    dlg = DriverRemoveDialog(self, path, cextensionType, 'Driver')
                    dlg.ShowModal()
                    if dlg.GetReturnCode() == 1:
                        EsPeEs.DriverManager.Instance().removeDriver(path, cextensionType)
                        treeItem = self.TreeCtrl.GetSelection()
                        parentItem = self.TreeCtrl.GetItemParent(treeItem)
                        self.TreeCtrl.Delete(treeItem)
                        self.TreeCtrl.Delete(parentItem)
                else:
                    dlg = DriverRemoveDialog(self, path, cextensionType, entryType)
                    dlg.ShowModal()
                    if dlg.GetReturnCode() == 1:
                        EsPeEs.DriverManager.Instance().removeCFile(path, cextensionType)
                        treeItem = self.TreeCtrl.GetSelection()
                        self.TreeCtrl.Delete(treeItem)

    def OnButton_EditButton(self, evt):
        path = self.__getPath__()
        if len(path) > 0:
            newPath = EsPeEs.DriverManager.Instance().removePath(path)
            name = path[len(path) - 1]
            cextensionType = self.__getCExtensionType__()
            entryType = EsPeEs.DriverManager.Instance().getEntryType(path, cextensionType)
            if entryType == 'Directory':
                dlg = DriverEditDirectoryDialog(self, path, cextensionType)
                dlg.ShowModal()
                if dlg.GetReturnCode() == 1:
                    EsPeEs.DriverManager.Instance().renameDirectory(dlg.getName(), path, cextensionType)
                    treeItem = self.TreeCtrl.GetSelection()
                    self.TreeCtrl.SetItemText(treeItem, dlg.getName())
                    self.TreeCtrl.SortChildren(self.TreeCtrl.GetItemParent(treeItem))
                    self.TreeCtrl.SelectItem(treeItem, True)
            if entryType == 'Driver':
                drv = EsPeEs.DriverManager.Instance().getDriver(path, cextensionType)
                registers = None
                isModbusCompatible = None
                isSPICompatible = None
                isI2CCompatible = None
                hasTenBitAdress = None
                hasSubAdress = None
                i2cAdress = None
                target = None
                libraries = None
                if cextensionType == EsPeEs.CExtension.Type.ModbusDevice:
                    registers = drv.getRegisters()
                if cextensionType == EsPeEs.CExtension.Type.Shield:
                    isModbusCompatible = drv.isModbusCompatible()
                    isSPICompatible = drv.isSPICompatible()
                    isI2CCompatible = drv.isI2CCompatible()
                if cextensionType == EsPeEs.CExtension.Type.I2CDevice:
                    hasTenBitAdress = drv.hasTenBitAdress()
                    hasSubAdress = drv.hasSubAdress()
                    i2cAdress = drv.getAdress()
                if cextensionType == EsPeEs.CExtension.Type.TargetDevice:
                    target = drv.getTarget()
                    libraries = drv.getLibraries()
                    isModbusCompatible = drv.isModbusCompatible()
                    isSPICompatible = drv.isSPICompatible()
                    isI2CCompatible = drv.isI2CCompatible()
                dlg = DriverEditDriverDialog(self, path, cextensionType, registers = registers, isModbusCompatible = isModbusCompatible, isSPICompatible = isSPICompatible, isI2CCompatible = isI2CCompatible, i2cAdress = i2cAdress, hasTenBitAdress = hasTenBitAdress, hasSubAdress = hasSubAdress, target = target, libraries = libraries)
                dlg.ShowModal()
                if dlg.GetReturnCode() == 1:
                    if cextensionType == EsPeEs.CExtension.Type.ModbusDevice:
                        drv.setRegisters(dlg.getRegisters())
                    if cextensionType == EsPeEs.CExtension.Type.Shield:
                        drv.setModbusCompability(dlg.isModbusCompatible())
                        drv.setSPICompability(dlg.isSPICompatible())
                        drv.setI2CCompability(dlg.isI2CCompatible())
                    if cextensionType == EsPeEs.CExtension.Type.I2CDevice:
                        drv.setAdress(dlg.getI2CAdress())
                        drv.setHasTenBitAdress(dlg.hasTenBitAdress())
                        drv.setHasSubAdress(dlg.hasSubAdress())
                    if cextensionType == EsPeEs.CExtension.Type.TargetDevice:
                        drv.setModbusCompability(dlg.isModbusCompatible())
                        drv.setSPICompability(dlg.isSPICompatible())
                        drv.setI2CCompability(dlg.isI2CCompatible())
                        drv.setTarget(dlg.getTarget())
                        drv.setLibraries(dlg.getLibraries())
                    EsPeEs.DriverManager.Instance().setDriver(EsPeEs.DriverManager.Instance().joinPath(newPath, dlg.getName()), drv)
                    treeItem = self.TreeCtrl.GetSelection()
                    self.TreeCtrl.SetItemText(treeItem, dlg.getName())
                    self.TreeCtrl.SortChildren(self.TreeCtrl.GetItemParent(treeItem))
                    self.TreeCtrl.SelectItem(treeItem, True)
            if entryType == 'CFile':
                self.__Name = path[len(path) - 1]
                self.__Path = newPath
                self.__Driver = EsPeEs.DriverManager.Instance().getDriver(newPath, cextensionType)
                self.__CFile = self.__Driver.getCFile(self.__Name)
                self.CppEditor.setCode(self.__Driver, self.__CFile)
                self.StartPanel.Hide()
                self.VariablesPanel.Show()
                self.StaticLine.Show()
                self.CppEditorPanel.Show()
                self.VariableEditorPanel.Hide()
                self.Layout()
                self.__refreshVariablesGrid__()
                self.__View = 'DriverEditor'

    def OnButton_VariableAddToolButton(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            self.__Mode = 'Add'
            self.__disableVariableToolButtons__()
            self.VariablesGrid.Disable()
            self.VariableEditButton.Hide()
            self.VariableAddButton.Show()
            self.VariableTypeChoice.SetSelection(0)
            self.VariableClassChoice.SetSelection(2)
            self.VariableNameTextCtrl.SetValue('')
            self.VariableNameTextCtrl.SetFocus()
            self.VariableEditorPanel.Show()
            self.VariableEditorPanel.Layout()
            self.VariablesPanel.Layout()
            self.Layout()

    def OnButton_VariableRemoveToolButton(self, evt):
        if not (self.__CFile == None):
            self.__CFile.removeVariable(index = self.__Row)
            self.__refreshVariablesGrid__()
            self.__VariableAddToolButtonState = True
            self.__VariableEditToolButtonState = False
            self.__VariableRemoveToolButtonnState = False
            self.__enableVariableToolButtons__()

    def OnButton_VariableEditToolButton(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            self.__Mode = 'Edit'
            self.__disableVariableToolButtons__()
            self.__TempVariable = self.__CFile.getVariable(index = self.__Row)
            self.VariableNameTextCtrl.SetValue(self.__TempVariable.getName())
            self.VariablesGrid.Disable()
            self.VariableEditorPanel.Show()
            self.VariableEditButton.Show()
            self.VariableAddButton.Hide()
            self.VariableTypeChoice.SetStringSelection(self.__TempVariable.getDataType())
            self.VariableClassChoice.SetStringSelection(self.__TempVariable.getMemoryType())
            self.VariableNameTextCtrl.SetFocus()
            self.VariableEditorPanel.Layout()
            self.VariablesPanel.Layout()
            self.Layout()

    def OnButton_VariableUpToolButton(self, evt):
        pass
                
    def OnButton_VariableDownToolButton(self, evt):
        pass

    def OnText_VariableNameTextCtrl(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            ok = True
            name = self.VariableNameTextCtrl.GetValue()
            
            if EsPeEs.legalName(name) == False:
                self.VariableStatusLabel.SetLabel('Illegal name.')
                self.VariableStatusLabel.Show()
                ok = False
            
            if name == '':
                self.VariableStatusLabel.SetLabel('Enter a name.')
                self.VariableStatusLabel.Show()
                ok = False
                
            if self.__Driver.getType() == EsPeEs.CExtension.Type.ModbusDevice:
                if (self.__CFile.existVariable(name) == True or self.__Driver.existRegister(name)):
                    self.VariableStatusLabel.SetLabel('Name already exist.')
                    self.VariableStatusLabel.Show()
                    ok = False
                
            if self.__Driver.getType() == EsPeEs.CExtension.Type.SPIDevice:
                if self.__CFile.existVariable(name) == True:
                    self.VariableStatusLabel.SetLabel('Name already exist.')
                    self.VariableStatusLabel.Show()
                    ok = False
                
            if self.__Driver.getType() == EsPeEs.CExtension.Type.Shield:
                if self.__CFile.existVariable(name) == True:
                    self.VariableStatusLabel.SetLabel('Name already exist.')
                    self.VariableStatusLabel.Show()
                    ok = False
                    
            if self.__Mode == 'Edit':
                if self.__TempVariable.getName() == name:
                    self.VariableStatusLabel.Hide()
                    ok = True
                    
            if ok == True:
                self.VariableStatusLabel.Hide()
                self.VariableAddButton.Enable()
                self.VariableEditButton.Enable()
            else:
                self.VariableAddButton.Disable()
                self.VariableEditButton.Disable()
                
            self.Layout()

    def OnChoice_VariableClassChoice(self, evt):
        pass

    def OnChoice_VariableTypeChoice(self, evt):
        pass

    def OnButton_VariableCancelButton(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            self.VariableEditorPanel.Hide()
            self.VariablesGrid.Enable()
            self.__enableVariableToolButtons__()
            self.VariablesPanel.Layout()
            self.Layout()

    def OnButton_VariableEditButton(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            newName = self.VariableNameTextCtrl.GetValue()
            memoryType = self.VariableClassChoice.GetString(self.VariableClassChoice.GetSelection())
            dataType = self.VariableTypeChoice.GetString(self.VariableTypeChoice.GetSelection())
            self.__CFile.editVariable(name = self.__TempVariable.getName(), newName = newName, dataType = dataType, memoryType = memoryType)
            self.VariableEditorPanel.Hide()
            self.VariablesGrid.Enable()
            self.__refreshVariablesGrid__()
            self.__Row = self.__CFile.getVariableIndex(newName)
            self.VariablesGrid.SelectRow(self.__Row)
            self.__VariableAddToolButtonState = True
            self.__VariableEditToolButtonState = True
            self.__VariableRemoveToolButtonnState = True
            self.__enableVariableToolButtons__()
            self.VariablesPanel.Layout()
            self.Layout()

    def OnButton_VariableAddButton(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            name = self.VariableNameTextCtrl.GetValue()
            memoryType = self.VariableClassChoice.GetString(self.VariableClassChoice.GetSelection())
            dataType = self.VariableTypeChoice.GetString(self.VariableTypeChoice.GetSelection())
            self.__CFile.addVariable(name = name, dataType = dataType, memoryType = memoryType)
            self.VariableEditorPanel.Hide()
            self.VariablesGrid.Enable()
            self.__refreshVariablesGrid__()
            row = self.__CFile.getVariableIndex(name)
            self.VariablesGrid.SelectRow(row)
            self.__Row = row
            self.__VariableAddToolButtonState = True
            self.__VariableEditToolButtonState = True
            self.__VariableRemoveToolButtonnState = True
            self.__enableVariableToolButtons__()
            self.VariablesPanel.Layout()
            self.Layout()
            
    def OnGrid_cell_left_click_VariablesGrid(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            self.__Row = evt.GetRow()
            self.__Col = evt.GetCol()
            self.VariablesGrid.ClearSelection()
            self.VariablesGrid.SetGridCursor(self.__Row, self.__Col)
            self.VariablesGrid.SelectRow(self.__Row)
            self.VariablesGrid.EnableEditing(False)
            if not (self.__Row == -1):
                self.__VariableAddToolButtonState = True
                self.__VariableEditToolButtonState = True
                self.__VariableRemoveToolButtonnState = True
            else:
                self.__VariableAddToolButtonState = True
                self.__VariableEditToolButtonState = False
                self.__VariableRemoveToolButtonnState = False
            self.__enableVariableToolButtons__()
        
    def OnGrid_cell_left_dclick_VariablesGrid(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            self.__Row = evt.GetRow()
            self.__Col = evt.GetCol()
            self.OnButton_VariableEditToolButton(None)
    
    def OnGrid_label_left_click_VariablesGrid(self, evt):
        pass
      
    def OnMenu_SaveMenuItem(self, evt):
        if not (self.__Driver == None) and not (self.__Path == None) and not(self.__CFile == None):
            self.__Driver.setCFile(name = self.__Name, cfile = self.__CFile)
            EsPeEs.DriverManager.Instance().setDriver(self.__Path, self.__Driver)

    def OnMenu_CloseMenuItem(self, evt):
        if not (self.__CFile == None) and not (self.__Driver == None):
            self.__Driver = None
            self.__CFile = None
            self.__Row = -1
            self.__Col = -1
            self.__Path = None
            self.__Name = None
            self.VariableEditorPanel.Hide()
            self.VariablesGrid.Enable()
            self.StartPanel.Show()
            self.VariablesPanel.Hide()
            self.StaticLine.Hide()
            self.CppEditorPanel.Hide()
            self.VariableEditorPanel.Hide()
            self.Layout()
            self.__View = 'DriverSelection'

    def OnMenu_UndoMenuItem(self, evt):
        if not (self.__Driver == None) and not (self.__Path == None) and not(self.__CFile == None):
            if self.CppEditor.CanUndo():
                self.CppEditor.Undo()

    def OnMenu_RedoMenuItem(self, evt):
        if not (self.__Driver == None) and not (self.__Path == None) and not(self.__CFile == None):
            if self.CppEditor.CanRedo():
                self.CppEditor.Redo()

    def OnMenu_CopyMenuItem(self, evt):
        if not (self.__Driver == None) and not (self.__Path == None) and not(self.__CFile == None):
            self.CppEditor.Copy()

    def OnMenu_CutMenuItem(self, evt):
        if not (self.__Driver == None) and not (self.__Path == None) and not(self.__CFile == None):
            self.CppEditor.Cut()

    def OnMenu_PasteMenuItem(self, evt):
        if not (self.__Driver == None) and not (self.__Path == None) and not(self.__CFile == None):
            if self.CppEditor.CanPaste():
                self.CppEditor.Paste()

    def OnMenu_DeleteMenuItem(self, evt):
        if not (self.__Driver == None) and not (self.__Path == None) and not(self.__CFile == None):
            self.CppEditor.DeleteBack()
        
    def getView(self):
        return self.__View
        
    def __disableVariableToolButtons__(self):
        self.VariableAddToolButton.Disable()
        self.VariableEditToolButton.Disable()
        self.VariableRemoveToolButton.Disable()
        
    def __enableVariableToolButtons__(self):
        self.VariableAddToolButton.Enable(self.__VariableAddToolButtonState)
        self.VariableEditToolButton.Enable(self.__VariableEditToolButtonState)
        self.VariableRemoveToolButton.Enable(self.__VariableRemoveToolButtonnState)

class DriverAddDriverDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DriverAddDriverDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.__Panel = DriverAddDriverPanel(self, path, cextensionType)
        self.__Panel.Show()
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
    def getName(self):
        return self.__Panel.getName()
        
    def getRegisters(self):
        return self.__Panel.getRegisters()
        
    def getI2CAdress(self):
        return self.__Panel.getI2CAdress()
        
    def hasTenBitAdress(self):
        return self.__Panel.hasTenBitAdress()
        
    def hasSubAdress(self):
        return self.__Panel.hasSubAdress()
        
    def isModbusCompatible(self):
        return self.__Panel.isModbusCompatible()
        
    def isSPICompatible(self):
        return self.__Panel.isSPICompatible()
        
    def isI2CCompatible(self):
        return self.__Panel.isI2CCompatible()
        
    def getTarget(self):
        return self.__Panel.getTarget()
        
    def getLibraries(self):
        return self.__Panel.getLibraries()

    def OnClose(self, evt):
        self.EndModal(0)

class DriverAddDriverPanel(wx.Panel):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "DriverAddDriverPanel")
        self.PostCreate(pre)
        self.__Register = EsPeEs.Register()

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Name_Label = xrc.XRCCTRL(self, "Name_Label")
        self.Name_TextCtrl = xrc.XRCCTRL(self, "Name_TextCtrl")
        self.nameAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "nameAlreadyBeenTaken_Label")
        self.illegalName_Label = xrc.XRCCTRL(self, "illegalName_Label")
        self.ModbusPanel = xrc.XRCCTRL(self, "ModbusPanel")
        self.ModbusFirstStaticline = xrc.XRCCTRL(self, "ModbusFirstStaticline")
        self.ModbusRegisterLabel = xrc.XRCCTRL(self, "ModbusRegisterLabel")
        self.ModbusRegisterListBox = xrc.XRCCTRL(self, "ModbusRegisterListBox")
        self.ModbusRegisterAddButton = xrc.XRCCTRL(self, "ModbusRegisterAddButton")
        self.ModbusRegisterRemoveButton = xrc.XRCCTRL(self, "ModbusRegisterRemoveButton")
        self.ModbusRegisterEditButton = xrc.XRCCTRL(self, "ModbusRegisterEditButton")
        self.ModbusRegisterButtonStaticLine = xrc.XRCCTRL(self, "ModbusRegisterButtonStaticLine")
        self.ModbusRegisterUpButton = xrc.XRCCTRL(self, "ModbusRegisterUpButton")
        self.ModbusRegisterDownButton = xrc.XRCCTRL(self, "ModbusRegisterDownButton")
        self.ModbusLastStaticline = xrc.XRCCTRL(self, "ModbusLastStaticline")
        self.ShieldPanel = xrc.XRCCTRL(self, "ShieldPanel")
        self.ShieldFirstStaticLine = xrc.XRCCTRL(self, "ShieldFirstStaticLine")
        self.ShieldHasSupportForLabel = xrc.XRCCTRL(self, "ShieldHasSupportForLabel")
        self.ShieldSupportsModbusCheckBox = xrc.XRCCTRL(self, "ShieldSupportsModbusCheckBox")
        self.ShieldSupportsSPICheckBox = xrc.XRCCTRL(self, "ShieldSupportsSPICheckBox")
        self.ShieldSupportsI2CCheckBox = xrc.XRCCTRL(self, "ShieldSupportsI2CCheckBox")
        self.ShieldLastStaticLine = xrc.XRCCTRL(self, "ShieldLastStaticLine")
        self.I2CPanel = xrc.XRCCTRL(self, "I2CPanel")
        self.I2CFirstStaticLine = xrc.XRCCTRL(self, "I2CFirstStaticLine")
        self.I2CAdressLabel = xrc.XRCCTRL(self, "I2CAdressLabel")
        self.I2CAdressSpinCtrl = xrc.XRCCTRL(self, "I2CAdressSpinCtrl")
        self.I2CHasCheckBox = xrc.XRCCTRL(self, "I2CHasCheckBox")
        self.I2CHasSubAdressCheckBox = xrc.XRCCTRL(self, "I2CHasSubAdressCheckBox")
        self.I2CLastStaticLine = xrc.XRCCTRL(self, "I2CLastStaticLine")
        self.TargetPanel = xrc.XRCCTRL(self, "TargetPanel")
        self.TargetFirstStaticLine = xrc.XRCCTRL(self, "TargetFirstStaticLine")
        self.TargetPlatformLabel = xrc.XRCCTRL(self, "TargetPlatformLabel")
        self.TargetChoice = xrc.XRCCTRL(self, "TargetChoice")
        self.TargetSecondStaticLine = xrc.XRCCTRL(self, "TargetSecondStaticLine")
        self.TargetHasSupportForLabel = xrc.XRCCTRL(self, "TargetHasSupportForLabel")
        self.TargetSupportsModbusCheckBox = xrc.XRCCTRL(self, "TargetSupportsModbusCheckBox")
        self.TargetSupportsSPICheckBox = xrc.XRCCTRL(self, "TargetSupportsSPICheckBox")
        self.TargetSupportsI2CCheckBox = xrc.XRCCTRL(self, "TargetSupportsI2CCheckBox")
        self.TargetThirdStaticLine = xrc.XRCCTRL(self, "TargetThirdStaticLine")
        self.TargetLibraryLabel = xrc.XRCCTRL(self, "TargetLibraryLabel")
        self.TargetCheckList = xrc.XRCCTRL(self, "TargetCheckList")
        self.TargetLastStaticLine = xrc.XRCCTRL(self, "TargetLastStaticLine")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.addButton = xrc.XRCCTRL(self, "addButton")

        self.Bind(wx.EVT_TEXT, self.OnText_Name_TextCtrl, self.Name_TextCtrl)
        self.Bind(wx.EVT_LISTBOX, self.OnListbox_ModbusRegisterListBox, self.ModbusRegisterListBox)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListbox_dclick_ModbusRegisterListBox, self.ModbusRegisterListBox)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterAddButton, self.ModbusRegisterAddButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterRemoveButton, self.ModbusRegisterRemoveButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterEditButton, self.ModbusRegisterEditButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterUpButton, self.ModbusRegisterUpButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterDownButton, self.ModbusRegisterDownButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_ShieldSupportsModbusCheckBox, self.ShieldSupportsModbusCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_ShieldSupportsSPICheckBox, self.ShieldSupportsSPICheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_ShieldSupportsI2CCheckBox, self.ShieldSupportsI2CCheckBox)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinctrl_I2CAdressSpinCtrl, self.I2CAdressSpinCtrl)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_I2CHasCheckBox, self.I2CHasCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_I2CHasSubAdressCheckBox, self.I2CHasSubAdressCheckBox)
        self.Bind(wx.EVT_CHOICE, self.OnChoice_TargetChoice, self.TargetChoice)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_TargetSupportsModbusCheckBox, self.TargetSupportsModbusCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_TargetSupportsSPICheckBox, self.TargetSupportsSPICheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_TargetSupportsI2CCheckBox, self.TargetSupportsI2CCheckBox)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnChecklistbox_TargetCheckList, self.TargetCheckList)
        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_addButton, self.addButton)
        
        self.__Path = path
        self.__CExtensionType = cextensionType
        self.__NameAlreadyExistChanged = False
                
        if self.__CExtensionType == EsPeEs.CExtension.Type.ModbusDevice:
            self.ShieldPanel.Hide()
            self.I2CPanel.Hide()
            self.TargetPanel.Hide()
            
        if self.__CExtensionType == EsPeEs.CExtension.Type.SPIDevice:
            self.ModbusPanel.Hide()
            self.ShieldPanel.Hide()
            self.I2CPanel.Hide()
            self.TargetPanel.Hide()
            
        if self.__CExtensionType == EsPeEs.CExtension.Type.I2CDevice:
            self.ModbusPanel.Hide()
            self.ShieldPanel.Hide()
            self.TargetPanel.Hide()
            
        if self.__CExtensionType == EsPeEs.CExtension.Type.Shield:
            self.ModbusPanel.Hide()
            self.I2CPanel.Hide()
            self.TargetPanel.Hide()
            
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            self.TargetChoice.Append('Linux32Bit')
            self.TargetChoice.Append('Linux64Bit')
            self.TargetChoice.Append('Windows')
            self.TargetChoice.Append('RaspberryPi')
            info = EsPeEs.ServerInformation()
            if info.isLinux() and info.is32Bit():
                self.TargetChoice.SetSelection(0)
            if info.isLinux() and info.is64Bit():
                self.TargetChoice.SetSelection(1)
            if info.isWindows():
                self.TargetChoice.SetSelection(2)
            if info.isRaspberryPi():
                self.TargetChoice.SetSelection(3)
            libs = EsPeEs.Libraries.Instance().listLibraries()
            for lib in libs:
                if not (lib == 'EsPeEs'):
                    self.TargetCheckList.Append(lib)
            self.ModbusPanel.Hide()
            self.ShieldPanel.Hide()
            self.I2CPanel.Hide()
            
        self.OnText_Name_TextCtrl(None)
        self.OnListbox_ModbusRegisterListBox(None)
        self.OnText_Name_TextCtrl(None)
        
        self.I2CAdressSpinCtrl.SetRange(0, 1023)
        
        self.Fit()
        self.GetParent().Fit()
        
    def __refresh__(self):
        self.ModbusRegisterListBox.Clear()
        registers = self.getRegisters()
        for i in range(len(registers)):
            self.ModbusRegisterListBox.Append(registers[i])

    def OnText_Name_TextCtrl(self, evt):
        ok = True
        if EsPeEs.DriverManager.Instance().childExist(self.Name_TextCtrl.GetValue(), self.__Path, self.__CExtensionType) == True:
            ok = False
            self.nameAlreadyBeenTaken_Label.Show()
        else:
            self.nameAlreadyBeenTaken_Label.Hide()
            
        if EsPeEs.legalName(self.Name_TextCtrl.GetValue()) == False:
            ok = False
            self.illegalName_Label.Show()
        else:
            self.illegalName_Label.Hide()
            
        if ok == True:
            self.addButton.Enable()
        else:
            self.addButton.Disable()
        self.Layout()

    def OnListbox_ModbusRegisterListBox(self, evt):
        if not (self.ModbusRegisterListBox.GetSelection() == -1):
            self.ModbusRegisterRemoveButton.Enable()
            self.ModbusRegisterEditButton.Enable()
            if self.canMoveUpRegister(self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection())) == True:
                self.ModbusRegisterUpButton.Enable()
            else:
                self.ModbusRegisterUpButton.Disable()
            if self.canMoveDownRegister(self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection())) == True:
                self.ModbusRegisterDownButton.Enable()
            else:
                self.ModbusRegisterDownButton.Disable()
        else:
            self.ModbusRegisterRemoveButton.Disable()
            self.ModbusRegisterEditButton.Disable()
            self.ModbusRegisterUpButton.Disable()
            self.ModbusRegisterDownButton.Disable()

    def OnListbox_dclick_ModbusRegisterListBox(self, evt):
        self.OnButton_ModbusRegisterEditButton(None)

    def OnButton_ModbusRegisterAddButton(self, evt):
        dlg = DriverAddRegisterDialog(self)
        dlg.ShowModal()
        if dlg.GetReturnCode() == 1:
            self.addRegister(dlg.getName())
            self.__refresh__()
            self.ModbusRegisterListBox.SetSelection(self.getRegisterIndex(dlg.getName()))
            self.OnListbox_ModbusRegisterListBox(None)

    def OnButton_ModbusRegisterRemoveButton(self, evt):
        self.removeRegister(self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection()))
        self.__refresh__()
        self.OnListbox_ModbusRegisterListBox(None)

    def OnButton_ModbusRegisterEditButton(self, evt):
        dlg = DriverEditRegisterDialog(self)
        dlg.ShowModal()
        if dlg.GetReturnCode() == 1:
            self.renameRegister(self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection()), dlg.getName())
            self.__refresh__()
            self.ModbusRegisterListBox.SetSelection(self.getRegisterIndex(dlg.getName()))
            self.OnListbox_ModbusRegisterListBox(None)

    def OnButton_ModbusRegisterUpButton(self, evt):
        name = self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection())
        self.moveUpRegister(name)
        self.__refresh__()
        self.ModbusRegisterListBox.SetSelection(self.getRegisterIndex(name))
        self.OnListbox_ModbusRegisterListBox(None)

    def OnButton_ModbusRegisterDownButton(self, evt):
        name = self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection())
        self.moveDownRegister(name)
        self.__refresh__()
        self.ModbusRegisterListBox.SetSelection(self.getRegisterIndex(name))
        self.OnListbox_ModbusRegisterListBox(None)

    def OnCheckbox_ShieldSupportsModbusCheckBox(self, evt):
        pass

    def OnCheckbox_ShieldSupportsSPICheckBox(self, evt):
        pass

    def OnCheckbox_ShieldSupportsI2CCheckBox(self, evt):
        pass
        
    def OnSpinctrl_I2CAdressSpinCtrl(self, evt):
        pass

    def OnCheckbox_I2CHasCheckBox(self, evt):
        if self.I2CHasCheckBox.GetValue() == True:        
            if self.I2CHasSubAdressCheckBox.GetValue() == True:
                self.I2CHasSubAdressCheckBox.SetValue(False)           

    def OnCheckbox_I2CHasSubAdressCheckBox(self, evt):
        if self.I2CHasSubAdressCheckBox.GetValue() == True:        
            if self.I2CHasCheckBox.GetValue() == True:
                self.I2CHasCheckBox.SetValue(False)

    def OnChoice_TargetChoice(self, evt):
        pass

    def OnCheckbox_TargetSupportsModbusCheckBox(self, evt):
        pass

    def OnCheckbox_TargetSupportsSPICheckBox(self, evt):
        pass

    def OnCheckbox_TargetSupportsI2CCheckBox(self, evt):
        pass

    def OnChecklistbox_TargetCheckList(self, evt):
        pass

    def OnButton_cancelButton(self, evt):
        self.GetParent().EndModal(0)

    def OnButton_addButton(self, evt):
        self.GetParent().EndModal(1)
        
    def getI2CAdress(self):
        return self.I2CAdressSpinCtrl.GetValue()
        
    def hasTenBitAdress(self):
        return self.I2CHasCheckBox.GetValue()
        
    def hasSubAdress(self):
        return self.I2CHasSubAdressCheckBox.GetValue()
        
    def isModbusCompatible(self):
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            return self.TargetSupportsModbusCheckBox.GetValue()
        else:
            return not self.ShieldSupportsModbusCheckBox.GetValue()
        
    def isSPICompatible(self):
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            return self.TargetSupportsSPICheckBox.GetValue()
        else:
            return not self.ShieldSupportsSPICheckBox.GetValue()
        
    def isI2CCompatible(self):
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            return self.TargetSupportsI2CCheckBox.GetValue()
        else:
            return not self.ShieldSupportsI2CCheckBox.GetValue()
        
    def getLibraries(self):
        return self.TargetCheckList.GetCheckedStrings()
    
    def getTarget(self):
        sel = self.TargetChoice.GetSelection()
        if sel == 0:
            return EsPeEs.Targets.Linux32Bit
        if sel == 1:
            return EsPeEs.Targets.Linux64Bit
        if sel == 3:
            return EsPeEs.Targets.RaspberryPi
        if sel == 2:
            return EsPeEs.Targets.Windows
        return 'Error'
        
    def getName(self):
        return self.Name_TextCtrl.GetValue()
        
    def addRegister(self, name):
        self.__Register.addRegister(name)
    
    def removeRegister(self, name):
        self.__Register.removeRegister(name)
                
    def renameRegister(self, name, newName):
        self.__Register.renameRegister(name, newName)
        
    def moveUpRegister(self, name):
        self.__Register.moveUpRegister(name)
        
    def moveDownRegister(self, name):
        self.__Register.moveDownRegister(name)
        
    def getRegisterIndex(self, name):
        return self.__Register.getRegisterIndex(name)
        
    def canMoveDownRegister(self, name):
        return self.__Register.canMoveDownRegister(name)
        
    def canMoveUpRegister(self, name):
        return self.__Register.canMoveUpRegister(name)
        
    def existRegister(self, name):
        registers = self.getRegisters()
        for i in range(len(registers)):
            if registers[i] == name:
                return True
        return False
        
    def getRegisters(self):
        registers = self.__Register.getRegisters()
        return registers
        
    def setRegisters(self, registers):
        self.__Register.setRegisters(registers)
        
    def getRegisterSize(self):
        return len(self.__Register.getRegisterSize()) + 3
        
class DriverEditDriverDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType, registers = None, isModbusCompatible = None, isSPICompatible = None, isI2CCompatible = None, i2cAdress = None, hasTenBitAdress = None, hasSubAdress = None, target = None, libraries = None):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DriverEditDriverDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.__Panel = DriverEditDriverPanel(self, path, cextensionType, registers = registers, isModbusCompatible = isModbusCompatible, isSPICompatible = isSPICompatible, isI2CCompatible = isI2CCompatible, i2cAdress = i2cAdress, hasTenBitAdress = hasTenBitAdress, hasSubAdress = hasSubAdress, target = target, libraries = libraries)
        self.__Panel.Show()
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
    def getName(self):
        return self.__Panel.getName()
        
    def getRegisters(self):
        return self.__Panel.getRegisters()
        
    def getI2CAdress(self):
        return self.__Panel.getI2CAdress()
        
    def hasTenBitAdress(self):
        return self.__Panel.hasTenBitAdress()
        
    def hasSubAdress(self):
        return self.__Panel.hasSubAdress()
        
    def isModbusCompatible(self):
        return self.__Panel.isModbusCompatible()
        
    def isSPICompatible(self):
        return self.__Panel.isSPICompatible()
        
    def isI2CCompatible(self):
        return self.__Panel.isI2CCompatible()
        
    def getTarget(self):
        return self.__Panel.getTarget()
        
    def getLibraries(self):
        return self.__Panel.getLibraries()

    def OnClose(self, evt):
        self.EndModal(0)

class DriverEditDriverPanel(wx.Panel):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType, registers = None, isModbusCompatible = None, isSPICompatible = None, isI2CCompatible = None, i2cAdress = None, hasTenBitAdress = None, hasSubAdress = None, target = None, libraries = None):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "DriverEditDriverPanel")
        self.PostCreate(pre)
        self.__Register = EsPeEs.Register()

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Name_Label = xrc.XRCCTRL(self, "Name_Label")
        self.Name_TextCtrl = xrc.XRCCTRL(self, "Name_TextCtrl")
        self.nameAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "nameAlreadyBeenTaken_Label")
        self.illegalName_Label = xrc.XRCCTRL(self, "illegalName_Label")
        self.ModbusPanel = xrc.XRCCTRL(self, "ModbusPanel")
        self.ModbusFirstStaticline = xrc.XRCCTRL(self, "ModbusFirstStaticline")
        self.ModbusRegisterLabel = xrc.XRCCTRL(self, "ModbusRegisterLabel")
        self.ModbusRegisterListBox = xrc.XRCCTRL(self, "ModbusRegisterListBox")
        self.ModbusRegisterAddButton = xrc.XRCCTRL(self, "ModbusRegisterAddButton")
        self.ModbusRegisterRemoveButton = xrc.XRCCTRL(self, "ModbusRegisterRemoveButton")
        self.ModbusRegisterEditButton = xrc.XRCCTRL(self, "ModbusRegisterEditButton")
        self.ModbusRegisterButtonStaticLine = xrc.XRCCTRL(self, "ModbusRegisterButtonStaticLine")
        self.ModbusRegisterUpButton = xrc.XRCCTRL(self, "ModbusRegisterUpButton")
        self.ModbusRegisterDownButton = xrc.XRCCTRL(self, "ModbusRegisterDownButton")
        self.ModbusLastStaticline = xrc.XRCCTRL(self, "ModbusLastStaticline")
        self.ShieldPanel = xrc.XRCCTRL(self, "ShieldPanel")
        self.ShieldFirstStaticLine = xrc.XRCCTRL(self, "ShieldFirstStaticLine")
        self.ShieldHasSupportForLabel = xrc.XRCCTRL(self, "ShieldHasSupportForLabel")
        self.ShieldSupportsModbusCheckBox = xrc.XRCCTRL(self, "ShieldSupportsModbusCheckBox")
        self.ShieldSupportsSPICheckBox = xrc.XRCCTRL(self, "ShieldSupportsSPICheckBox")
        self.ShieldSupportsI2CCheckBox = xrc.XRCCTRL(self, "ShieldSupportsI2CCheckBox")
        self.ShieldLastStaticLine = xrc.XRCCTRL(self, "ShieldLastStaticLine")
        self.I2CPanel = xrc.XRCCTRL(self, "I2CPanel")
        self.I2CFirstStaticLine = xrc.XRCCTRL(self, "I2CFirstStaticLine")
        self.I2CAdressLabel = xrc.XRCCTRL(self, "I2CAdressLabel")
        self.I2CAdressSpinCtrl = xrc.XRCCTRL(self, "I2CAdressSpinCtrl")
        self.I2CHasCheckBox = xrc.XRCCTRL(self, "I2CHasCheckBox")
        self.I2CHasSubAdressCheckBox = xrc.XRCCTRL(self, "I2CHasSubAdressCheckBox")
        self.I2CLastStaticLine = xrc.XRCCTRL(self, "I2CLastStaticLine")
        self.TargetPanel = xrc.XRCCTRL(self, "TargetPanel")
        self.TargetFirstStaticLine = xrc.XRCCTRL(self, "TargetFirstStaticLine")
        self.TargetPlatformLabel = xrc.XRCCTRL(self, "TargetPlatformLabel")
        self.TargetChoice = xrc.XRCCTRL(self, "TargetChoice")
        self.TargetSecondStaticLine = xrc.XRCCTRL(self, "TargetSecondStaticLine")
        self.TargetHasSupportForLabel = xrc.XRCCTRL(self, "TargetHasSupportForLabel")
        self.TargetSupportsModbusCheckBox = xrc.XRCCTRL(self, "TargetSupportsModbusCheckBox")
        self.TargetSupportsSPICheckBox = xrc.XRCCTRL(self, "TargetSupportsSPICheckBox")
        self.TargetSupportsI2CCheckBox = xrc.XRCCTRL(self, "TargetSupportsI2CCheckBox")
        self.TargetThirdStaticLine = xrc.XRCCTRL(self, "TargetThirdStaticLine")
        self.TargetLibraryLabel = xrc.XRCCTRL(self, "TargetLibraryLabel")
        self.TargetCheckList = xrc.XRCCTRL(self, "TargetCheckList")
        self.TargetLastStaticLine = xrc.XRCCTRL(self, "TargetLastStaticLine")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.editButton = xrc.XRCCTRL(self, "editButton")

        self.Bind(wx.EVT_TEXT, self.OnText_Name_TextCtrl, self.Name_TextCtrl)
        self.Bind(wx.EVT_LISTBOX, self.OnListbox_ModbusRegisterListBox, self.ModbusRegisterListBox)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListbox_dclick_ModbusRegisterListBox, self.ModbusRegisterListBox)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterAddButton, self.ModbusRegisterAddButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterRemoveButton, self.ModbusRegisterRemoveButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterEditButton, self.ModbusRegisterEditButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterUpButton, self.ModbusRegisterUpButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_ModbusRegisterDownButton, self.ModbusRegisterDownButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_ShieldSupportsModbusCheckBox, self.ShieldSupportsModbusCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_ShieldSupportsSPICheckBox, self.ShieldSupportsSPICheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_ShieldSupportsI2CCheckBox, self.ShieldSupportsI2CCheckBox)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinctrl_I2CAdressSpinCtrl, self.I2CAdressSpinCtrl)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_I2CHasCheckBox, self.I2CHasCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_I2CHasSubAdressCheckBox, self.I2CHasSubAdressCheckBox)
        self.Bind(wx.EVT_CHOICE, self.OnChoice_TargetChoice, self.TargetChoice)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_TargetSupportsModbusCheckBox, self.TargetSupportsModbusCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_TargetSupportsSPICheckBox, self.TargetSupportsSPICheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_TargetSupportsI2CCheckBox, self.TargetSupportsI2CCheckBox)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnChecklistbox_TargetCheckList, self.TargetCheckList)
        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_editButton, self.editButton)
        
        self.__Path = path
        self.__CExtensionType = cextensionType
        self.__NameAlreadyExistChanged = False
        self.__OldName = path[len(path) - 1]
        
        if not (registers == None):
            del registers[len(registers) - 1]
            del registers[len(registers) - 1]
            del registers[len(registers) - 1]
            del registers[len(registers) - 1]
            del registers[len(registers) - 1]
            self.setRegisters(registers)
            self.__refresh__()
        
        if not (isModbusCompatible == None):
            self.ShieldSupportsModbusCheckBox.SetValue(not isModbusCompatible)
            
        if not (isSPICompatible == None):
            self.ShieldSupportsSPICheckBox.SetValue(not isSPICompatible)
        
        if not (isI2CCompatible == None):
            self.ShieldSupportsI2CCheckBox.SetValue(not isI2CCompatible)
            
        if not (i2cAdress == None):
            self.I2CAdressSpinCtrl.SetValue(i2cAdress)
            
        if not (hasTenBitAdress == None):
            self.I2CHasCheckBox.SetValue(hasTenBitAdress)
            
        if not (hasSubAdress == None):
            self.I2CHasSubAdressCheckBox.SetValue(hasSubAdress)
                            
        if self.__CExtensionType == EsPeEs.CExtension.Type.ModbusDevice:
            self.ShieldPanel.Hide()
            self.TargetPanel.Hide()
            self.I2CPanel.Hide()
            
        if self.__CExtensionType == EsPeEs.CExtension.Type.SPIDevice:
            self.ModbusPanel.Hide()
            self.ShieldPanel.Hide()
            self.I2CPanel.Hide()
            self.TargetPanel.Hide()
            
        if self.__CExtensionType == EsPeEs.CExtension.Type.I2CDevice:
            self.ModbusPanel.Hide()
            self.ShieldPanel.Hide()
            self.TargetPanel.Hide()
            
        if self.__CExtensionType == EsPeEs.CExtension.Type.Shield:
            self.ModbusPanel.Hide()
            self.I2CPanel.Hide()
            self.TargetPanel.Hide()
            
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            self.TargetChoice.Append('Linux32Bit')
            self.TargetChoice.Append('Linux64Bit')
            self.TargetChoice.Append('Windows')
            self.TargetChoice.Append('RaspberryPi')
            
            if target == EsPeEs.Targets.Linux32Bit:
                self.TargetChoice.SetSelection(0)
            if target == EsPeEs.Targets.Linux64Bit:
                self.TargetChoice.SetSelection(1)
            if target == EsPeEs.Targets.Windows:
                self.TargetChoice.SetSelection(2)
            if target == EsPeEs.Targets.RaspberryPi:
                self.TargetChoice.SetSelection(3)
            libs = EsPeEs.Libraries.Instance().listLibraries()
            for lib in libs:
                if not (lib == 'EsPeEs'):
                    self.TargetCheckList.Append(lib)
            self.TargetCheckList.SetCheckedStrings(libraries)
            self.TargetSupportsModbusCheckBox.SetValue(isModbusCompatible)
            self.TargetSupportsSPICheckBox.SetValue(isSPICompatible)
            self.TargetSupportsI2CCheckBox.SetValue(isI2CCompatible)
            self.ModbusPanel.Hide()
            self.ShieldPanel.Hide()
            self.I2CPanel.Hide()
            
        self.Name_TextCtrl.SetValue(self.__OldName)
            
        self.OnText_Name_TextCtrl(None)
        self.OnListbox_ModbusRegisterListBox(None)
        self.OnText_Name_TextCtrl(None)
        
        self.I2CAdressSpinCtrl.SetRange(0, 1023)
        
        self.Fit()
        self.GetParent().Fit()
        
    def OnChoice_TargetChoice(self, evt):
        print "OnChoice_TargetChoice()"

    def OnCheckbox_TargetSupportsModbusCheckBox(self, evt):
        print "OnCheckbox_TargetSupportsModbusCheckBox()"

    def OnCheckbox_TargetSupportsSPICheckBox(self, evt):
        print "OnCheckbox_TargetSupportsSPICheckBox()"

    def OnCheckbox_TargetSupportsI2CCheckBox(self, evt):
        print "OnCheckbox_TargetSupportsI2CCheckBox()"

    def OnChecklistbox_TargetCheckList(self, evt):
        print "OnChecklistbox_TargetCheckList()"
        
    def __refresh__(self):
        self.ModbusRegisterListBox.Clear()
        registers = self.getRegisters()
        for i in range(len(registers)):
            self.ModbusRegisterListBox.Append(registers[i])

    def OnText_Name_TextCtrl(self, evt):
        ok = True
        
        if (EsPeEs.DriverManager.Instance().childExist(self.Name_TextCtrl.GetValue(), self.__Path, self.__CExtensionType) == True) and not (self.__OldName == self.Name_TextCtrl.GetValue()):
            ok = False
            self.nameAlreadyBeenTaken_Label.Show()
        else:
            self.nameAlreadyBeenTaken_Label.Hide()
            
        if EsPeEs.legalName(self.Name_TextCtrl.GetValue()) == False:
            ok = False
            self.illegalName_Label.Show()
        else:
            self.illegalName_Label.Hide()
            
        if ok == True:
            self.editButton.Enable()
        else:
            self.editButton.Disable()
        self.Layout()

    def OnListbox_ModbusRegisterListBox(self, evt):
        if not (self.ModbusRegisterListBox.GetSelection() == -1):
            self.ModbusRegisterRemoveButton.Enable()
            self.ModbusRegisterEditButton.Enable()
            if self.canMoveUpRegister(self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection())) == True:
                self.ModbusRegisterUpButton.Enable()
            else:
                self.ModbusRegisterUpButton.Disable()
            if self.canMoveDownRegister(self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection())) == True:
                self.ModbusRegisterDownButton.Enable()
            else:
                self.ModbusRegisterDownButton.Disable()
        else:
            self.ModbusRegisterRemoveButton.Disable()
            self.ModbusRegisterEditButton.Disable()
            self.ModbusRegisterUpButton.Disable()
            self.ModbusRegisterDownButton.Disable()

    def OnListbox_dclick_ModbusRegisterListBox(self, evt):
        self.OnButton_ModbusRegisterEditButton(None)

    def OnButton_ModbusRegisterAddButton(self, evt):
        dlg = DriverAddRegisterDialog(self)
        dlg.ShowModal()
        if dlg.GetReturnCode() == 1:
            self.addRegister(dlg.getName())
            self.__refresh__()
            self.ModbusRegisterListBox.SetSelection(self.getRegisterIndex(dlg.getName()))
            self.OnListbox_ModbusRegisterListBox(None)

    def OnButton_ModbusRegisterRemoveButton(self, evt):
        self.removeRegister(self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection()))
        self.__refresh__()
        self.OnListbox_ModbusRegisterListBox(None)

    def OnButton_ModbusRegisterEditButton(self, evt):
        dlg = DriverEditRegisterDialog(self)
        dlg.ShowModal()
        if dlg.GetReturnCode() == 1:
            self.renameRegister(self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection()), dlg.getName())
            self.__refresh__()
            self.ModbusRegisterListBox.SetSelection(self.getRegisterIndex(dlg.getName()))
            self.OnListbox_ModbusRegisterListBox(None)

    def OnButton_ModbusRegisterUpButton(self, evt):
        name = self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection())
        self.moveUpRegister(name)
        self.__refresh__()
        self.ModbusRegisterListBox.SetSelection(self.getRegisterIndex(name))
        self.OnListbox_ModbusRegisterListBox(None)

    def OnButton_ModbusRegisterDownButton(self, evt):
        name = self.ModbusRegisterListBox.GetString(self.ModbusRegisterListBox.GetSelection())
        self.moveDownRegister(name)
        self.__refresh__()
        self.ModbusRegisterListBox.SetSelection(self.getRegisterIndex(name))
        self.OnListbox_ModbusRegisterListBox(None)

    def OnCheckbox_ShieldSupportsModbusCheckBox(self, evt):
        pass

    def OnCheckbox_ShieldSupportsSPICheckBox(self, evt):
        pass

    def OnCheckbox_ShieldSupportsI2CCheckBox(self, evt):
        pass
        
    def OnSpinctrl_I2CAdressSpinCtrl(self, evt):
        pass

    def OnCheckbox_I2CHasCheckBox(self, evt):
        if self.I2CHasCheckBox.GetValue() == True:        
            if self.I2CHasSubAdressCheckBox.GetValue() == True:
                self.I2CHasSubAdressCheckBox.SetValue(False)           

    def OnCheckbox_I2CHasSubAdressCheckBox(self, evt):
        if self.I2CHasSubAdressCheckBox.GetValue() == True:        
            if self.I2CHasCheckBox.GetValue() == True:
                self.I2CHasCheckBox.SetValue(False)

    def OnButton_cancelButton(self, evt):
        self.GetParent().EndModal(0)

    def OnButton_editButton(self, evt):
        self.GetParent().EndModal(1)
        
    def getI2CAdress(self):
        return self.I2CAdressSpinCtrl.GetValue()
        
    def hasTenBitAdress(self):
        return self.I2CHasCheckBox.GetValue()
        
    def hasSubAdress(self):
        return self.I2CHasSubAdressCheckBox.GetValue()
        
    def isModbusCompatible(self):
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            return self.TargetSupportsModbusCheckBox.GetValue()
        else:
            return not self.ShieldSupportsModbusCheckBox.GetValue()
        
    def isSPICompatible(self):
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            return self.TargetSupportsSPICheckBox.GetValue()
        else:
            return not self.ShieldSupportsSPICheckBox.GetValue()
        
    def isI2CCompatible(self):
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            return self.TargetSupportsI2CCheckBox.GetValue()
        else:
            return not self.ShieldSupportsI2CCheckBox.GetValue()
        
    def getLibraries(self):
        return self.TargetCheckList.GetCheckedStrings()
    
    def getTarget(self):
        sel = self.TargetChoice.GetSelection()
        if sel == 0:
            return EsPeEs.Targets.Linux32Bit
        if sel == 1:
            return EsPeEs.Targets.Linux64Bit
        if sel == 3:
            return EsPeEs.Targets.RaspberryPi
        if sel == 2:
            return EsPeEs.Targets.Windows
        return 'Error'
        
    def getName(self):
        return self.Name_TextCtrl.GetValue()
        
    def addRegister(self, name):
        self.__Register.addRegister(name)
    
    def removeRegister(self, name):
        self.__Register.removeRegister(name)
                
    def renameRegister(self, name, newName):
        self.__Register.renameRegister(name, newName)
        
    def moveUpRegister(self, name):
        self.__Register.moveUpRegister(name)
        
    def moveDownRegister(self, name):
        self.__Register.moveDownRegister(name)
        
    def getRegisterIndex(self, name):
        return self.__Register.getRegisterIndex(name)
        
    def canMoveDownRegister(self, name):
        return self.__Register.canMoveDownRegister(name)
        
    def canMoveUpRegister(self, name):
        return self.__Register.canMoveUpRegister(name)
        
    def existRegister(self, name):
        registers = self.getRegisters()
        for i in range(len(registers)):
            if registers[i] == name:
                return True
        return False
        
    def getRegisters(self):
        registers = self.__Register.getRegisters()
        return registers
        
    def setRegisters(self, registers):
        self.__Register.setRegisters(registers)
        
    def getRegisterSize(self):
        return len(self.__Register.getRegisterSize()) + 3

class DriverEditDirectoryDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DriverEditDirectoryDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.__Panel = DriverEditDirectoryPanel(self, path, cextensionType)
        self.__Panel.Show()
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
    def getName(self):
        return self.__Panel.getName()

    def OnClose(self, evt):
        self.EndModal(0)

class DriverEditDirectoryPanel(wx.Panel):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "DriverEditDirectoryPanel")
        self.PostCreate(pre)

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Name_Label = xrc.XRCCTRL(self, "Name_Label")
        self.Name_TextCtrl = xrc.XRCCTRL(self, "Name_TextCtrl")
        self.nameAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "nameAlreadyBeenTaken_Label")
        self.illegalName_Label = xrc.XRCCTRL(self, "illegalName_Label")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.editButton = xrc.XRCCTRL(self, "editButton")

        self.Bind(wx.EVT_TEXT, self.OnText_Name_TextCtrl, self.Name_TextCtrl)
        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_editButton, self.editButton)
        
        self.__Path = path
        self.__CExtensionType = cextensionType
        self.OnText_Name_TextCtrl(None)
        self.Layout()
        self.GetParent().Fit()

    def OnText_Name_TextCtrl(self, evt):
        ok = True
        
        if EsPeEs.DriverManager.Instance().childExist(self.Name_TextCtrl.GetValue(), EsPeEs.DriverManager.Instance().removePath(self.__Path), self.__CExtensionType) == True:
            ok = False
            self.nameAlreadyBeenTaken_Label.Show()
        else:
            self.nameAlreadyBeenTaken_Label.Hide()
            
        if EsPeEs.legalName(self.Name_TextCtrl.GetValue()) == False:
            ok = False
            self.illegalName_Label.Show()
        else:
            self.illegalName_Label.Hide()
            
        if ok == True:
            self.editButton.Enable()
        else:
            self.editButton.Disable()
        self.Layout()

    def OnButton_cancelButton(self, evt):
        self.GetParent().EndModal(0)
        
    def OnButton_editButton(self, evt):
        self.GetParent().EndModal(1)
        
    def getName(self):
        return self.Name_TextCtrl.GetValue()

class DriverAddDirectoryDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DriverAddDirectoryDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.__Panel = DriverAddDirectoryPanel(self, path, cextensionType)
        self.__Panel.Show()
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
    def getName(self):
        return self.__Panel.getName()

    def OnClose(self, evt):
        self.EndModal(0)

class DriverAddDirectoryPanel(wx.Panel):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "DriverAddDirectoryPanel")
        self.PostCreate(pre)

        # Define variables for the controls, bind event handlers
        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Name_Label = xrc.XRCCTRL(self, "Name_Label")
        self.Name_TextCtrl = xrc.XRCCTRL(self, "Name_TextCtrl")
        self.nameAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "nameAlreadyBeenTaken_Label")
        self.illegalName_Label = xrc.XRCCTRL(self, "illegalName_Label")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.addButton = xrc.XRCCTRL(self, "addButton")

        self.Bind(wx.EVT_TEXT, self.OnText_Name_TextCtrl, self.Name_TextCtrl)
        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_addButton, self.addButton)
        
        self.__Path = path
        self.__CExtensionType = cextensionType
        self.OnText_Name_TextCtrl(None)
        self.GetParent().Fit()

    def OnText_Name_TextCtrl(self, evt):
        ok = True
        
        if EsPeEs.DriverManager.Instance().childExist(self.Name_TextCtrl.GetValue(), self.__Path, self.__CExtensionType) == True:
            ok = False
            self.nameAlreadyBeenTaken_Label.Show()
        else:
            self.nameAlreadyBeenTaken_Label.Hide()
            
        if EsPeEs.legalName(self.Name_TextCtrl.GetValue()) == False:
            ok = False
            self.illegalName_Label.Show()
        else:
            self.illegalName_Label.Hide()
            
        if ok == True:
            self.addButton.Enable()
        else:
            self.addButton.Disable()
            
        self.Layout()

    def OnButton_cancelButton(self, evt):
        self.GetParent().EndModal(0)
        
    def OnButton_addButton(self, evt):
        self.GetParent().EndModal(1)
        
    def getName(self):
        return self.Name_TextCtrl.GetValue()
        
class DriverAddCFileDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DriverAddCFileDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.__Panel = DriverAddCFilePanel(self, path, cextensionType)
        self.__Panel.Show()
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
    def getName(self):
        return self.__Panel.getName()

    def OnClose(self, evt):
        self.EndModal(0)

class DriverAddCFilePanel(wx.Panel):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "DriverAddCFilePanel")
        self.PostCreate(pre)

        # Define variables for the controls, bind event handlers
        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Name_Label = xrc.XRCCTRL(self, "Name_Label")
        self.Name_TextCtrl = xrc.XRCCTRL(self, "Name_TextCtrl")
        self.nameAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "nameAlreadyBeenTaken_Label")
        self.illegalName_Label = xrc.XRCCTRL(self, "illegalName_Label")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.addButton = xrc.XRCCTRL(self, "addButton")

        self.Bind(wx.EVT_TEXT, self.OnText_Name_TextCtrl, self.Name_TextCtrl)
        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_addButton, self.addButton)

        self.__Path = path
        self.__CExtensionType = cextensionType
        self.OnText_Name_TextCtrl(None)
        self.GetParent().Fit()

    def OnText_Name_TextCtrl(self, evt):
        ok = True
        
        if EsPeEs.DriverManager.Instance().childExist(self.Name_TextCtrl.GetValue(), self.__Path, self.__CExtensionType) == True:
            ok = False
            self.nameAlreadyBeenTaken_Label.Show()
        else:
            self.nameAlreadyBeenTaken_Label.Hide()
            
        if EsPeEs.legalName(self.Name_TextCtrl.GetValue()) == False:
            ok = False
            self.illegalName_Label.Show()
        else:
            self.illegalName_Label.Hide()
            
        if ok == True:
            self.addButton.Enable()
        else:
            self.addButton.Disable()
            
        self.Layout()

    def OnButton_cancelButton(self, evt):
        self.GetParent().EndModal(0)
        
    def OnButton_addButton(self, evt):
        self.GetParent().EndModal(1)
        
    def getName(self):
        return self.Name_TextCtrl.GetValue()
 
class DriverRemoveDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType, entryType):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DriverRemoveDialog")
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        self.__Panel = DriverRemovePanel(self, path, cextensionType, entryType)
        self.__Panel.Show()
        

    def OnClose(self, evt):
        self.EndModal(0)

class DriverRemovePanel(wx.Panel):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent, path, cextensionType, entryType):
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "DriverRemovePanel")
        self.PostCreate(pre)

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Remove_Label = xrc.XRCCTRL(self, "Remove_Label")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.removeButton = xrc.XRCCTRL(self, "removeButton")

        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_removeButton, self.removeButton)
        
        self.__Path = path
        self.__CExtensionType = cextensionType
        self.__EntryType = entryType
        
        if self.__EntryType == 'Directory':
            self.TitleLabel.SetLabel('Remove directory')
        if self.__EntryType == 'Driver':
            self.TitleLabel.SetLabel('Remove driver')
        if self.__EntryType == 'CFile':
            self.TitleLabel.SetLabel('Remove c-file')
        self.Remove_Label.SetLabel(self.pathToText(self.__Path))
        self.Layout()
        self.Fit()
        self.GetParent().Fit()

    def OnButton_cancelButton(self, evt):
        self.GetParent().EndModal(0)

    def OnButton_removeButton(self, evt):
        self.GetParent().EndModal(1)
        
    def pathToText(self, path):
        text = ''
        if self.__CExtensionType == EsPeEs.CExtension.Type.ModbusDevice:
           text += 'Modbus modules'
        if self.__CExtensionType == EsPeEs.CExtension.Type.SPIDevice:
            text += 'SPI modules'
        if self.__CExtensionType == EsPeEs.CExtension.Type.I2CDevice:
            text += 'I²C modules'
        if self.__CExtensionType == EsPeEs.CExtension.Type.Shield:
            text += 'Raspberry Pi modules'
        if self.__CExtensionType == EsPeEs.CExtension.Type.TargetDevice:
            text += 'Programmable logic controllers'
        for i in range(len(path)):
            text += ' -> '
            text += path[i].encode('utf-8')
        return text
    
class DriverAddRegisterDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DriverAddRegisterDialog")
        self.PostCreate(pre)

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Panel = xrc.XRCCTRL(self, "Panel")
        self.Name_Label = xrc.XRCCTRL(self, "Name_Label")
        self.Name_TextCtrl = xrc.XRCCTRL(self, "Name_TextCtrl")
        self.nameAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "nameAlreadyBeenTaken_Label")
        self.illegalName_Label = xrc.XRCCTRL(self, "illegalName_Label")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.addButton = xrc.XRCCTRL(self, "addButton")

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TEXT, self.OnText_Name_TextCtrl, self.Name_TextCtrl)
        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_addButton, self.addButton)
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        self.__Registers = parent
        
        self.OnText_Name_TextCtrl(None)
        self.Fit()
        
    def getName(self):
        return self.Name_TextCtrl.GetValue()
        
    def OnClose(self, evt):
        self.EndModal(0)

    def OnText_Name_TextCtrl(self, evt):
        ok = True
        if self.__Registers.existRegister(self.Name_TextCtrl.GetValue()) == True:
            ok = False
            self.nameAlreadyBeenTaken_Label.Show()
        else:
            self.nameAlreadyBeenTaken_Label.Hide()
            
        if EsPeEs.legalName(self.Name_TextCtrl.GetValue()) == False:
            ok = False
            self.illegalName_Label.Show()
        else:
            self.illegalName_Label.Hide()
            
        if ok == True:
            self.addButton.Enable()
        else:
            self.addButton.Disable()
        self.Panel.Layout()

    def OnButton_cancelButton(self, evt):
        self.EndModal(0)

    def OnButton_addButton(self, evt):
        self.EndModal(1)

class DriverEditRegisterDialog(wx.Dialog):
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
    def __init__(self, parent):
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "DriverEditRegisterDialog")
        self.PostCreate(pre)

        self.TitleLabel = xrc.XRCCTRL(self, "TitleLabel")
        self.Panel = xrc.XRCCTRL(self, "Panel")
        self.Name_Label = xrc.XRCCTRL(self, "Name_Label")
        self.Name_TextCtrl = xrc.XRCCTRL(self, "Name_TextCtrl")
        self.nameAlreadyBeenTaken_Label = xrc.XRCCTRL(self, "nameAlreadyBeenTaken_Label")
        self.illegalName_Label = xrc.XRCCTRL(self, "illegalName_Label")
        self.cancelButton = xrc.XRCCTRL(self, "cancelButton")
        self.editButton = xrc.XRCCTRL(self, "editButton")

        self.Bind(wx.EVT_TEXT, self.OnText_Name_TextCtrl, self.Name_TextCtrl)
        self.Bind(wx.EVT_BUTTON, self.OnButton_cancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton_editButton, self.editButton)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("GUIs/Icons/espees.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
              
        self.__Registers = parent
        
        self.OnText_Name_TextCtrl(None)
        self.Fit()
        
    def getName(self):
        return self.Name_TextCtrl.GetValue()

    def OnText_Name_TextCtrl(self, evt):
        if self.__Registers.existRegister(self.Name_TextCtrl.GetValue()) == True:
            ok = False
            self.nameAlreadyBeenTaken_Label.Show()
        else:
            self.nameAlreadyBeenTaken_Label.Hide()
            
        if EsPeEs.legalName(self.Name_TextCtrl.GetValue()) == False:
            ok = False
            self.illegalName_Label.Show()
        else:
            self.illegalName_Label.Hide()
            
        if ok == True:
            self.editButton.Enable()
        else:
            self.editButton.Disable()
        self.Panel.Layout()

    def OnButton_cancelButton(self, evt):
        self.EndModal(0)

    def OnButton_editButton(self, evt):
        self.EndModal(1)

    def OnClose(self, evt):
        self.EndModal(0)
        
#DEFAULT_ENCODING= 'utf8'

faces = { 'times': 'Times',
          'mono' : 'Courier',
          'helv' : 'Helvetica',
          'other': 'new century schoolbook',
          'size' : 10 }

ERROR_HIGHLIGHT = (wx.Colour(255, 255, 0), wx.RED)
SEARCH_RESULT_HIGHLIGHT = (wx.Colour(255, 165, 0), wx.WHITE)

REFRESH_HIGHLIGHT_PERIOD = 0.1
          
[STC_CODE_ERROR, STC_CODE_SEARCH_RESULT, 
 STC_CODE_SECTION] = range(15, 18)

HIGHLIGHT_TYPES = { ERROR_HIGHLIGHT: STC_CODE_ERROR,
                    SEARCH_RESULT_HIGHLIGHT: STC_CODE_SEARCH_RESULT }
       
class CppEditor(stc.StyledTextCtrl):
    
    EDGE_COLUMN = 80
   
    KEYWORDS = ["asm", "auto", "bool", "break", "case", "catch", "char", "class", 
                "const", "const_cast", "continue", "default", "delete", "do", "double", 
                "dynamic_cast", "else", "enum", "explicit", "export", "extern", "false", 
                "float", "for", "friend", "goto", "if", "inline", "int", "long", "mutable", 
                "namespace", "new", "operator", "private", "protected", "public", "register", 
                "reinterpret_cast", "return", "short", "signed", "sizeof", "static", 
                "static_cast", "struct", "switch", "template", "this", "throw", "true", "try",
                "typedef", "typeid", "typename", "union", "unsigned", "using", "virtual", 
                "void", "volatile", "wchar_t", "while"]
    COMMENT_HEADER = ""
    
    def __init__(self, parent):
        stc.StyledTextCtrl.__init__(self,parent,-1)
        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 25)

        self.SetProperty("fold", "1")
        self.SetProperty("tab.timmy.whinge.level", "1")
        self.SetMargins(0,0)

        self.SetViewWhiteSpace(False)
        
        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(CppEditor.EDGE_COLUMN)

        # Setup a margin to hold fold markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        # Like a flattened tree control using square headers
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS,          "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,           "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,             "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,           "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,           "white", "#808080")
        
        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
       
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)

        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from
        # Scintilla sample property files.

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(mono)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")
        
        # Highlighting styles
        self.StyleSetSpec(STC_CODE_ERROR, 'fore:#FF0000,back:#FFFF00,size:%(size)d' % faces)
        self.StyleSetSpec(STC_CODE_SEARCH_RESULT, 'fore:#FFFFFF,back:#FFA500,size:%(size)d' % faces)
        
        # Section style
        self.StyleSetSpec(STC_CODE_SECTION, 'fore:#808080,size:%(size)d')
        self.StyleSetChangeable(STC_CODE_SECTION, False)
        
        # Indentation size
        self.SetTabWidth(4)
        self.SetUseTabs(0)
        
        self.SetCodeLexer()
        keywords = " ".join(self.KEYWORDS) + " ".join(EsPeEs.DataTypes.get())
        self.SetKeyWords(0, keywords)
               
        self.RefreshHighlightsTimer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnRefreshHighlightsTimer, self.RefreshHighlightsTimer)
            
        self.SetModEventMask(stc.STC_MOD_INSERTTEXT|stc.STC_MOD_DELETETEXT)

        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(stc.EVT_STC_PAINTED, self.OnPainted)
        
        self.__Driver = None
        self.__CFile = None
        self.__OldCode = ''
        self.__NewCode = ''
        self.__OldSelection = (-1, -1)
        self.__NewSelection = (-1, -1)
        self.__EditingAllowed = False
    
    def setCode(self, driver, cfile):
        self.__Driver = driver
        self.__CFile = cfile
        self.__OldCode = self.__Driver.generateCCode(None, self.__CFile).getCode()
        self.SetText(self.__OldCode)
        self.Colourise(0, -1)
        
    def editingAllowed(self, selection):
        if not (self.__Driver == None) and not (self.__CFile == None):
            return self.__Driver.betweenTags(self.__OldCode, selection)
        else:
            return False
            
    def processChanges(self):
        self.__NewCode = self.GetText()
        if not (self.__Driver == None) and not (self.__CFile == None):
            if (self.__EditingAllowed == True) and (self.__Driver.hasTags(self.__NewCode) == True):
                if self.__Driver.getType() == EsPeEs.CExtension.Type.ModbusDevice:
                    includeCode = self.__Driver.extractCode(self.__NewCode, 'IncludeCode', indent = 0)
                    globalCode = self.__Driver.extractCode(self.__NewCode, 'GlobalCode', indent = 0)
                    retrieveCode = self.__Driver.extractCode(self.__NewCode, 'RetrieveCode', indent = 1)
                    publishCode = self.__Driver.extractCode(self.__NewCode, 'PublishCode', indent = 1)
                    if not (includeCode == '') and not (globalCode == '') and not (retrieveCode == '') and not (publishCode == ''):
                        self.__CFile.setIncludeCode(includeCode[:-1])
                        self.__CFile.setGlobalCode(globalCode[:-1])
                        self.__CFile.setRetrieveCode(retrieveCode[:-1])
                        self.__CFile.setPublishCode(publishCode[:-1])
                        self.__OldCode = self.__NewCode
                        return
                    else:
                        self.Undo()
                        return
                        
                if self.__Driver.getType() == EsPeEs.CExtension.Type.SPIDevice:
                    includeCode = self.__Driver.extractCode(self.__NewCode, 'IncludeCode', indent = 0)
                    globalCode = self.__Driver.extractCode(self.__NewCode, 'GlobalCode', indent = 0)
                    retrieveCode = self.__Driver.extractCode(self.__NewCode, 'RetrieveCode', indent = 1)
                    publishCode = self.__Driver.extractCode(self.__NewCode, 'PublishCode', indent = 1)
                    if not (includeCode == '') and not (globalCode == '') and not (retrieveCode == '') and not (publishCode == ''):
                        self.__CFile.setIncludeCode(includeCode[:-1])
                        self.__CFile.setGlobalCode(globalCode[:-1])
                        self.__CFile.setRetrieveCode(retrieveCode[:-1])
                        self.__CFile.setPublishCode(publishCode[:-1])
                        self.__OldCode = self.__NewCode
                        return
                    else:
                        self.Undo()
                        return
                        
                if self.__Driver.getType() == EsPeEs.CExtension.Type.Shield:
                    includeCode = self.__Driver.extractCode(self.__NewCode, 'IncludeCode', indent = 0)
                    globalCode = self.__Driver.extractCode(self.__NewCode, 'GlobalCode', indent = 0)
                    retrieveCode = self.__Driver.extractCode(self.__NewCode, 'RetrieveCode', indent = 1)
                    publishCode = self.__Driver.extractCode(self.__NewCode, 'PublishCode', indent = 1)
                    if self.__Driver.isSPICompatible() == True:
                        spiCode = self.__Driver.extractCode(self.__NewCode, 'SPICode', indent = 1)
                        if spiCode == '':
                            self.Undo()
                            return
                            
                    if self.__Driver.isI2CCompatible() == True:
                        i2cReadCode = self.__Driver.extractCode(self.__NewCode, 'I2CReadCode', indent = 1)
                        i2cWriteCode = self.__Driver.extractCode(self.__NewCode, 'I2CWriteCode', indent = 1)
                        i2cSetupCode = self.__Driver.extractCode(self.__NewCode, 'I2CSetupCode', indent = 1)
                        if (i2cReadCode == '') or (i2cWriteCode == '') or (i2cSetupCode == ''):
                            self.Undo()
                            return
                            
                    if not (includeCode == '') and not (globalCode == '') and not (retrieveCode == '') and not (publishCode == ''):
                        self.__CFile.setIncludeCode(includeCode[:-1])
                        self.__CFile.setGlobalCode(globalCode[:-1])
                        self.__CFile.setRetrieveCode(retrieveCode[:-1])
                        self.__CFile.setPublishCode(publishCode[:-1])
                        self.__OldCode = self.__NewCode
                        return
                    else:
                        self.Undo()
                        return
                    
                if self.__Driver.getType() == EsPeEs.CExtension.Type.TargetDevice:
                    includeCode = self.__Driver.extractCode(self.__NewCode, 'IncludeCode', indent = 0)
                    globalCode = self.__Driver.extractCode(self.__NewCode, 'GlobalCode', indent = 0)
                    ModbusInterfaceRTUCode = self.__Driver.extractCode(self.__NewCode, 'ModbusInterfaceRTUCode', indent = 1)
                    ModbusInterfaceTCPCode = self.__Driver.extractCode(self.__NewCode, 'ModbusInterfaceTCPCode', indent = 1)
                    ModbusDeviceCode = self.__Driver.extractCode(self.__NewCode, 'ModbusDeviceCode', indent = 1)
                    ModbusInterfaceFreeCode = self.__Driver.extractCode(self.__NewCode, 'ModbusInterfaceFreeCode', indent = 1)
                    ModbusReadRegisterCode = self.__Driver.extractCode(self.__NewCode, 'ModbusReadRegisterCode', indent = 1)
                    ModbusWriteRegisterCode = self.__Driver.extractCode(self.__NewCode, 'ModbusWriteRegisterCode', indent = 1)
                    SPIInterfaceCode = self.__Driver.extractCode(self.__NewCode, 'SPIInterfaceCode', indent = 1)
                    SPIDeviceCode = self.__Driver.extractCode(self.__NewCode, 'SPIDeviceCode', indent = 1)
                    SPIInterfaceFreeCode = self.__Driver.extractCode(self.__NewCode, 'SPIInterfaceFreeCode', indent = 1)
                    SPITransmitCode = self.__Driver.extractCode(self.__NewCode, 'SPITransmitCode', indent = 1)
                    I2CInterfaceCode = self.__Driver.extractCode(self.__NewCode, 'I2CInterfaceCode', indent = 1)
                    I2CDeviceCode = self.__Driver.extractCode(self.__NewCode, 'I2CDeviceCode', indent = 1)
                    I2CInterfaceFreeCode = self.__Driver.extractCode(self.__NewCode, 'I2CInterfaceFreeCode', indent = 1)
                    I2CReadCode = self.__Driver.extractCode(self.__NewCode, 'I2CReadCode', indent = 1)
                    I2CWriteCode = self.__Driver.extractCode(self.__NewCode, 'I2CWriteCode', indent = 1)
                    StartCycleCode = self.__Driver.extractCode(self.__NewCode, 'StartCycleCode', indent = 1)
                    StopCycleCode = self.__Driver.extractCode(self.__NewCode, 'StopCycleCode', indent = 1)
                    AverageCycleTimeCode = self.__Driver.extractCode(self.__NewCode, 'AverageCycleTimeCode', indent = 1)
                    LastCycleTimeCode = self.__Driver.extractCode(self.__NewCode, 'LastCycleTimeCode', indent = 1)
                    ModbusInterfaceStructCode = self.__Driver.extractCode(self.__NewCode, 'ModbusInterfaceStructCode', indent = 1)
                    SPIInterfaceStructCode = self.__Driver.extractCode(self.__NewCode, 'SPIInterfaceStructCode', indent = 1)
                    I2CInterfaceStructCode = self.__Driver.extractCode(self.__NewCode, 'I2CInterfaceStructCode', indent = 1)
                    if not (includeCode == '') and not (globalCode == '') and not (ModbusInterfaceRTUCode == '') and not (ModbusInterfaceTCPCode == '') and not (ModbusDeviceCode == '') and not (ModbusInterfaceFreeCode == '') and not (ModbusReadRegisterCode == '') and not (ModbusWriteRegisterCode == '') and not (SPIInterfaceCode == '') and not (SPIDeviceCode == '') and not (SPIInterfaceFreeCode == '') and not (SPITransmitCode == '') and not (I2CInterfaceCode == '') and not (I2CDeviceCode == '') and not (I2CInterfaceFreeCode == '') and not (I2CReadCode == '') and not (I2CWriteCode == '') and not (StartCycleCode == '') and not (StopCycleCode == '') and not (AverageCycleTimeCode == '') and not (LastCycleTimeCode == '') and not (ModbusInterfaceStructCode == '') and not (SPIInterfaceStructCode == '') and not (I2CInterfaceStructCode == ''):
                        self.__CFile.setIncludeCode(includeCode[:-1])
                        self.__CFile.setGlobalCode(globalCode[:-1])
                        self.__Driver.setModbusInterfaceRTUCode(ModbusInterfaceRTUCode[:-1])
                        self.__Driver.setModbusInterfaceTCPCode(ModbusInterfaceTCPCode[:-1])
                        self.__Driver.setModbusDeviceCode(ModbusDeviceCode[:-1])
                        self.__Driver.setModbusInterfaceFreeCode(ModbusInterfaceFreeCode[:-1])
                        self.__Driver.setModbusReadRegisterCode(ModbusReadRegisterCode[:-1])
                        self.__Driver.setModbusWriteRegisterCode(ModbusWriteRegisterCode[:-1])
                        self.__Driver.setSPIInterfaceCode(SPIInterfaceCode[:-1])
                        self.__Driver.setSPIDeviceCode(SPIDeviceCode[:-1])
                        self.__Driver.setSPIInterfaceFreeCode(SPIInterfaceFreeCode[:-1])
                        self.__Driver.setSPITransmitCode(SPITransmitCode[:-1])
                        self.__Driver.setI2CInterfaceCode(I2CInterfaceCode[:-1])
                        self.__Driver.setI2CDeviceCode(I2CDeviceCode[:-1])
                        self.__Driver.setI2CInterfaceFreeCode(I2CInterfaceFreeCode[:-1])
                        self.__Driver.setI2CReadCode(I2CReadCode[:-1])
                        self.__Driver.setI2CWriteCode(I2CWriteCode[:-1])
                        self.__Driver.setStartCycleCode(StartCycleCode[:-1])                            
                        self.__Driver.setStopCycleCode(StopCycleCode[:-1])
                        self.__Driver.setAverageCycleTimeCode(AverageCycleTimeCode[:-1])
                        self.__Driver.setLastCycleTimeCode(LastCycleTimeCode[:-1])
                        self.__Driver.setModbusInterfaceStructCode(ModbusInterfaceStructCode[:-1])
                        self.__Driver.setSPIInterfaceStructCode(SPIInterfaceStructCode[:-1])
                        self.__Driver.setI2CInterfaceStructCode(I2CInterfaceStructCode[:-1])

                        self.__OldCode = self.__NewCode
                        return
                    else:
                        self.Undo()
                        return
            else:
                self.Undo()
                return
                
    def OnPainted(self, evt):
        if (self.__OldCode != self.GetText()):
            if self.__EditingAllowed == True:
                self.processChanges()
            else:
                self.Undo()
        else:
            self.__OldSelection = self.__NewSelection
            self.__NewSelection = self.GetSelection()
            self.__EditingAllowed = self.editingAllowed(self.__NewSelection)
    
    def SetCodeLexer(self):
        self.SetLexer(stc.STC_LEX_CPP)
        self.StyleSetSpec(stc.STC_C_COMMENT, 'fore:#408060,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_C_COMMENTLINE, 'fore:#408060,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_C_COMMENTDOC, 'fore:#408060,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_C_NUMBER, 'fore:#0076AE,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_C_WORD, 'bold,fore:#800056,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_C_STRING, 'fore:#2a00ff,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_C_PREPROCESSOR, 'bold,fore:#800056,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_C_OPERATOR, 'bold,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_C_STRINGEOL, 'back:#FFD5FF,size:%(size)d' % faces)
           
    def OnKeyPressed(self, event):
        if self.CallTipActive():
            self.CallTipCancel()
        key = event.GetKeyCode()
        current_pos = self.GetCurrentPos()
        selected = self.GetSelection()
        text_selected = selected[0] != selected[1]
        
        # Test if caret is before Windows like new line
        text = self.GetText()
        if current_pos < len(text) and ord(text[current_pos]) == 13:
            newline_size = 2
        else:
            newline_size = 1
        
        # Disable to type any character in section header lines
        if (self.GetLineState(self.LineFromPosition(current_pos)) and
            not text_selected and
            key not in NAVIGATION_KEYS + [
                wx.WXK_RETURN,
                wx.WXK_NUMPAD_ENTER]):
            return
        
        # Disable to delete line between code and header lines
        elif (self.GetCurLine()[0].strip() != "" and not text_selected and
              (key == wx.WXK_BACK and
               self.GetLineState(self.LineFromPosition(max(0, current_pos - 1))) or
               key in [wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE] and
               self.GetLineState(self.LineFromPosition(min(len(text), current_pos + newline_size))))):
            return
        
        elif key == 32 and event.ControlDown():
            pos = self.GetCurrentPos()

            # Tips
            if event.ShiftDown():
                pass
            # Code completion
            else:
                self.AutoCompSetIgnoreCase(False)  # so this needs to match
                
                keywords = self.KEYWORDS + EsPeEs.DataTypes.get() + [var.getName() for var in self.__CFile.getVariables()]
                keywords.sort()
                self.AutoCompShow(0, " ".join(keywords))
        else:
            event.Skip()

    def OnKillFocus(self, event):
        self.AutoCompCancel()
        event.Skip()

    def OnUpdateUI(self, event):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
    
    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())

                if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)
        evt.Skip()

    def FoldAll(self):
        lineCount = self.GetLineCount()
        expanding = True

        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break

        lineNum = 0

        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)

                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1

    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1

        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)

                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1

        return line

    def OnRefreshHighlightsTimer(self, event):
        self.Colourise(0, -1)
        event.Skip()

    def ClearHighlights(self, highlight_type=None):
        if highlight_type is None:
            self.Highlights = []
        else:
            highlight_type = HIGHLIGHT_TYPES.get(highlight_type, None)
            if highlight_type is not None:
                self.Highlights = [(start, end, highlight) for (start, end, highlight) in self.Highlights if highlight != highlight_type]
        self.RefreshView()

    def AddHighlight(self, start, end, highlight_type):
        highlight_type = HIGHLIGHT_TYPES.get(highlight_type, None)
        if highlight_type is not None:
            self.Highlights.append((start, end, highlight_type))
            self.GotoPos(self.PositionFromLine(start[0]) + start[1])
            self.RefreshHighlightsTimer.Start(int(REFRESH_HIGHLIGHT_PERIOD * 1000), oneShot=True)
            self.RefreshView()

    def RemoveHighlight(self, start, end, highlight_type):
        highlight_type = HIGHLIGHT_TYPES.get(highlight_type, None)
        if (highlight_type is not None and 
            (start, end, highlight_type) in self.Highlights):
            self.Highlights.remove((start, end, highlight_type))
            self.RefreshHighlightsTimer.Start(int(REFRESH_HIGHLIGHT_PERIOD * 1000), oneShot=True)
    
    def ShowHighlights(self):
        for start, end, highlight_type in self.Highlights:
            if start[0] == 0:
                highlight_start_pos = start[1]
            else:
                highlight_start_pos = self.GetLineEndPosition(start[0] - 1) + start[1] + 1
            if end[0] == 0:
                highlight_end_pos = end[1] + 1
            else:
                highlight_end_pos = self.GetLineEndPosition(end[0] - 1) + end[1] + 2
            self.StartStyling(highlight_start_pos, 0xff)
            self.SetStyling(highlight_end_pos - highlight_start_pos, highlight_type)
            self.StartStyling(highlight_end_pos, 0x00)
            self.SetStyling(len(self.GetText()) - highlight_end_pos, stc.STC_STYLE_DEFAULT)

__res = None
        
def get_resources():
    """ This function provides access to the XML resources in this module."""
    global __res
    if __res == None:
        __res = xrc.EmptyXmlResource()
        __res.Load('GUIs/EsPeEs.xrc')
        
    return __res        
        
def onCtrlC(signal, frame):
    GUI.quit()        
        
def usage():
    usage = '\nUsage of EsPeEs-Project:\n\n'
    usage += 'EsPeEs-Project [--port=number] [--help]\n\n'
    usage += '           --port=number        - Sets the port-number.\n'
    usage += '                                  Default is 9999.\n'
    usage += '           --help               - Shows this help.\n'
    print usage

if __name__ == '__main__':
    signal.signal(signal.SIGINT, onCtrlC)
    GUI.run()
