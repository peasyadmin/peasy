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
import copy
import codecs
import datetime
import exceptions
import fnmatch
import json
import jsonpickle
import os
import platform
import psutil
import serial.tools.list_ports
import shutil
import signal
import socket
import subprocess
import sys
import time
import wx
import xml.dom.minidom
import zlib
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.client.sync import ModbusSerialClient
from SOAPpy import SOAPProxy
from SOAPpy import SOAPServer
from threading import Thread

if sys.platform == 'win32':
    os.putenv('PATH', os.environ['PATH'] + os.getcwd() + os.sep + 'mingw' +os.sep + 'bin;' + os.getcwd() + os.sep + 'mingw' +os.sep + 'lib;')  

jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)

class Object(object):
    def __init__(self):
        pass
    
    def clone(self):
        return copy.deepcopy(self)

class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

class DataTypes(object):
    """
    This class defines the datatypes of a Beremiz project.
    """
    @staticmethod
    def get():
        l = range(0, 0)
        l.append(DataTypes.BOOL)
        l.append(DataTypes.SINT)
        l.append(DataTypes.INT)
        l.append(DataTypes.DINT)
        l.append(DataTypes.LINT)
        l.append(DataTypes.USINT)
        l.append(DataTypes.UINT)
        l.append(DataTypes.UDINT)
        l.append(DataTypes.ULINT)
        l.append(DataTypes.LREAL)
        l.append(DataTypes.TIME)
        l.append(DataTypes.DATE)
        l.append(DataTypes.TOD)
        l.append(DataTypes.DT)
        l.append(DataTypes.STRING)
        l.append(DataTypes.BYTE)
        l.append(DataTypes.WORD)
        l.append(DataTypes.DWORD)
        l.append(DataTypes.LWORD)
        return sorted(l)
        
    BOOL = 'BOOL'
    SINT = 'SINT'
    INT = 'INT'
    DINT = 'DINT'
    LINT = 'LINT'
    USINT = 'USINT'
    UINT = 'UINT'
    UDINT = 'UDINT'
    ULINT = 'ULINT'
    REAL = 'REAL'
    LREAL = 'LREAL'
    TIME = 'TIME'
    DATE = 'DATE'
    TOD = 'TOD'
    DT = 'DT'
    STRING = 'STRING'
    BYTE = 'BYTE'
    WORD = 'WORD'
    DWORD = 'DWORD'
    LWORD = 'LWORD'

class MemoryTypes(object):
    """
    This class defines the memory-types of a variable.
    It can be an input variable,) an output variable
    or a memory variable.
    """
    @staticmethod
    def get():
        l = range(0,0)
        l.append(MemoryTypes.Input)
        l.append(MemoryTypes.Output)
        l.append(MemoryTypes.Memory)
        return l
    
    Input = 'Input'
    Output = 'Output'
    Memory = 'Memory'
    
class Targets(object):
    """
    This class defines all system-architectures, that can be compiled,
    so these architectures can be used as PLC.
    """
    Linux32Bit = 'Linux32Bit'
    Linux64Bit = 'Linux64Bit'
    RaspberryPi = 'RaspberryPi'
    Windows = 'Windows'
    
class Preferences(object):
    class Modbus(object):
        Baudrate = 115200
        Parity = 'none'
        PyParity = 'N'
        DataBit = 8
        StopBit = 1
        TimeOut = 0.1
        Retries = 25
        DefaultPort = 60502

        
    class SPI(object):
        Clock = 500000
        
    class I2C(object):
        Baudrate = 19200
        
    class SOAP(object):
        TimeOut = 5
        Retries = 3
        
    CCodeIndent = '    '    
    DefaultPort = 60001
    
    @staticmethod
    def saveLastUsedPort(port):
        espees_plc = os.path.join(getSaveFolder(), 'lastUsedPort.xml')   #/home/USER/.EsPeEs/lastUsedPLC.xml
        if not os.path.exists(getSaveFolder()):
            Utilities.makeDirectory(getSaveFolder())
        Utilities.writeToFile(Utilities.objectToJson(port), espees_plc)
        
    @staticmethod
    def loadLastUsedPort():
        espees_plc = os.path.join(getSaveFolder(), 'lastUsedPort.xml')   #/home/USER/.EsPeEs/lastUsedPLC.xml
        if not os.path.exists(getSaveFolder()):
            Utilities.makeDirectory(getSaveFolder())
            Preferences.saveLastUsedPort(Preferences.DefaultPort)
            return Preferences.DefaultPort
        if not os.path.exists(espees_plc):
            Preferences.saveLastUsedPort(Preferences.DefaultPort)
            return Preferences.DefaultPort
        try:
            val = int(Utilities.jsonToObject(Utilities.readFromFile(espees_plc)))
            return val
        except ValueError, e:
            return Preferences.DefaultPort
        
    @staticmethod
    def loadLastUsedPLC():
        espees_plc = os.path.join(getSaveFolder(), 'lastUsedPLC.xml')   #/home/USER/.EsPeEs/lastUsedPLC.xml
        if not os.path.exists(getSaveFolder()):
            Utilities.makeDirectory(getSaveFolder())
            Preferences.saveLastUsedPLC('')
            return ''
        if not os.path.exists(espees_plc):
            Preferences.saveLastUsedPLC('')
            return ''
        return Utilities.jsonToObject(Utilities.readFromFile(espees_plc))
        
    @staticmethod
    def saveLastUsedPLC(plc):
        espees_plc = os.path.join(getSaveFolder(), 'lastUsedPLC.xml')   #/home/USER/.EsPeEs/lastUsedPLC.xml
        if not os.path.exists(getSaveFolder()):
            Utilities.makeDirectory(getSaveFolder())
        Utilities.writeToFile(Utilities.objectToJson(plc), espees_plc)
        
    @staticmethod
    def loadUsedPLCs():
        espees_plcs = os.path.join(getSaveFolder(), 'plcs.xml')   #/home/USER/.EsPeEs/plcs.xml
        if not os.path.exists(getSaveFolder()):
            Utilities.makeDirectory(getSaveFolder())
            Preferences.saveUsedPLCs(range(0, 0))
            return range(0, 0)
        if not os.path.exists(espees_plcs):
            Preferences.saveUsedPLCs(range(0, 0))
            return range(0, 0)
        return Utilities.jsonToObject(Utilities.readFromFile(espees_plcs))
        
    @staticmethod
    def saveUsedPLCs(plcs):
        espees_plcs = os.path.join(getSaveFolder(), 'plcs.xml')   #/home/USER/.EsPeEs/plcs.xml
        if not os.path.exists(getSaveFolder()):
            Utilities.makeDirectory(getSaveFolder())
        Utilities.writeToFile(Utilities.objectToJson(plcs), espees_plcs)    

class Variable(Object):
    """
    The class Variable is written for the class CFile.
    A CFile has variables and this class defines a variable.
    
    A variable has a name, a data-type (look DataTypes) and
    a memory-type (look MemoryTypes).
    """
    def __init__(self, name = None, dataType = DataTypes.BOOL, memoryType = MemoryTypes.Input):
        """
        Constructor of the Variable class.
        
            Args:
               * name (str): Name of the variable.
               * dataType (str): DataType of the variable.
               * memoryType (str): MemoryType of the variable.
        """
        Object.__init__(self)
        self.__Name = name
        self.__DataType = dataType
        self.__MemoryType = memoryType
        
    def getName(self):
        """
        Return the name of this Variable.

           Returns:
                Name of this Variable (str).
        """
        if self.__Name == None:
            return ''
        return self.__Name
    
    def getDataType(self):
        """
        Return the Datatype of this Variable.

           Returns:
                Datatype of this Variable (str).
        """
        return self.__DataType
    
    def getMemoryType(self):
        """
        Return the Memorytype of this Variable.

           Returns:
                Memorytype of this Variable (str).
        """
        return self.__MemoryType
    
    def setName(self, name):
        """
        Set the name of this Variable

           Args:
               * name (str): Name to set.
        """        
        self.__Name = name
    
    def setDataType(self, dataType):
        """
        Set the datatype of this Variable

           Args:
               * dataType (str): Datatype to set.
        """
        self.__DataType = dataType
        
    def setMemoryType(self, memoryType):
        """
        Set the memorytype of this Variable.

           Args:
               * memoryType (str): Memorytype to set.
        """
        self.__MemoryType = memoryType
   
class CCode(Object):
    """
    The class CCode is written for the class CFile, which derives from CCode.
    
    A CFile contains several section to add c-code:
    
        IncludeCode     -   Code to include headers.
        GlobalCode      -   Code to define functions and variables.
        InitializeCode  -   Code, which will be executed, when the CFile will initialized.
        CleanUpCode     -   Code, which will be executed, when the CFile will be destroyed.
        RetrieveCode    -   Code to retrieve data. It will be executed every cycle.
        PublishCode     -   Code to publish data. It will be executed every cycle.
    """
    def __init__(self):
        """
        Constructor of the CCode class.
        """
        Object.__init__(self)
        self.__IncludeCode = ''
        self.__GlobalCode = ''
        self.__InitializeCode = ''
        self.__CleanUpCode = ''
        self.__RetrieveCode = ''
        self.__PublishCode = ''
        
    def getIncludeCode(self):
        """
        Return the include-code.

           Returns:
                Include c-code (str).
        """
        return self.__IncludeCode
    
    def getGlobalCode(self):
        """
        Return the global-code.

           Returns:
                Global c-code (str).
        """
        return self.__GlobalCode    
    
    def getInitializeCode(self):
        """
        Return the initialize-code.

           Returns:
                Initialize-code (str).
        """
        return self.__InitializeCode 
    
    def getCleanUpCode(self):
        """
        Return the cleanup-code.

           Returns:
                Cleanup-code (str).
        """
        return self.__CleanUpCode  
    
    def getRetrieveCode(self):
        """
        Return the retrieve-code.

           Returns:
                Retrieve-code (str).
        """
        return self.__RetrieveCode
    
    def getPublishCode(self):
        """
        Return the publish-code.

           Returns:
                Publish-code (str).
        """
        return self.__PublishCode
    
    def setIncludeCode(self, includeCode):
        """
        Set the include-code.

           Args:
               * includeCode (str): Include-code to set.
        """
        self.__IncludeCode = includeCode

    def setGlobalCode(self, globalCode):
        """
        Set the global-code.

           Args:
               * globalCode (str): Global-code to set.
        """
        self.__GlobalCode = globalCode
    
    def setInitializeCode(self, initializeCode):
        """
        Set the initialize-code.

           Args:
               * initializeCode (str): Initialize-code to set.
        """
        self.__InitializeCode = initializeCode
        
    def setCleanUpCode(self, cleanUpCode):
        """
        Set the cleanup-code.

           Args:
               * cleanUpCode (str): Cleanup-code to set.
        """
        self.__CleanUpCode = cleanUpCode
    
    def setRetrieveCode(self, retrieveCode):
        """
        Set the retrieve-code.

           Args:
               * retriveCode (str): Retrieve-code to set.
        """
        self.__RetrieveCode = retrieveCode
        
    def setPublishCode(self, publishCode):
        """
        Set the publish-code.

           Args:
               * publishCode (str): Publish-code to set.
        """
        self.__PublishCode = publishCode
        
    def setCode(self, includeCode, globalCode, initializeCode, cleanUpCode, retrieveCode, publishCode):
        """
        Set all c-code to in one strike.

           Args:
               * includeCode (str): Include-code to set.
               * globalCode (str): Global-code to set.
               * initializeCode (str): Initialize-code to set.
               * cleanUpCode (str): Cleanup-code to set.
               * retrieveCode (str): Retrieve-code to set.
               * publishCode (str): Publish-code to set.
        """
        self.__IncludeCode = includeCode
        self.__GlobalCode = globalCode
        self.__InitializeCode = initializeCode
        self.__CleanUpCode = cleanUpCode
        self.__RetrieveCode = retrieveCode
        self.__PublishCode = publishCode
        
    def getCode(self):
        text = ''
        text += self.__IncludeCode + '\n'
        text += self.__GlobalCode + '\n'
        text += self.__InitializeCode + '\n'
        text += self.__CleanUpCode + '\n'
        text += self.__RetrieveCode + '\n'
        text += self.__PublishCode + '\n'
        while (text.endswith('\n') == True) :
            text = text[:-1]
        return text
            
class CFile(CCode):
    """
    The class CFile is written for the class CExtension and 
    derives from the class CCode.
    It has a name and it contains variables, which can be added and removed.
    """
    def __init__(self, name = None):
        """
        Constructor of the CFile class.
        
            Args:
               * name (str): Name of the CFile.
        """
        self.__Name = name
        self.__Variables = range(0, 0)
        CCode.__init__(self)
        
    def __compareVariables__(self, x, y):
        if x.getName().lower() > y.getName().lower():
            return 1
        elif x.getName().lower() < y.getName().lower():
            return -1
        else:
            return 0
            
    def __sort__(self):
        self.__Variables.sort(cmp=self.__compareVariables__)
            
    def getName(self):
        """
        Return the name of this CFile.

           Returns:
                Name of this CFile (str).
        """
        return self.__Name
    
    def setName(self, name):
        """
        Set the name of this CFile.

           Args:
               * name (str): Name to set.
        """    
        self.__Name = name
            
    def addVariable(self, name = None, dataType = DataTypes.BOOL, memoryType = MemoryTypes.Input, instance = None):
        """
        Add a new variable by name, data-type and memory-type.
        Or add a already existing instance.

           Args:
               * name (str): Name of the new Variable.
               * dataType (str): DataTyee of the new Variable.
               * memoryType (str): Name of the new Variable.
               * instance (Variable): Already created instance to add.
            
           Returns:
                New created Variable or overgiven instance (Variable).
        """
        if not (name == None) and (instance == None):
            if not self.existVariable(name) and not (name == ''):
                var = Variable(name = name)
                var.setDataType(dataType)
                var.setMemoryType(memoryType)
                self.__Variables.append(var)
                self.__sort__()
                return var
        if (name == None) and not (instance == None):
            if not self.existVariable(instance.getName()) and not (instance.getName() == ''):
                self.__Variables.append(instance)
                self.__sort__()
                return var
        return None
        
    def editVariable(self, name = None, newName = None, dataType = DataTypes.BOOL, memoryType = MemoryTypes.Input):
        if not (name == None) and not (newName == None):
            if self.existVariable(name) == True:
                if (not self.existVariable(newName) or (newName == name)) and not (newName == ''):
                    for var in self.__Variables:
                        if var.getName() == name:
                            var.setName(newName)
                            var.setDataType(dataType)
                            var.setMemoryType(memoryType)
                            self.__sort__()
                            return

    def existVariable(self, name):
        """
        Check if a Variable already exists by the name.

           Args:
               * name (str): Name of the Variable.
            
           Returns:
                True if a Variable exists, else False (bool).
        """
        if not (name == None):
            for var in self.__Variables:
                if var.getName() == name:
                    return True
            return False
        else:
            return False
            
    def getVariableIndex(self, name):
        """
        Check if a Variable already exists by the name.

           Args:
               * name (str): Name of the Variable.
            
           Returns:
                True if a Variable exists, else False (bool).
        """
        if not (name == None):
            for i in range(len(self.__Variables)):
                if self.__Variables[i].getName() == name:
                    return i
            return -1
        else:
            return -1

    def getVariable(self, name = None, index = None):
        """
        Return a Variable by the name or by the index.

           Args:
               * name (str): Name of the Variable.
               * index (int): Index of the Variable.
            
           Returns:
                The Variable (Variable).
        """
        if not (name == None) and (index == None):
            for var in self.__Variables:
                if var.getName() == name:
                    return var
        if not (index == None) and (name == None):
            if (len(self.__Variables) > 0) and (index < len(self.__Variables)):
                return self.__Variables[index]
        return None
        
    def countVariables(self):
        return len(self.__Variables)
    
    def getVariables(self):
        """
        Return the Variable list.
            
           Returns:
                List of Variable (Variable[]).
        """
        return self.__Variables

    def setVariables(self, variables):
        """
        Set a list of Variable.

           Args:
               * variables (str): List of Variable.
        """
        self.__Variables = variables
        self.__sort__()
    
    def removeVariable(self, name = None, index = None):
        """
        Remove a Variable by the name or by the index.

           Args:
               * name (str): Name of the Variable.
               * index (int): Index of the Variable.
        """
        if not (name == None) and (index == None):
            for i in range(len(self.__Variables)):
                if self.__Variables[i].getName() == name:
                    del self.__Variables[i] 
                    self.__sort__()
                    return 
        if not (index == None) and (name == None):
            if (len(self.__Variables) > 0) and (index < len(self.__Variables)):
                del self.__Variables[index]
                self.__sort__()

    def save(self, directory, project, extension):
        """
        Save a CFile.

           Args:
               * directory (str): Root directory of the overgiven project.
               * project (Project): Project, which contain the CExtension.
               * extension (CExtension): CExtension, which contain this CFile.
        """
        Utilities.makeDirectory(directory + os.sep + extension.getName() + '_' +  self.getName() + '@c_ext')
        Utilities.writeToFile(self.__generateBasePluginXML__(project, extension), 
                              directory + os.sep + extension.getName() + '_' +  self.getName() + '@c_ext' + os.sep + 'baseconfnode.xml')
        Utilities.writeToFile(self.__generatePluginXML__(), 
                              directory + os.sep + extension.getName() + '_' +  self.getName() + '@c_ext' + os.sep + 'confnode.xml')
        Utilities.writeToFile(self.__generateCFileXML__(project, extension), 
                             directory + os.sep + extension.getName() + '_' +  self.getName() + '@c_ext' + os.sep + 'cfile.xml')
            
    def __generateCFileXML__(self, project, extension):
        """
        Generate the string for the file "cfile.xml".

           Args:
               * project (Project): Project, which contain the CExtension.
               * extension (CExtension): CExtension, which contain this CFile.
            
           Returns:
                String for the file "cfile.xml" (str).
        """
        ccode = extension.generateCCode(project, self)
        xml = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        xml += '<CFile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.w3.org/2001/XMLSchema" xsi:schemaLocation="cext_xsd.xsd">\n'
        xml += '  <includes>\n'
        xml += '<![CDATA[\n'
        xml += ccode.getIncludeCode()
        xml += ']]>\n'
        xml += '  </includes>\n'
        xml += self.__generateVariablesXML__()
        xml += '  <globals>\n'
        xml += '<![CDATA[\n'
        xml += ccode.getGlobalCode()
        xml += ']]>\n'
        xml += '  </globals>\n'
        xml += '  <initFunction>\n'
        xml += '<![CDATA[\n'
        xml += ccode.getInitializeCode()
        xml += ']]>\n'
        xml += '  </initFunction>\n'
        xml += '  <cleanUpFunction>\n'
        xml += '<![CDATA[\n'
        xml += ccode.getCleanUpCode()
        xml += ']]>\n'
        xml += '  </cleanUpFunction>\n'
        xml += '  <retrieveFunction>\n'
        xml += '<![CDATA[\n'
        xml += ccode.getRetrieveCode() 
        xml += ']]>\n'
        xml += '  </retrieveFunction>\n'
        xml += '  <publishFunction>\n'
        xml += '<![CDATA[\n'
        xml += ccode.getPublishCode()
        xml += ']]>\n'
        xml += '  </publishFunction>\n'
        xml += '</CFile>'
        xml = Libraries.Instance().replaceHeaders(xml)
        return xml
        
    def generateCCode(self, extension):
        ccode = extension.generateCCode(None, self)
        return ccode.getCode()
        
    def __generateBasePluginXML__(self, project, extension):
        """
        Generate the string for the file "baseplugin.xml".

           Args:
               * cfile_nr (str): Number for this CFile.
            
           Returns:
                String for the file "baseplugin.xml" (str).
        """
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<BaseParams Name=' + '"' + extension.getName() + '_' + self.getName() + '"'
        xml += ' IEC_Channel='  + '"' + str(project.getRealCExtensionNumber(extension.getName(), self.getName())) + '"' + '/>'
        return xml
        
    def __generatePluginXML__(self):
        """
        Generate the string for the file "plugin.xml".

           Args:
               * cfile_nr (str): Number for this CFile.
            
           Returns:
                String for the file "plugin.xml" (str).
        """
        xml =  '<?xml version="1.0" encoding="UTF-8"?>\n'
        #if sys.platform == 'win32':
        #    xml += '<CExtension CFLAGS="-lws2_32" LDFLAGS="-lws2_32"/>'
        #else:
        xml += '<CExtension CFLAGS="" LDFLAGS=""/>'
        return xml
        
    def __generateVariablesXML__(self):
        """
        Generate the XML-content of the variables.
            
           Returns:
                XML-content of the variables (str).
        """
        xml = '  <variables>\n'
        for var in self.__Variables:
            xml += '    <variable name="' + var.getName() + '" type="' + var.getDataType() +'" class="' + var.getMemoryType().lower() + '"/>\n'
        xml +='  </variables>\n'
        return xml
        
class Tagging(object):
    
    def __init__(self):
        pass
    
    def extractCode(self, code, tag, indent = 0):
        return self.__extractCode__(code, tag, indent = indent)
        
    def __extractCode__(self, code, tag, indent = 0):
        if self.hasTag(code, tag, indent) == False:
            return ''
        splitter1 = ''
        splitter2 = ''#'\n'
        for i in range(indent):
            splitter1 += Preferences.CCodeIndent
            splitter2 += Preferences.CCodeIndent
        splitter1 += '// <' + tag + '>\n'
        splitter2 += '// </' + tag + '>'
        l1 = code.split(splitter1)
        l2 = l1[1].split(splitter2)
        return l2[0]
        
    def hasTag(self, code, tag, indent = 0):
        has = True
        splitter1 = ''
        splitter2 = '\n'
        for i in range(indent):
            splitter1 += Preferences.CCodeIndent
            splitter2 += Preferences.CCodeIndent
        splitter1 += '// <' + tag + '>\n'
        splitter2 += '// </' + tag + '>'
        if (code.find(splitter1) == -1) or (code.find(splitter2) == -1):
            has = False
        return has
        
    def hasTags(self, code):
        return self.__hasTags__(code)
        
    def __hasTags__(self, code):
        return False
        
    def betweenTags(self, code, cursor = -1):
        return self.__betweenTags__(code, cursor)
        
    def __betweenTags__(self, code, cursor = -1):
        return False
        
    def __betweenTag__(self, code, tag, indent = 0, cursor = -1):
        if self.hasTag(code, tag, indent = indent) == True:
            splitter1 = ''
            splitter2 = '\n'
            for i in range(indent):
                splitter1 += Preferences.CCodeIndent
                splitter2 += Preferences.CCodeIndent
            splitter1 += '// <' + tag + '>\n'
            splitter2 += '// </' + tag + '>'
            a = code.find(splitter1) + len(splitter1)
            b = code.find(splitter2)
            if (cursor[0] >= a) and (cursor[0] <= b) and (cursor[1] >= a) and (cursor[1] <= b):
                return True
        return False
           
    def generateTag(self, tag, indent = 0, insertCode = '\n'):
        ic = insertCode
        t = ''
        if ic == '':
            for i in range(indent):
                ic += Preferences.CCodeIndent
        for i in range(indent):
            t += Preferences.CCodeIndent
        t += '// <%%TAG%%>\n'
        t += ic
        t += '\n'
        for i in range(indent):
            t += Preferences.CCodeIndent
        t += '// </%%TAG%%>'
        return t.replace('%%TAG%%', tag)
     
class CExtension(Object, Tagging):
    class Type(object):
        Composition = 'Composition'
        Shield = 'Shield'
        ModbusDevice = 'ModbusDevice'
        SPIDevice = 'SPIDevice'
        I2CDevice = 'I2CDevice'
        TargetDevice = 'TargetDevice'
        
    def __init__(self, name = None):
        Object.__init__(self)
        Tagging.__init__(self)
        self.__Name = name
        self.__Type = ''
        self.__CFiles = range(0, 0)
        self.__DeviceName = ''
               
    def getName(self):
        return self.__Name
    
    def setName(self, name):
        self.__Name = name
        
    def getDeviceName(self):
        return self.__DeviceName
    
    def __setDeviceName__(self, name):
        self.__DeviceName = name
        
    def getType(self):
        return self.__Type
        
    def addCFile(self, name = None, instance = None):
        if not (name == None) and (instance == None):
            if not self.existCFile(name) and not (name == ''):
                cfile = CFile(name = name)
                self.__CFiles.append(cfile)
                return cfile
        if (name == None) and not (instance == None):
            if not self.existCFile(instance.getName()) and not (instance.getName() == ''):
                self.__CFiles.append(instance)
                return instance
        return None

    def existCFile(self, name):
        if not (name == None):
            for cfile in self.__CFiles:
                if cfile.getName() == name:
                    return True
            return False
        else:
            return False
            
    def setCFile(self, name = None, index = None, cfile = None):
        if not (cfile == None):
            if not (name == None) and (index == None):
                for i in range(len(self.__CFiles)):
                    if self.__CFiles[i].getName() == name:
                        self.__CFiles[i] = cfile
            if not (index == None) and (name == None):
                if (len(self.__CFiles) > 0) and (index < len(self.__CFiles)):
                    self.__CFiles[index] = cfile

    def getCFile(self, name = None, index = None):
        if not (name == None) and (index == None):
            for cfile in self.__CFiles:
                if cfile.getName() == name:
                    return cfile.clone()
        if not (index == None) and (name == None):
            if (len(self.__CFiles) > 0) and (index < len(self.__CFiles)):
                return self.__CFiles[index].clone()
        return None
    
    def getCFiles(self):
        return self.__CFiles
        
    def countCFiles(self):
        return len(self.__CFiles)
        
    def listCFiles(self):
        l = range(0, 0)
        for i in range(len(self.__CFiles)):
            l.append(self.__CFiles[i].getName())
        return l

    def removeCFile(self, name = None, index = None):
        if not (name == None) and (index == None):
            for i in range(len(self.__CFiles)):
                if self.__CFiles[i].getName() == name:
                    del self.__CFiles[i] 
                    return 
        if not (index == None) and (name == None):
            if (len(self.__CFiles) > 0) and (index < len(self.__CFiles)):
                del self.__CFiles[index]
    
    def getCFileNumber(self, name):
        if not (name == None):
            for i in range(len(self.__CFiles)):
                if self.__CFiles[i].getName() == name:
                    return  i
        return 65535
    
    def save(self, directory, project):
        for i in range(len(self.__CFiles)):
            self.__CFiles[i].save(directory, project, self)
    
    def __generateBasePluginXML__(self, project):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<BaseParams Name=' + '"' + self.getName() + '"'
        xml += ' IEC_Channel='  + '"' + str(project.getCExtensionNumber(self.getName())) + '"' + '/>'
        return xml
        
    def generateCCode(self, project, cfile):
        return self.__generateCCode__(project, cfile)
    
    def __generateCCode__(self, project, cfile):
        return cfile
        
class Composition(CExtension):
    def __init__(self, name = None, project = None):
        CExtension.__init__(self, name)
        self.__Project = project
        self.__TargetDevice = project.getTargetDevice()
        Libraries.Instance().setTargetDevice(self.__TargetDevice)
        libs = self.__TargetDevice.getLibraries()
        for lib in libs:
            contents =  Libraries.Instance().getLibrary(lib).listContents()
            for c in contents:
                cf = CFile(name = lib + '_' + c)
                cf.setGlobalCode(Libraries.Instance().getLibrary(lib).getContent(c, project.getTargetDevice().getTargetHeaderCode()))
                self.addCFile(instance = cf)
                
        #self.addCFile(instance = self.__TargetDevice.getCFile(index = 0))
                
        cfile = self.addCFile(name = 'Information')
        cfile.addVariable(name = 'LastCycleTime', memoryType = MemoryTypes.Input, dataType = DataTypes.UINT)
        cfile.addVariable(name = 'AverageCycleTime', memoryType = MemoryTypes.Input, dataType = DataTypes.UINT)
        self.__Type = CExtension.Type.Composition
        
    def generateCCode(self, project, cfile):
        ccode = CCode()
        if cfile.getName() == 'Information':
            includeCode = '#include "EsPeEs.h"\n'
            globalCode = ''
            initializeCode = ''
            retrieveCode = ''
            publishCode = ''
            cleanupCode = ''
            
            retrieveCode += 'EsPeEs_start_cycle();\n'
            
            modbusInterfaces = project.getModbusInterfaces()
            modbusDevices = project.getModbusDevices()
            spiDevices = project.getSPIDevices()
            i2cDevices = project.getI2CDevices()
            
            shield = project.getShield()
            cfiles = shield.getCFiles()
            for h in range(len(cfiles)):
                retrieveCode += 'EsPeEs_Shield_retrieve_' + str(project.getCExtensionNumber(shield.getName())) + '_' + str(h) + '();\n'
                publishCode += 'EsPeEs_Shield_publish_' + str(project.getCExtensionNumber(shield.getName())) + '_' + str(h) + '();\n'
                globalCode += 'void EsPeEs_Shield_retrieve_' + str(project.getCExtensionNumber(shield.getName())) + '_' + str(h) + '();\n'
                globalCode += 'void EsPeEs_Shield_publish_' + str(project.getCExtensionNumber(shield.getName())) + '_' + str(h) + '();\n'
            
            for i in range(len(modbusInterfaces)):
                globalCode += 'EsPeEs_modbus_interface_t *_ModbusInterface_' + str(i) + ';\n'
                if modbusInterfaces[i].getMode() == Modbus.Modes.RTU:
                    initializeCode += '_ModbusInterface_' + str(i) + ' = EsPeEs_modbus_interface_rtu("' + modbusInterfaces[i].getSerialPort() + '");\n'
                if modbusInterfaces[i].getMode() == Modbus.Modes.TCP:
                    initializeCode += '_ModbusInterface_' + str(i) + ' = EsPeEs_modbus_interface_tcp("' + modbusInterfaces[i].getTCPAdress() + '", ' + str(modbusInterfaces[i].getTCPPort()) + ');\n'
                    
            for i in range(len(modbusDevices)):
                cfiles = modbusDevices[i].getCFiles()
                globalCode += 'EsPeEs_modbus_device_t* _ModbusDevice_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + ';\n'
                initializeCode += '_ModbusDevice_' + str(project.getCExtensionNumber(modbusDevices[i].getName()))
                initializeCode += ' = EsPeEs_modbus_device("' + modbusDevices[i].getName() + '", _ModbusInterface_'
                initializeCode += str(project.getModbusInterfaceNumber(modbusDevices[i].getModbusInterface().getName())) + ', ' + str(modbusDevices[i].getAdress())
                initializeCode += ', ' + str(modbusDevices[i].getRegisterSize()) + ');\n'
                retrieveCode += 'EsPeEs_modbus_read_registers(_ModbusDevice_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + ');\n'
                for h in range(len(cfiles)):
                    retrieveCode += 'EsPeEs_ModbusDevice_retrieve_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + '_' + str(h) + '(' + '_ModbusDevice_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + '->Registers);\n'
                    publishCode += 'EsPeEs_ModbusDevice_publish_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + '_' + str(h) + '(' + '_ModbusDevice_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + '->Registers);\n'
                    globalCode += 'void EsPeEs_ModbusDevice_retrieve_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + '_' + str(h) + '(uint16_t *Registers);\n'
                    globalCode += 'void EsPeEs_ModbusDevice_publish_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + '_' + str(h) + '(uint16_t *Registers);\n'
                publishCode += 'EsPeEs_modbus_write_registers(_ModbusDevice_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + ');\n'
                cleanupCode += 'EsPeEs_modbus_device_free(_ModbusDevice_' + str(project.getCExtensionNumber(modbusDevices[i].getName())) + ');\n'
                
            for i in range(len(spiDevices)):
                cfiles = spiDevices[i].getCFiles()
                for h in range(len(cfiles)):
                    retrieveCode += 'EsPeEs_SPIDevice_retrieve_' + str(project.getCExtensionNumber(spiDevices[i].getName())) + '_' + str(h) + '();\n'
                    publishCode += 'EsPeEs_SPIDevice_publish_' + str(project.getCExtensionNumber(spiDevices[i].getName())) + '_' + str(h) + '();\n'
                    globalCode += 'void EsPeEs_SPIDevice_retrieve_' + str(project.getCExtensionNumber(spiDevices[i].getName())) + '_' + str(h) + '();\n'
                    globalCode += 'void EsPeEs_SPIDevice_publish_' + str(project.getCExtensionNumber(spiDevices[i].getName())) + '_' + str(h) + '();\n'
                cleanupCode += 'EsPeEs_spi_device_free(_ModbusDevice_' + str(project.getCExtensionNumber(spiDevices[i].getName())) + ');\n'
                    
            for i in range(len(i2cDevices)):
                cfiles = i2cDevices[i].getCFiles()
                for h in range(len(cfiles)):
                    retrieveCode += 'EsPeEs_I2CDevice_retrieve_' + str(project.getCExtensionNumber(i2cDevices[i].getName())) + '_' + str(h) + '();\n'
                    publishCode += 'EsPeEs_I2CDevice_publish_' + str(project.getCExtensionNumber(i2cDevices[i].getName())) + '_' + str(h) + '();\n'
                    globalCode += 'void EsPeEs_I2CDevice_retrieve_' + str(project.getCExtensionNumber(i2cDevices[i].getName())) + '_' + str(h) + '();\n'
                    globalCode += 'void EsPeEs_I2CDevice_publish_' + str(project.getCExtensionNumber(i2cDevices[i].getName())) + '_' + str(h) + '();\n'
                cleanupCode += 'EsPeEs_i2c_device_free(_ModbusDevice_' + str(project.getCExtensionNumber(i2cDevices[i].getName())) + ');\n'
                
            for i in range(len(modbusInterfaces)):
                cleanupCode += 'EsPeEs_modbus_interface_free(_ModbusInterface_' + str(i) + ');\n'
                
            publishCode += 'EsPeEs_stop_cycle();\n'
            publishCode += 'LastCycleTime = EsPeEs_last_cycle_time();\n'
            publishCode += 'AverageCycleTime = EsPeEs_average_cycle_time();\n'
                
            ccode.setCode(includeCode, globalCode, initializeCode, cleanupCode, retrieveCode, publishCode)
        else:
            ccode.setCode('', cfile.getCode(), '', '', '', '')
        return ccode

class Shield(CExtension):
    def __init__(self, name = None, modbusCompatible = False, spiCompatible = False, i2cCompatible = False):
        CExtension.__init__(self, name)
        self.__ModbusCompatible = modbusCompatible
        self.__SPICompatible = spiCompatible
        self.__I2CCompatible = i2cCompatible
        self.__SPICode = ''
        self.__I2CReadCode = ''
        self.__I2CWriteCode = ''
        self.__I2CSetupCode = ''
        self.__Type = CExtension.Type.Shield
        
    def isModbusCompatible(self):
        return self.__ModbusCompatible
    
    def isSPICompatible(self):
        return self.__SPICompatible
    
    def isI2CCompatible(self):
        return self.__I2CCompatible
        
    def setModbusCompability(self, compability):
        self.__ModbusCompatible = compability
        
    def setSPICompability(self, compability):
        self.__SPICompatible = compability
        
    def setI2CCompability(self, compability):
        self.__I2CCompatible = compability
        
    def __generateCCode__(self, project, cfile):
        cextNr = 0
        if not (project == None):
            cextNr = project.getCExtensionNumber(self.getName())
        includeCode = ''
        includeCode += '#include "EsPeEs.h"\n\n'
        includeCode += self.generateTag('IncludeCode', indent = 0, insertCode = cfile.getIncludeCode()) + '\n'
        globalCode = ''
        globalCode += self.generateTag('GlobalCode', indent = 0, insertCode = cfile.getGlobalCode()) + '\n\n'
        globalCode += 'void EsPeEs_Shield_retrieve_' + str(cextNr) + '_' + str(self.getCFileNumber(cfile.getName())) + '()\n{\n'
        globalCode += self.generateTag('RetrieveCode', indent = 1, insertCode = cfile.getRetrieveCode()) + '\n'
        globalCode += '}\n\nvoid EsPeEs_Shield_publish_' + str(cextNr) + '_' + str(self.getCFileNumber(cfile.getName())) + '()\n{\n'
        globalCode += self.generateTag('PublishCode', indent = 1, insertCode = cfile.getPublishCode()) + '\n'
        globalCode += '}'
        ccode = CCode()
        ccode.setCode(includeCode, globalCode, '', '', '', '')
        return ccode
        
    def __betweenTags__(self, code, cursor = -1):
        between = False
        if self.__betweenTag__(code, 'IncludeCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'GlobalCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'RetrieveCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'PublishCode', indent = 1, cursor = cursor) == True:
            between = True
        return between
        
    def __hasTags__(self, code):
        has = True
        if self.hasTag(code, 'IncludeCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'GlobalCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'RetrieveCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'PublishCode', indent = 1) == False:
            has = False
        return has
        
    def getType(self):
        return self.__Type

class Register(Object):
    def __init__(self):
        self.__Registers = range(0, 0)
        Object.__init__(self)
    
    def addRegister(self, name):
        if self.existRegister(name) == False:
            self.__Registers.append(name)
    
    def removeRegister(self, name):
        for i in range(len(self.__Registers)):
            if self.__Registers[i] == name:
                del self.__Registers[i]
                return        
                
    def renameRegister(self, name, newName):
        if self.existRegister(newName) == False:
            for i in range(len(self.__Registers)):
                if self.__Registers[i] == name:
                    self.__Registers[i] = newName
                    return   
        
    def moveUpRegister(self, name):
        if self.canMoveUpRegister(name) == True:
            oldIndex = self.getRegisterIndex(name)
            newIndex = oldIndex - 1
            temp = self.__Registers[newIndex]
            self.__Registers[newIndex] = self.__Registers[oldIndex]
            self.__Registers[oldIndex] = temp
        
    def moveDownRegister(self, name):
        if self.canMoveDownRegister(name) == True:
            oldIndex = self.getRegisterIndex(name)
            newIndex = oldIndex + 1
            temp = self.__Registers[newIndex]
            self.__Registers[newIndex] = self.__Registers[oldIndex]
            self.__Registers[oldIndex] = temp
        
    def getRegisterIndex(self, name):
        index = -1
        for i in range(len(self.__Registers)):
            if self.__Registers[i] == name:
                index = i
                break
        return i
        
    def canMoveDownRegister(self, name):
        if self.existRegister(name) == True:
            if  self.getRegisterIndex(name) < (len(self.__Registers) - 1):
                return True
        return False
        
    def canMoveUpRegister(self, name):
        if self.existRegister(name) == True:
            if self.getRegisterIndex(name) > 0:
                return True
        return False
        
    def existRegister(self, name):
        for i in range(len(self.__Registers)):
            if self.__Registers[i] == name:
                return True
        return False
        
    def getRegisters(self):
        l = range(0, 0)
        for reg in self.__Registers:
            l.append(reg)
        return l
        
    def setRegisters(self, registers):
        self.__Registers = registers
        
    def getRegisterSize(self):
        return len(self.__Registers)
        
class ModbusDevice(CExtension):
    def __init__(self, name = None, adress = 255, registerCode = '', registerSize = 0):
        CExtension.__init__(self, name)
        self.__Register = Register()
        self.__ModbusInterface = None
        self.__Adress = adress
        self.__Type = CExtension.Type.ModbusDevice
               
    def getAdress(self):
        return self.__Adress
        
    def getRegisterCode(self):
        registers = self.__Register.getRegisters()
        code = 'enum\n{'
        for i in range(len(registers)):
            code += '\n    ' + registers[i] + ','
        code += '\n    LastCycleTime,\n    AverageCycleTime,\n    TotalTimeouts,\n    TotalErrors,\n    TotalRegisterSize\n};\n'
        return code
    
    def getModbusInterface(self):
        if not (self.__ModbusInterface == None):
            return self.__ModbusInterface
        else:
            return Modbus.Interface()
    
    def setAdress(self, adress):
        self.__Adress = adress
        
    def setModbusInterface(self, modbus):
        self.__ModbusInterface = modbus
        
    def __generateCCode__(self, project, cfile):
        cextNr = 0
        if not (project == None):
            cextNr = project.getCExtensionNumber(self.getName())
        includeCode = ''
        includeCode += '#include "EsPeEs.h"\n\n'
        includeCode += self.generateTag('IncludeCode', indent = 0, insertCode = cfile.getIncludeCode()) + '\n'
        globalCode = ''
        globalCode += self.getRegisterCode() + '\n'
        globalCode += self.generateTag('GlobalCode', indent = 0, insertCode = cfile.getGlobalCode()) + '\n\n'
        globalCode += 'void EsPeEs_ModbusDevice_retrieve_' + str(cextNr) + '_' + str(self.getCFileNumber(cfile.getName())) + '(uint16_t *Registers)\n{\n'
        globalCode += self.generateTag('RetrieveCode', indent = 1, insertCode = cfile.getRetrieveCode()) + '\n'
        globalCode += '}\n\nvoid EsPeEs_ModbusDevice_publish_' + str(cextNr) + '_' + str(self.getCFileNumber(cfile.getName())) + '(uint16_t *Registers)\n{\n'
        globalCode += self.generateTag('PublishCode', indent = 1, insertCode = cfile.getPublishCode()) + '\n'
        globalCode += '}'
        ccode = CCode()
        ccode.setCode(includeCode, globalCode, '', '', '', '')
        return ccode
        
    def __betweenTags__(self, code, cursor = -1):
        between = False
        if self.__betweenTag__(code, 'IncludeCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'GlobalCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'RetrieveCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'PublishCode', indent = 1, cursor = cursor) == True:
            between = True
        return between
        
    def __hasTags__(self, code):
        has = True
        if self.hasTag(code, 'IncludeCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'GlobalCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'RetrieveCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'PublishCode', indent = 1) == False:
            has = False
        return has
                                
    def getType(self):
        return self.__Type
        
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
        registers.append('LastCycleTime')
        registers.append('AverageCycleTime')
        registers.append('TotalTimeouts')
        registers.append('TotalErrors')
        registers.append('TotalRegisterSize')
        return registers
        
    def setRegisters(self, registers):
        del_regs = range(0, 0)
        for i in range(len(registers)): 
            if (registers[len(registers) - 1 - i] == 'LastCycleTime') or(registers[len(registers) - 1 - i] == 'AverageCycleTime') or (registers[len(registers) - 1 - i] == 'TotalTimeouts') or (registers[len(registers) - 1 - i] == 'TotalErrors') or (registers[len(registers) - 1 - i] == 'TotalRegisterSize'):
                del registers[len(registers) - 1 - i]
        self.__Register.setRegisters(registers)
        
    def getRegisterSize(self):
        return self.__Register.getRegisterSize() + 3
    
class SPIDevice(CExtension):
    def __init__(self, name = None, adress = 0):
        CExtension.__init__(self, name)
        self.__Adress = adress
        self.__Type = CExtension.Type.SPIDevice
    
    def getAdress(self):
        return self.__Adress
            
    def setAdress(self, adress):
        self.__Adress = adress
        
    def __generateCCode__(self, project, cfile):
        cextNr = 0
        if not (project == None):
            cextNr = project.getCExtensionNumber(self.getName())
        includeCode = ''
        includeCode += '#include "EsPeEs.h"\n\n'
        includeCode += self.generateTag('IncludeCode', indent = 0, insertCode = cfile.getIncludeCode()) + '\n'
        includeCode += '\nAdress = ' + str(self.getAdress()) + ';\n'
        globalCode = ''
        globalCode += self.generateTag('GlobalCode', indent = 0, insertCode = cfile.getGlobalCode()) + '\n\n'
        globalCode += 'void EsPeEs_SPIDevice_retrieve_' + str(cextNr) + '_' + str(self.getCFileNumber(cfile.getName())) + '()\n{\n'
        globalCode += self.generateTag('RetrieveCode', indent = 1, insertCode = cfile.getRetrieveCode()) + '\n'
        globalCode += '}\n\nvoid EsPeEs_SPIDevice_publish_' + str(cextNr) + '_' + str(self.getCFileNumber(cfile.getName())) + '()\n{\n'
        globalCode += self.generateTag('PublishCode', indent = 1, insertCode = cfile.getPublishCode()) + '\n'
        globalCode += '}'
        ccode = CCode()
        ccode.setCode(includeCode, globalCode, '', '', '', '')
        return ccode
        
    def __betweenTags__(self, code, cursor = -1):
        between = False
        if self.__betweenTag__(code, 'IncludeCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'GlobalCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'RetrieveCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'PublishCode', indent = 1, cursor = cursor) == True:
            between = True
        return between
        
    def __hasTags__(self, code):
        has = True
        if self.hasTag(code, 'IncludeCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'GlobalCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'RetrieveCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'PublishCode', indent = 1) == False:
            has = False
        return has
        
    def getType(self):
        return self.__Type
    
class I2CDevice(CExtension):
    def __init__(self, name = None, adress = 255):
        CExtension.__init__(self, name)
        self.__Adress = adress
        self.__Type = CExtension.Type.I2CDevice
        self.__HasSubAdress = False
        self.__SubAdress = -1
        self.__HasTenBitAdress = False
        
    def getAdress(self):
        if self.hasSubAdress() == True:
            return self.__Adress
        else:
            return self.__Adress
            
    def setAdress(self, adress):
        self.__Adress = adress
        
    def hasTenBitAdress(self):
        return self.__HasTenBitAdress
           
    def setHasTenBitAdress(self, hasTenBitAdress):
        self.__HasTenBitAdress = hasTenBitAdress
        
    def hasSubAdress(self):
        return self.__HasSubAdress
        
    def setHasSubAdress(self, hasSubAdress):
        self.__HasSubAdress = hasSubAdress
           
    def getSubAdress(self):
        return self.__SubAdress
            
    def setSubAdress(self, subAdress):
        self.__SubAdress = subAdress
                
    def __generateCCode__(self, project, cfile):
        cextNr = 0
        if not (project == None):
            cextNr = project.getCExtensionNumber(self.getName())
        includeCode = ''
        includeCode += '#include "EsPeEs.h"\n\n'
        includeCode += self.generateTag('IncludeCode', indent = 0, insertCode = cfile.getIncludeCode()) + '\n'
        includeCode += '\nint Adress = ' + str(self.getAdress()) + ';\n' 
        globalCode = ''
        globalCode += self.generateTag('GlobalCode', indent = 0, insertCode = cfile.getGlobalCode()) + '\n\n'
        globalCode += 'void EsPeEs_I2CDevice_retrieve_' + str(cextNr) + '_' + str(self.getCFileNumber(cfile.getName())) + '()\n{\n'
        globalCode += self.generateTag('RetrieveCode', indent = 1, insertCode = cfile.getRetrieveCode()) + '\n'
        globalCode += '}\n\nvoid EsPeEs_I2CDevice_publish_' + str(cextNr) + '_' + str(self.getCFileNumber(cfile.getName())) + '()\n{\n'
        globalCode += self.generateTag('PublishCode', indent = 1, insertCode = cfile.getPublishCode()) + '\n'
        globalCode += '}'
        ccode = CCode()
        ccode.setCode(includeCode, globalCode, '', '', '', '')
        return ccode
        
    def __betweenTags__(self, code, cursor = -1):
        between = False
        if self.__betweenTag__(code, 'IncludeCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'GlobalCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'RetrieveCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'PublishCode', indent = 1, cursor = cursor) == True:
            between = True
        return between
        
    def __hasTags__(self, code):
        has = True
        if self.hasTag(code, 'IncludeCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'GlobalCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'RetrieveCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'PublishCode', indent = 1) == False:
            has = False
        return has
        
    def getType(self):
        return self.__Type
    
class TargetDevice(CExtension):
    def __init__(self, name = None, target = None, libraries = None, modbusCompatible = False, spiCompatible = False, i2cCompatible = False):
        CExtension.__init__(self, name)
        self.__Type = CExtension.Type.TargetDevice
        self.__Target = target
        self.__ModbusCompatible = modbusCompatible
        self.__SPICompatible = spiCompatible
        self.__I2CCompatible = i2cCompatible
        self.__Libraries = libraries
        self.__ModbusInterfaceRTUCode = ''
        self.__ModbusInterfaceTCPCode = ''
        self.__ModbusDeviceCode = ''
        self.__ModbusInterfaceFreeCode = ''
        self.__ModbusReadRegisterCode = ''
        self.__ModbusWriteRegisterCode = ''
        self.__SPIInterfaceCode = ''
        self.__SPIDeviceCode = ''
        self.__SPIInterfaceFreeCode = ''
        self.__SPITransmitCode = ''
        self.__I2CInterfaceCode = ''
        self.__I2CDeviceCode = ''
        self.__I2CInterfaceFreeCode = ''
        self.__I2CReadCode = ''
        self.__I2CWriteCode = ''
        self.__StartCycleCode = ''
        self.__StopCycleCode = ''
        self.__AverageCycleTimeCode = ''
        self.__LastCycleTimeCode = ''
        self.__ModbusInterfaceStructCode = ''
        self.__SPIInterfaceStructCode = ''
        self.__I2CInterfaceStructCode = ''
        
    def isModbusCompatible(self):
        return self.__ModbusCompatible
    
    def isSPICompatible(self):
        return self.__SPICompatible
    
    def isI2CCompatible(self):
        return self.__I2CCompatible
        
    def setModbusCompability(self, compability):
        self.__ModbusCompatible = compability
        
    def setSPICompability(self, compability):
        self.__SPICompatible = compability
        
    def setI2CCompability(self, compability):
        self.__I2CCompatible = compability
        
    def setTarget(self, target):
        if not (target == None):
            self.__Target = target
            
    def getTarget(self):
        return self.__Target
        
    def setLibraries(self, libraries):
        if not (libraries == None):
            self.__Libraries = libraries
            
    def getLibraries(self):
        return self.__Libraries
        
    def setModbusInterfaceRTUCode(self, code):
        self.__ModbusInterfaceRTUCode = code
        
    def getModbusInterfaceRTUCode(self):
        return self.__ModbusInterfaceRTUCode
        
    def setModbusInterfaceTCPCode(self, code):
        self.__ModbusInterfaceTCPCode = code
        
    def getModbusInterfaceTCPCode(self):
        return self.__ModbusInterfaceTCPCode
        
    def setModbusDeviceCode(self, code):
        self.__ModbusDeviceCode = code
        
    def getModbusDeviceCode(self):
        return self.__ModbusDeviceCode
        
    def setModbusInterfaceFreeCode(self, code):
        self.__ModbusInterfaceFreeCode = code
        
    def getModbusInterfaceFreeCode(self):
        return self.__ModbusInterfaceFreeCode
        
    def setModbusReadRegisterCode(self, code):
        self.__ModbusReadRegisterCode = code
        
    def getModbusReadRegisterCode(self):
        return self.__ModbusReadRegisterCode
        
    def setModbusWriteRegisterCode(self, code):
        self.__ModbusWriteRegisterCode = code
        
    def getModbusWriteRegisterCode(self):
        return self.__ModbusWriteRegisterCode
        
    def setSPIInterfaceCode(self, code):
        self.__SPIInterfaceCode = code
        
    def getSPIInterfaceCode(self):
        return self.__SPIInterfaceCode
        
    def setSPIDeviceCode(self, code):
        self.__SPIDeviceCode = code
        
    def getSPIDeviceCode(self):
        return self.__SPIDeviceCode
        
    def setSPIInterfaceFreeCode(self, code):
        self.__SPIInterfaceFreeCode = code
        
    def getSPIInterfaceFreeCode(self):
        return self.__SPIInterfaceFreeCode
        
    def setSPITransmitCode(self, code):
        self.__SPITransmitCode = code
        
    def getSPITransmitCode(self):
        return self.__SPITransmitCode
        
    def setI2CInterfaceCode(self, code):
        self.__I2CInterfaceCode = code
        
    def getI2CInterfaceCode(self):
        return self.__I2CInterfaceCode
        
    def setI2CDeviceCode(self, code):
        self.__I2CDeviceCode = code
        
    def getI2CDeviceCode(self):
        return self.__I2CDeviceCode
        
    def setI2CInterfaceFreeCode(self, code):
        self.__I2CInterfaceFreeCode = code
        
    def getI2CInterfaceFreeCode(self):
        return self.__I2CInterfaceFreeCode
        
    def setI2CReadCode(self, code):
        self.__I2CReadCode = code
        
    def getI2CReadCode(self):
        return self.__I2CReadCode
        
    def setI2CWriteCode(self, code):
        self.__I2CWriteCode = code
        
    def getI2CWriteCode(self):
        return self.__I2CWriteCode
        
    def setStartCycleCode(self, code):
        self.__StartCycleCode = code
        
    def getStartCycleCode(self):
        return self.__StartCycleCode
        
    def setStopCycleCode(self, code):
        self.__StopCycleCode = code
        
    def getStopCycleCode(self):
        return self.__StopCycleCode
        
    def setAverageCycleTimeCode(self, code):
        self.__AverageCycleTimeCode = code
        
    def getAverageCycleTimeCode(self):
        return self.__AverageCycleTimeCode
        
    def setLastCycleTimeCode(self, code):
        self.__LastCycleTimeCode = code
        
    def getLastCycleTimeCode(self):
        return self.__LastCycleTimeCode
        
    def setModbusInterfaceStructCode(self, code):
        self.__ModbusInterfaceStructCode = code
        
    def getModbusInterfaceStructCode(self):
        return self.__ModbusInterfaceStructCode
        
    def setSPIInterfaceStructCode(self, code):
        self.__SPIInterfaceStructCode = code
        
    def getSPIInterfaceStructCode(self):
        return self.__SPIInterfaceStructCode
        
    def setI2CInterfaceStructCode(self, code):
        self.__I2CInterfaceStructCode = code
        
    def getI2CInterfaceStructCode(self):
        return self.__I2CInterfaceStructCode
        
    def getTargetHeaderCode(self):
        globalCode = ''
        if self.getTarget() == Targets.Windows:
            globalCode += '#define EsPeEs_Windows\n'
        if (self.getTarget() == Targets.Linux32Bit) or (self.getTarget() == Targets.Linux64Bit) or (self.getTarget() == Targets.RaspberryPi):
            globalCode += '#define EsPeEs_Linux\n'
        return globalCode
        
    def getHeaderCode(self):
        globalCode = ''
        if self.getTarget() == Targets.Windows:
            globalCode += '#define EsPeEs_Windows\n'
        if (self.getTarget() == Targets.Linux32Bit) or (self.getTarget() == Targets.Linux64Bit) or (self.getTarget() == Targets.RaspberryPi):
            globalCode += '#define EsPeEs_Linux\n'
        globalCode += '#ifndef _ESPEES_H_\n'
        globalCode += '#define _ESPEES_H_\n'
        globalCode += '\n'
        globalCode += '#include <stdbool.h>\n'
        globalCode += '#include <stdint.h>\n'
        globalCode += '#include <stdio.h>\n'
        globalCode += '#include <stdlib.h>\n'
        globalCode += self.generateTag('IncludeCode', indent = 0, insertCode = self.getCFile(index = 0).getIncludeCode()) + '\n'
        globalCode += '\n'
        globalCode += '\n'
        globalCode += '\n'
        globalCode += '// Modbus-interface struct.\n'
        globalCode += 'struct EsPeEs_modbus_interface_t_struct {\n'
        globalCode += '    char *Name;\n'
        globalCode += '    char *SerialPort;\n'
        globalCode += '    char *IPAdress;\n'
        globalCode += '    int Port;\n'
        globalCode += '    int Connected;\n'
        globalCode += self.generateTag('ModbusInterfaceStructCode', indent = 1, insertCode = self.getModbusInterfaceStructCode()) + '\n'
        globalCode += '};\n'
        globalCode += '\n'
        globalCode += '// Spi-interface struct.\n'
        globalCode += 'struct EsPeEs_spi_interface_t_struct {\n'
        globalCode += '    char *Name;\n'
        globalCode += self.generateTag('SPIInterfaceStructCode', indent = 1, insertCode = self.getSPIInterfaceStructCode()) + '\n'
        globalCode += '};\n'
        globalCode += '\n'
        globalCode += '// I2C-interface struct.\n'
        globalCode += 'struct EsPeEs_i2c_interface_t_struct {\n'
        globalCode += '    char *Name;\n'
        globalCode += self.generateTag('I2CInterfaceStructCode', indent = 1, insertCode = self.getI2CInterfaceStructCode()) + '\n'
        globalCode += '};\n'
        globalCode += '\n'
        globalCode += 'struct EsPeEs_modbus_device_t_struct {\n'
        globalCode += '	char *Name;\n'
        globalCode += '	uint8_t Adress;\n'
        globalCode += '	uint16_t *Registers;\n'
        globalCode += '	uint8_t Size;\n'
        globalCode += '	struct EsPeEs_modbus_interface_t_struct *ModbusInterface;\n'
        globalCode += '};\n'
        globalCode += '\n'
        globalCode += 'struct EsPeEs_spi_device_t_struct {\n'
        globalCode += '	char *Name;\n'
        globalCode += '	uint8_t Adress;\n'
        globalCode += '    struct EsPeEs_spi_interface_t_struct *SPIInterface;\n'
        globalCode += '};\n'
        globalCode += '\n'
        globalCode += 'struct EsPeEs_i2c_device_t_struct {\n'
        globalCode += '	char *Name;\n'
        globalCode += '	uint8_t Adress;\n'
        globalCode += '    struct EsPeEs_i2c_interface_t_struct *I2CInterface;\n'
        globalCode += '};\n'
        globalCode += '\n'
        globalCode += 'struct EsPeEs_preferences_t_struct {\n'
        globalCode += '	int Baudrate;\n'
        globalCode += '	char Parity;  // "none", "even" or "odd"\n'
        globalCode += '	int DataBit;  // 5, 6, 7, 8\n'
        globalCode += '	int StopBit;  // 0, 1\n'
        globalCode += '	int SPISpeed;\n'
        globalCode += '};\n'
        globalCode += '\n'
        globalCode += 'typedef struct EsPeEs_modbus_interface_t_struct EsPeEs_modbus_interface_t;\n'
        globalCode += 'typedef struct EsPeEs_spi_interface_t_struct EsPeEs_spi_interface_t;\n'
        globalCode += 'typedef struct EsPeEs_i2c_interface_t_struct EsPeEs_i2c_interface_t;\n'
        globalCode += 'typedef struct EsPeEs_modbus_device_t_struct EsPeEs_modbus_device_t;\n'
        globalCode += 'typedef struct EsPeEs_spi_device_t_struct EsPeEs_spi_device_t;\n'
        globalCode += 'typedef struct EsPeEs_i2c_device_t_struct EsPeEs_i2c_device_t;\n'
        globalCode += 'typedef struct EsPeEs_preferences_t_struct EsPeEs_preferences_t;\n'
        globalCode += '\n'
        globalCode += 'EsPeEs_modbus_interface_t* EsPeEs_modbus_interface_rtu(char *minterface);\n'
        globalCode += 'EsPeEs_modbus_interface_t* EsPeEs_modbus_interface_tcp(char *ipadress, int port);\n'
        globalCode += 'EsPeEs_modbus_device_t* EsPeEs_modbus_device(char *name, EsPeEs_modbus_interface_t *minterface, uint8_t adress, uint8_t regsize);\n'
        globalCode += 'void EsPeEs_modbus_interface_free(EsPeEs_modbus_interface_t *minterface);\n'
        globalCode += 'void EsPeEs_modbus_device_free(EsPeEs_modbus_device_t *device);\n'
        globalCode += 'int EsPeEs_modbus_read_registers(EsPeEs_modbus_device_t *device);\n'
        globalCode += 'int EsPeEs_modbus_write_registers(EsPeEs_modbus_device_t *device);\n'
        globalCode += '\n'
        globalCode += 'EsPeEs_spi_interface_t* EsPeEs_spi_interface(char *name);\n'
        globalCode += 'EsPeEs_spi_device_t* EsPeEs_spi_device(char *name, EsPeEs_spi_interface_t *minterface, uint8_t adress);\n'
        globalCode += 'void EsPeEs_spi_interface_free(EsPeEs_spi_interface_t *minterface);\n'
        globalCode += 'void EsPeEs_spi_device_free(EsPeEs_spi_device_t *device);\n'
        globalCode += 'int EsPeEs_spi_transmit(EsPeEs_spi_device_t *device, char *data);\n'
        globalCode += '\n'
        globalCode += 'EsPeEs_i2c_interface_t* EsPeEs_i2c_interface(char *name);\n'
        globalCode += 'EsPeEs_i2c_device_t* EsPeEs_i2c_device(char *name, EsPeEs_i2c_interface_t *minterface, uint8_t adress);\n'
        globalCode += 'void EsPeEs_i2c_interface_free(EsPeEs_i2c_interface_t *minterface);\n'
        globalCode += 'void EsPeEs_i2c_device_free(EsPeEs_i2c_device_t *device);\n'
        globalCode += 'int EsPeEs_i2c_read(EsPeEs_i2c_device_t *device);\n'
        globalCode += 'int EsPeEs_i2c_write(EsPeEs_i2c_device_t *device, int data);\n'
        globalCode += '\n'
        globalCode += 'void EsPeEs_start_cycle();\n'
        globalCode += 'void EsPeEs_stop_cycle();\n'
        globalCode += 'uint16_t EsPeEs_average_cycle_time();\n'
        globalCode += 'uint16_t EsPeEs_last_cycle_time();\n'
        globalCode += '\n'
        globalCode += '#define EsPeEs_bit_read(value, bit) (((value) >> (bit)) & 0x01)\n'
        globalCode += '#define EsPeEs_bit_set(value, bit) ((value) |= (1UL << (bit)))\n'
        globalCode += '#define EsPeEs_bit_clear(value, bit) ((value) &= ~(1UL << (bit)))\n'
        globalCode += '#define EsPeEs_bit_write(value, bit, bitvalue) (bitvalue ? EsPeEs_bit_set(value, bit) : EsPeEs_bit_clear(value, bit))\n'
        globalCode += '\n'
        globalCode += '#endif\n'
        return globalCode
        
    def __generateCCode__(self, project, cfile):
        globalCode = ''
        includeCode = ''
        includeCode += '#include "EsPeEs.h"\n'
        globalCode += self.generateTag('IncludeCode', indent = 0, insertCode = cfile.getIncludeCode()) + '\n\n'
        globalCode += self.generateTag('GlobalCode', indent = 0, insertCode = cfile.getGlobalCode()) + '\n\n'
        if (project == None):
            globalCode += '// Modbus-interface struct.\n'
            globalCode += 'struct EsPeEs_modbus_interface_t_struct {\n'
            globalCode += '    char *Name;\n'
            globalCode += '    char *SerialPort;\n'
            globalCode += '    char *IPAdress;\n'
            globalCode += '    int Port;\n'
            globalCode += '    int Connected;\n'
            globalCode += self.generateTag('ModbusInterfaceStructCode', indent = 1, insertCode = self.getModbusInterfaceStructCode()) + '\n'
            globalCode += '};\n'
            globalCode += '\n'
            globalCode += '// Spi-interface struct.\n'
            globalCode += 'struct EsPeEs_spi_interface_t_struct {\n'
            globalCode += '    char *Name;\n'
            globalCode += self.generateTag('SPIInterfaceStructCode', indent = 1, insertCode = self.getSPIInterfaceStructCode()) + '\n'
            globalCode += '};\n'
            globalCode += '\n'
            globalCode += '// I2C-interface struct.\n'
            globalCode += 'struct EsPeEs_i2c_interface_t_struct {\n'
            globalCode += '    char *Name;\n'
            globalCode += self.generateTag('I2CInterfaceStructCode', indent = 1, insertCode = self.getI2CInterfaceStructCode()) + '\n'
            globalCode += '};\n\n'
        globalCode += '// Creates a modbus-rtu interface.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   minterface : Name or path of the serial port.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   The modbus-rtu interface.\n'
        globalCode += 'EsPeEs_modbus_interface_t* EsPeEs_modbus_interface_rtu(char *minterface)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('ModbusInterfaceRTUCode', indent = 1, insertCode = self.getModbusInterfaceRTUCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Creates a modbus-tcp interface.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   ipadress : IP-Adress of the target device.\n'
        globalCode += '//   port     : Port of the target device.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   The modbus-tcp interface.\n'
        globalCode += 'EsPeEs_modbus_interface_t* EsPeEs_modbus_interface_tcp(char *ipadress, int port)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('ModbusInterfaceTCPCode', indent = 1, insertCode = self.getModbusInterfaceTCPCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Creates a modbus-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   name       : Name of the modbus-device.\n'
        globalCode += '//   minterface : Modbus interface.\n'
        globalCode += '//   adress     : Adress of the modbus-device (affects only modbus-rtu).\n'
        globalCode += '//   regsize    : Register size of the modbus-device.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   Modbus-device.\n'
        globalCode += 'EsPeEs_modbus_device_t* EsPeEs_modbus_device(char *name, EsPeEs_modbus_interface_t *minterface, uint8_t adress, uint8_t regsize)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('ModbusDeviceCode', indent = 1, insertCode = self.getModbusDeviceCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Destroys a modbus-interface.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   minterface : Modbus-interface.\n'
        globalCode += 'void EsPeEs_modbus_interface_free(EsPeEs_modbus_interface_t *minterface)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('ModbusInterfaceFreeCode', indent = 1, insertCode = self.getModbusInterfaceFreeCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Destroys a modbus-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   device : Modbus-device.\n'
        globalCode += 'void EsPeEs_modbus_device_free(EsPeEs_modbus_device_t *device)\n'
        globalCode += '{\n'
        globalCode += '    if(device != NULL)\n'
        globalCode += '    {\n'
        globalCode += '        free(device);\n'
        globalCode += '    }\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Reads all register of the overgiven modbus-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   device : Modbus-device.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   Count of the read registers.\n'
        globalCode += 'int EsPeEs_modbus_read_registers(EsPeEs_modbus_device_t *device)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('ModbusReadRegisterCode', indent = 1, insertCode = self.getModbusReadRegisterCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Writes all register to the overgiven modbus-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   device : Modbus-device.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   Count of the written registers.\n'
        globalCode += 'int EsPeEs_modbus_write_registers(EsPeEs_modbus_device_t *device)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('ModbusWriteRegisterCode', indent = 1, insertCode = self.getModbusWriteRegisterCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Creates a spi-interface.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   name : Name or path of the spi-interface.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   The spi-interface.\n'
        globalCode += 'EsPeEs_spi_interface_t* EsPeEs_spi_interface(char *name)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('SPIInterfaceCode', indent = 1, insertCode = self.getSPIInterfaceCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Creates a spi-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   name       : Name of the spi-device.\n'
        globalCode += '//   minterface : The spi-interface.\n'
        globalCode += '//   adress     : Adress of the spi-device.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   Spi-device.\n'
        globalCode += 'EsPeEs_spi_device_t* EsPeEs_spi_device(char *name, EsPeEs_spi_interface_t *minterface, uint8_t adress)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('SPIDeviceCode', indent = 1, insertCode = self.getSPIDeviceCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Destroys a spi-interface.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   minterface : Spi-interface.\n'
        globalCode += 'void EsPeEs_spi_interface_free(EsPeEs_spi_interface_t *minterface)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('SPIInterfaceFreeCode', indent = 1, insertCode = self.getSPIInterfaceFreeCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Destroys a spi-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   device : Spi-device.\n'
        globalCode += 'void EsPeEs_spi_device_free(EsPeEs_spi_device_t *device)\n'
        globalCode += '{\n'
        globalCode += '    if(device != NULL)\n'
        globalCode += '    {\n'
        globalCode += '        free(device);\n'
        globalCode += '    }\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Transmit bytes to a spi-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   device : Spi-device.\n'
        globalCode += '//   data   : Bytes to transmit.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   Size of transmitted bytes.\n'
        globalCode += 'int EsPeEs_spi_transmit(EsPeEs_spi_device_t *device, char *data)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('SPITransmitCode', indent = 1, insertCode = self.getSPITransmitCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Creates a I2C-interface.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   name : Name or path of the I2C-interface.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   The I2C-interface.\n'
        globalCode += 'EsPeEs_i2c_interface_t* EsPeEs_i2c_interface(char *name)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('I2CInterfaceCode', indent = 1, insertCode = self.getI2CInterfaceCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Creates a I2C-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   name       : Name of the I2C-device.\n'
        globalCode += '//   minterface : The I2C-interface.\n'
        globalCode += '//   adress     : Adress of the I2C-device.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   I2C-device.\n'
        globalCode += 'EsPeEs_i2c_device_t* EsPeEs_i2c_device(char *name, EsPeEs_i2c_interface_t *minterface, uint8_t adress)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('I2CDeviceCode', indent = 1, insertCode = self.getI2CDeviceCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Destroys a I2C-interface.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   minterface : I2C-interface.\n'
        globalCode += 'void EsPeEs_i2c_interface_free(EsPeEs_i2c_interface_t *minterface)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('I2CInterfaceFreeCode', indent = 1, insertCode = self.getI2CInterfaceFreeCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Destroys a I2C-device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   device : I2C-device.\n'
        globalCode += 'void EsPeEs_i2c_device_free(EsPeEs_i2c_device_t *device)\n'
        globalCode += '{\n'
        globalCode += '    if(device != NULL)\n'
        globalCode += '    {\n'
        globalCode += '        free(device);\n'
        globalCode += '    }\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Reads a byte from a device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   device : I2C-device.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   Read byte from I2C-device.\n'
        globalCode += 'int EsPeEs_i2c_read(EsPeEs_i2c_device_t *device)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('I2CReadCode', indent = 1, insertCode = self.getI2CReadCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Writes a byte to a device.\n'
        globalCode += '// Parameters:\n'
        globalCode += '//   device : I2C-device.\n'
        globalCode += '//   data   : Byte.\n'
        globalCode += '// Returns:\n'
        globalCode += '//   Written byte from I2C-device.\n'
        globalCode += 'int EsPeEs_i2c_write(EsPeEs_i2c_device_t *device, int data)\n'
        globalCode += '{\n'
        globalCode += self.generateTag('I2CWriteCode', indent = 1, insertCode = self.getI2CWriteCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Sets the timer to zero.\n'
        globalCode += 'void EsPeEs_start_cycle()\n'
        globalCode += '{\n'
        globalCode += self.generateTag('StartCycleCode', indent = 1, insertCode = self.getStartCycleCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Stops the time.\n'
        globalCode += 'void EsPeEs_stop_cycle()\n'
        globalCode += '{\n'
        globalCode += self.generateTag('StopCycleCode', indent = 1, insertCode = self.getStopCycleCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Returns the average cycle time.\n'
        globalCode += 'uint16_t EsPeEs_average_cycle_time()\n'
        globalCode += '{\n'
        globalCode += self.generateTag('AverageCycleTimeCode', indent = 1, insertCode = self.getAverageCycleTimeCode()) + '\n'
        globalCode += '}\n'
        globalCode += '\n'
        globalCode += '// Returns the last cycle time.\n'
        globalCode += 'uint16_t EsPeEs_last_cycle_time()\n'
        globalCode += '{\n'
        globalCode += self.generateTag('LastCycleTimeCode', indent = 1, insertCode = self.getLastCycleTimeCode()) + '\n'
        globalCode += '}\n'

        ccode = CCode()
        ccode.setCode(includeCode, globalCode, '', '', '', '')
        return ccode
        
    def __betweenTags__(self, code, cursor = -1):
        between = False
        if self.__betweenTag__(code, 'IncludeCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'GlobalCode', indent = 0, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'ModbusInterfaceRTUCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'ModbusInterfaceTCPCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'ModbusDeviceCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'ModbusInterfaceFreeCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'ModbusReadRegisterCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'ModbusWriteRegisterCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'SPIInterfaceCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'SPIDeviceCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'SPIInterfaceFreeCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'SPITransmitCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'I2CInterfaceCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'I2CDeviceCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'I2CInterfaceFreeCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'I2CReadCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'I2CWriteCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'StartCycleCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'StopCycleCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'AverageCycleTimeCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'LastCycleTimeCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'ModbusInterfaceStructCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'SPIInterfaceStructCode', indent = 1, cursor = cursor) == True:
            between = True
        if self.__betweenTag__(code, 'I2CInterfaceStructCode', indent = 1, cursor = cursor) == True:
            between = True
        return between
        
    def __hasTags__(self, code):
        has = True
        if self.hasTag(code, 'IncludeCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'GlobalCode', indent = 0) == False:
            has = False
        if self.hasTag(code, 'ModbusInterfaceRTUCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'ModbusInterfaceTCPCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'ModbusDeviceCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'ModbusInterfaceFreeCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'ModbusReadRegisterCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'ModbusWriteRegisterCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'SPIInterfaceCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'SPIDeviceCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'SPIInterfaceFreeCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'SPITransmitCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'I2CInterfaceCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'I2CDeviceCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'I2CInterfaceFreeCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'I2CReadCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'I2CWriteCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'StartCycleCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'StopCycleCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'AverageCycleTimeCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'LastCycleTimeCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'ModbusInterfaceStructCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'SPIInterfaceStructCode', indent = 1) == False:
            has = False
        if self.hasTag(code, 'I2CInterfaceStructCode', indent = 1) == False:
            has = False
        return has
        
    def getType(self):
        return self.__Type
      
class Project(Object):
    def __init__(self, name):
        Object.__init__(self)
        self.__Name = name
        self.__CompanyName = ''
        self.__ProductName = ''
        self.__ProductVersion = ''
        self.__Composition = None
        self.__ModbusDevices = range(0, 0)
        self.__SPIDevices = range(0, 0)
        self.__I2CDevices = range(0, 0)
        self.__Target = 'Unknown'
        self.__TargetTCPAdress = 'localhost'
        self.__TargetTCPPort = 3000
        self.__CFlags = ''
        self.__LDFlags = ''
        self.__Shield = None
        self.__TargetDevice = None
              
    def getName(self):
        return self.__Name
    
    def setName(self, name):
        self.__Name = name
        
    def getCompanyName(self):
        return self.__CompanyName
    
    def getProductName(self):
        return self.__ProductName
        
    def getProductVersion(self):
        return self.__ProductVersion

    def getTarget(self):
        return self.__Target
        
    def getTargetDevice(self):
        return self.__TargetDevice
    
    def getTargetTCPAdress(self):
        return self.__TargetTCPAdress
    
    def getTargetTCPPort(self):
        return self.__TargetTCPPort

    def getCFlags(self):
        return self.__CFlags
    
    def getLDFlags(self):
        return self.__LDFlags

    def setCompanyName(self, companyName):
        self.__CompanyName = companyName
    
    def setProductName(self, productName):
        self.__ProductName = productName
    
    def setProductVersion(self, productVersion):
        self.__ProductVersion = productVersion
        
    def setTarget(self, target):
        self.__Target = target
        
    def setTargetDevice(self, targetDevice):
        self.__TargetDevice = targetDevice
        
    def setTargetTCPAdress(self, adress):
        self.__TargetTCPAdress = adress
        
    def setTargetTCPPort(self, port):
        self.__TargetTCPPort = port
  
    def setCFlags(self, cflags):
        self.__CFlags = cflags
        
    def setLDFlags(self, ldflags):
        self.__LDFlags = ldflags        
      
    def getShield(self):
        return self.__Shield
        
    def setShield(self, shield):
        self.__Shield = shield
        
    def existDevice(self, name):
        exist = self.existModbusDevice(name) or self.existSPIDevice(name) or self.existI2CDevice(name)
        if not (self.getShield() == None):
            exist = exist or (self.getShield().getName() == name)
        exist = exist or (name == 'EsPeEs')
        return exist
    
    
    def addModbusDevice(self, name = None, instance = None):
        if not (name == None) and (instance == None):
            if not self.existDevice(name) and not (name == ''):
                md = ModbusDevice(name = name)
                self.__ModbusDevices.append(md)
                return md
        if (name == None) and not (instance == None):
            if not self.existDevice(instance.getName()) and not (instance.getName() == ''):
                self.__ModbusDevices.append(instance)
                return instance
        self.__sortModbusDevices__()
        return None
    
    def __sortModbusDevices__(self):
        deviceNames = range(0, 0)
        devices = self.__ModbusDevices
        for i in range(len(self.__ModbusDevices)):
            deviceNames.append(self.__ModbusDevices[i].getName())
        self.__ModbusDevices = range(0, 0)
        deviceNames.sort()
        for i in range(len(deviceNames)):
            for g in range(len(devices)):
                if devices[g].getName() == deviceNames[i]:
                    self.__ModbusDevices.append(devices[g])

    def existModbusDevice(self, name):
        if not (name == None):
            for md in self.__ModbusDevices:
                if md.getName() == name:
                    return True
            return False
        else:
            return False

    def getModbusDevice(self, name = None, index = None):
        if not (name == None) and (index == None):
            for md in self.__ModbusDevices:
                if md.getName() == name:
                    return md
        if not (index == None) and (name == None):
            if (len(self.__ModbusDevices) > 0) and (index < len(self.__ModbusDevices)):
                return self.__ModbusDevices[index]
        return None
    
    def getModbusDevices(self):
        return self.__ModbusDevices
    
    def clearModbusDevices(self):
        self.__ModbusDevices = range(0, 0)
        
    def modbusAdressAlreadyAssigned(self, interface, adress):
        for i in range(len(self.__ModbusDevices)):
            modbusInterface = self.__ModbusDevices[i].getModbusInterface().getSerialPort()
            modbusAdress = self.__ModbusDevices[i].getAdress()
            if (modbusInterface == interface) and (modbusAdress == adress):
                return True
        return False
        
    def modbusTCPAdressAlreadyAssigned(self, ipadress, port):
        if not (port == None):
            port = Preferences.Modbus.DefaultPort
        if not (ipadress == None):
            for i in range(len(self.__ModbusDevices)):
                __ipadress = self.__ModbusDevices[i].getModbusInterface().getTCPAdress()
                __port = self.__ModbusDevices[i].getModbusInterface().getTCPPort()
                if (ipadress == __ipadress) and (port == __port):
                    return True
        return False
    
    def removeModbusDevice(self, name = None, index = None):
        if not (name == None) and (index == None):
            for i in range(len(self.__ModbusDevices)):
                if self.__ModbusDevices[i].getName() == name:
                    del self.__ModbusDevices[i] 
                    return 
        if not (index == None) and (name == None):
            if (len(self.__ModbusDevices) > 0) and (index < len(self.__ModbusDevices)):
                del self.__ModbusDevices[index]
    
    def addSPIDevice(self, name = None, instance = None):
        if not (name == None) and (instance == None):
            if not self.existDevice(name) and not (name == ''):
                md = SPIDevice(name = name)
                self.__SPIDevices.append(md)
                return md
        if (name == None) and not (instance == None):
            if not self.existDevice(instance.getName()) and not (instance.getName() == ''):
                self.__SPIDevices.append(instance)
                return instance
        self.__sortSPIDevices__()
        return None
    
    def __sortSPIDevices__(self):
        deviceNames = range(0, 0)
        devices = self.__SPIDevices
        for i in range(len(self.__SPIDevices)):
            deviceNames.append(self.__SPIDevices[i].getName())
        self.__SPIDevices = range(0, 0)
        deviceNames.sort()
        for i in range(len(deviceNames)):
            for g in range(len(devices)):
                if devices[g].getName() == deviceNames[i]:
                    self.__SPIDevices.append(devices[g])

    def existSPIDevice(self, name):
        if not (name == None):
            for md in self.__SPIDevices:
                if md.getName() == name:
                    return True
            return False
        else:
            return False

    def getSPIDevice(self, name = None, index = None):
        if not (name == None) and (index == None):
            for md in self.__SPIDevices:
                if md.getName() == name:
                    return md
        if not (index == None) and (name == None):
            if (len(self.__SPIDevices) > 0) and (index < len(self._SPIDevices)):
                return self.__SPIDevices[index]
        return None
    
    def getSPIDevices(self):
        return self.__SPIDevices
    
    def clearSPIDevices(self):
        self.__SPIDevices = range(0, 0)
        
    def spiAdressAlreadyAssigned(self, adress):
        for i in range(len(self.__SPIDevices)):
            spiAdress = self.__SPIDevices[i].getAdress()
            if spiAdress == adress:
                return True
        return False

    def removeSPIDevice(self, name = None, index = None):
        if not (name == None) and (index == None):
            for i in range(len(self.__SPIDevices)):
                if self.__SPIDevices[i].getName() == name:
                    del self.__SPIDevices[i] 
                    return 
        if not (index == None) and (name == None):
            if (len(self.__SPIDevices) > 0) and (index < len(self.__SPIDevices)):
                del self.__SPIDevices[index]    
                
    def addI2CDevice(self, name = None, instance = None):
        if not (name == None) and (instance == None):
            if not self.existDevice(name) and not (name == ''):
                md = I2CDevice(name = name)
                self.__I2CDevices.append(md)
                return md
        if (name == None) and not (instance == None):
            if not self.existDevice(instance.getName()) and not (instance.getName() == ''):
                self.__I2CDevices.append(instance)
                return instance
        self.__sortI2CDevices__()
        return None
    
    def __sortI2CDevices__(self):
        deviceNames = range(0, 0)
        devices = self.__I2CDevices
        for i in range(len(self.__I2CDevices)):
            deviceNames.append(self.__I2CDevices[i].getName())
        self.__I2CDevices = range(0, 0)
        deviceNames.sort()
        for i in range(len(deviceNames)):
            for g in range(len(devices)):
                if devices[g].getName() == deviceNames[i]:
                    self.__I2CDevices.append(devices[g])

    def existI2CDevice(self, name):
        if not (name == None):
            for md in self.__I2CDevices:
                if md.getName() == name:
                    return True
            return False
        else:
            return False

    def getI2CDevice(self, name = None, index = None):
        if not (name == None) and (index == None):
            for md in self.__I2CDevices:
                if md.getName() == name:
                    return md
        if not (index == None) and (name == None):
            if (len(self.__I2CDevices) > 0) and (index < len(self._I2CDevices)):
                return self.__I2CDevices[index]
        return None
    
    def getI2CDevices(self):
        return self.__I2CDevices
    
    def clearI2CDevices(self):
        self.__I2CDevices = range(0, 0)
        
    def i2cAdressAlreadyAssigned(self, adress):
        for i in range(len(self.__I2CDevices)):
            i2cAdress = self.__I2CDevices[i].getAdress()
            if i2cAdress == adress:
                return True
        return False

    def removeI2CDevice(self, name = None, index = None):
        if not (name == None) and (index == None):
            for i in range(len(self.__I2CDevices)):
                if self.__I2CDevices[i].getName() == name:
                    del self.__I2CDevices[i] 
                    return 
        if not (index == None) and (name == None):
            if (len(self.__I2CDevices) > 0) and (index < len(self.__I2CDevices)):
                del self.__I2CDevices[index]    
                
    def getModbusInterfaces(self):
        modbusInterfaces = range(0, 0)
        for i in range(len(self.__ModbusDevices)):
            mi = self.__ModbusDevices[i].getModbusInterface()
            exists = False
            for h in range(len(modbusInterfaces)):
                if modbusInterfaces[h].getName == mi.getName():
                    exists = True
                    break
            if exists == False:
                modbusInterfaces.append(mi)
        return modbusInterfaces
    
    def getModbusInterfaceNumber(self, name):
        modbusInterfaces = self.getModbusInterfaces()
        for i in range(len(modbusInterfaces)):
            if modbusInterfaces[i].getName() == name:
                return i
        return 65535
    
    def getCExtensionNumber(self, name):
        if not (name == None):
            count = 1
            if name == 'Composition':
                return 0
            if not (self.getShield() == None):
                count = count + 1
                if self.getShield().getName() == name:
                    return 1
            for i in range(len(self.__ModbusDevices)):
                if self.__ModbusDevices[i].getName() == name:
                    return  i + count
            count = count + len(self.__ModbusDevices)
            for i in range(len(self.__SPIDevices)):
                if self.__SPIDevices[i].getName() == name:
                    return  i + count
            count = count + len(self.__SPIDevices)
            for i in range(len(self.__I2CDevices)):
                if self.__I2CDevices[i].getName() == name:
                    return  i + count
        return 65535
        
    def getRealCExtensionNumber(self, cextName, cfileName):
        if not (cextName == None) and not (cfileName == None):
            count = 0
            
            # Shield
            cfiles = self.getShield().getCFiles()
            for h in range(len(cfiles)):
                if (self.getShield().getName() == cextName) and (cfiles[h].getName() == cfileName):
                    return count
                count = count + 1
                
            # Modbus
            for i in range(len(self.__ModbusDevices)):
                cfiles = self.__ModbusDevices[i].getCFiles()
                for h in range(len(cfiles)):
                    if (self.__ModbusDevices[i].getName() == cextName) and (cfiles[h].getName() == cfileName):
                        return count
                    count = count + 1
                    
            # SPI
            for i in range(len(self.__SPIDevices)):
                cfiles = self.__SPIDevices[i].getCFiles()
                for h in range(len(cfiles)):
                    if (self.__SPIDevices[i].getName() == cextName) and (cfiles[h].getName() == cfileName):
                        return count
                    count = count + 1
                    
            # I2C
            for i in range(len(self.__I2CDevices)):
                cfiles = self.__I2CDevices[i].getCFiles()
                for h in range(len(cfiles)):
                    if (self.__I2CDevices[i].getName() == cextName) and (cfiles[h].getName() == cfileName):
                        return count
                    count = count + 1
                    
            # TargetDevice
            cfiles = self.__TargetDevice.getCFiles()
            for h in range(len(cfiles)):
                if (self.__TargetDevice.getName() == cextName) and (cfiles[h].getName() == cfileName):
                    return count
                count = count + 1
            
            # Composition
            cfiles = self.__Composition.getCFiles()
            for h in range(len(cfiles)):
                if (self.__Composition.getName() == cextName) and (cfiles[h].getName() == cfileName):
                    return count
                count = count + 1
                
        return 65535
    
    def save(self, directory):
        if not (self.__TargetDevice == None):
            if self.__TargetDevice.getTarget() == Targets.Windows:
                self.__CFlags = '-lws2_32'
                self.__LDFlags = '-lws2_32'
        Utilities.makeDirectory(directory)
        Utilities.writeToFile(self.__generatePlcXML__(), 
                              directory + os.sep + 'plc.xml')
        Utilities.writeToFile(self.__generateBeremizXML__(), 
                              directory + os.sep + 'beremiz.xml')
        self.__Composition = Composition(name = 'Composition', project = self)
        self.__Composition.save(directory, self)
        if not (self.__TargetDevice == None):
            self.__TargetDevice.setName('EsPeEs')
            self.__TargetDevice.save(directory, self)
        self.__Shield.save(directory, self)
        for i in range(len(self.__ModbusDevices)):
            self.__ModbusDevices[i].save(directory, self)
        for i in range(len(self.__SPIDevices)):
            self.__SPIDevices[i].save(directory, self)
        for i in range(len(self.__I2CDevices)):
            self.__I2CDevices[i].save(directory, self)
        Utilities.writeToFile(Utilities.objectToJson(self), 
                              directory + os.sep + 'project.xml')
            
    def __generatePlcXML__(self):
        currentTime = datetime.datetime.today().isoformat().replace(' ', 'T').split('.')[0]
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<project xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        xml += '         xmlns="http://www.plcopen.org/xml/tc6.xsd"\n'
        xml += '         xmlns:xhtml="http://www.w3.org/1999/xhtml"\n'
        xml += '         xsi:schemaLocation="http://www.plcopen.org/xml/tc6.xsd">\n'
        xml += '  <fileHeader companyName=' + '"' + self.getCompanyName() + '"' + '\n'
        xml += '              productName=' + '"' + self.getProductName() + '"' + '\n'
        xml += '              productVersion=' + '"' + self.getProductVersion() + '"' + '\n'
        xml += '              creationDateTime="' + currentTime + '"/>\n'
        xml += '  <contentHeader name=' + '"' + self.getName() + '"' + '\n'
        xml += '                 modificationDateTime="' + currentTime + '">\n'
        xml += '        <coordinateInfo>\n'
        xml += '      <fbd>\n'
        xml += '        <scaling x="0" y="0"/>\n'
        xml += '      </fbd>\n'
        xml += '      <ld>\n'
        xml += '        <scaling x="0" y="0"/>\n'
        xml += '      </ld>\n'
        xml += '      <sfc>\n'
        xml += '        <scaling x="0" y="0"/>\n'
        xml += '      </sfc>\n'
        xml += '    </coordinateInfo>\n'
        xml += '  </contentHeader>\n'
        xml += '  <types>\n'
        xml += '    <dataTypes/>\n'
        xml += '    <pous>\n'
        xml += '      <pou name="MainProgram" pouType="program">\n'
        xml += '        <interface>\n'
        xml += '          <localVars>\n'
        xml += '            <variable name="In">\n'
        xml += '              <type>\n'
        xml += '                <BOOL/>\n'
        xml += '              </type>\n'
        xml += '            </variable>\n'
        xml += '            <variable name="Out">\n'
        xml += '              <type>\n'
        xml += '                <BOOL/>\n'
        xml += '              </type>\n'
        xml += '            </variable>\n'
        xml += '          </localVars>\n'
        xml += '        </interface>\n'
        xml += '        <body>\n'
        xml += '          <FBD>\n'
        xml += '            <inVariable localId="1" height="26" width="22">\n'
        xml += '              <position x="20" y="20"/>\n'
        xml += '              <connectionPointOut>\n'
        xml += '                <relPosition x="22" y="13"/>\n'
        xml += '              </connectionPointOut>\n'
        xml += '              <expression>In</expression>\n'
        xml += '            </inVariable>\n'
        xml += '            <outVariable localId="2" height="26" width="33">\n'
        xml += '              <position x="90" y="20"/>\n'
        xml += '              <connectionPointIn>\n'
        xml += '                <relPosition x="0" y="13"/>\n'
        xml += '                <connection refLocalId="1">\n'
        xml += '                  <position x="90" y="33"/>\n'
        xml += '                  <position x="42" y="33"/>\n'
        xml += '                </connection>\n'
        xml += '              </connectionPointIn>\n'
        xml += '              <expression>Out</expression>\n'
        xml += '            </outVariable>\n'
        xml += '          </FBD>\n'
        xml += '        </body>\n'
        xml += '      </pou>\n'
        xml += '    </pous>\n'
        xml += '  </types>\n'
        xml += '  <instances>\n'
        xml += '    <configurations>\n'
        xml += '      <configuration name="config">\n'
        xml += '        <resource name="MainResource">\n'
        xml += '          <task name="MainTask" interval="T#150ms" priority="0"/>\n'
        xml += '          <pouInstance name="MainInstance" typeName="MainProgram"/>\n'
        xml += '        </resource>\n'
        xml += '      </configuration>\n'
        xml += '    </configurations>\n'
        xml += '  </instances>\n'
        xml += '</project>'
        return xml
    
    def __generateBeremizXML__(self):
        xml =  '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<BeremizRoot URI_location="PYRO://' + self.getTargetTCPAdress() + ':' + str(self.getTargetTCPPort()) + '">\n'
        xml += '  <TargetType>\n'
        xml += '    <' + self.getTarget() + ' CFLAGS="' + self.getCFlags() + '" LDFLAGS="' + self.getLDFlags() + '"/>\n'
        xml += '  </TargetType>\n'
        xml += '</BeremizRoot>'
        return xml   
    
class ProjectData(Object):
    def __init__(self, name = None):
        Object.__init__(self)
        self.__Name = name
        self.__RootDirectory = None
        
    def getName(self):
        return self.__Name    
    
    def setName(self, name):
        self.__Name = name 
        
    def load(self, path):
        if not (self.__Name == None):
            if os.path.exists(path + os.sep + self.__Name):
                self.__RootDirectory = self.__load__(path + os.sep + self.__Name)
    
    def __load__(self, path):
        name = path.split(os.sep)[-1:][0]
        directory = Directory(name = name)
        entries = Utilities.listDirectory(path)
        for i in range(len(entries)):
            type = Utilities.isFileOrDirectory(os.path.join(path, entries[i]))
            if type == 'File':
                file = File(name = entries[i], buffer = base64.b64encode(Utilities.readFromFile(os.path.join(path, entries[i]))))
                directory.addEntry(instance = file)
            if type == 'Directory':
                directory.addEntry(instance = self.__load__(os.path.join(path, entries[i])))
        return directory 
        
    def save(self, path):
        if not (self.__Name == None) and not (self.__RootDirectory == None):
            if os.path.exists(path):
                self.__save__(path, self.__RootDirectory)
            
    def __save__(self, path, directory):
        dirpath = os.path.join(path, directory.getName())
        Utilities.makeDirectory(dirpath)
        entries = directory.getEntries()
        for i in range(len(entries)):
            type = entries[i].getType()
            if type == 'File':
                Utilities.writeToFile(base64.b64decode(entries[i].getBuffer()), os.path.join(dirpath, entries[i].getName()))
            if type == 'Directory':
                self.__save__(dirpath, entries[i])
    
    def remove(self, path):
        self.load(path)
        if not (self.__Name == None) and not (self.__RootDirectory == None):
            if os.path.exists(path):
                self.__remove__(path, self.__RootDirectory)
        
    def __remove__(self, path, directory):
        dirpath = os.path.join(path, directory.getName())
        entries = directory.getEntries()
        for i in range(len(entries)):
            type = entries[i].getType()
            if type == 'File':
                Utilities.removeFile(os.path.join(dirpath, entries[i].getName()))
            if type == 'Directory':
                self.__remove__(dirpath, entries[i])
        Utilities.removeDirectory(dirpath)

class Modbus(object):
    class Modes(object):
        Error = 'Error'
        RTU = 'RTU'
        TCP = 'TCP'

    class Interface(Object):
        def __init__(self, serialport = None, ipadress = None, port = 60502):
            Object.__init__(self)
            self.__SerialPort = serialport
            self.__TCPAdress = ipadress
            self.__TCPPort = port
            if not (serialport == None) and (ipadress == None):
                self.__Mode = Modbus.Modes.RTU
            if (serialport == None) and not (ipadress == None):
                self.__Mode = Modbus.Modes.TCP
            if (not (serialport == None) and not (ipadress == None)) or ((serialport == None) and (ipadress == None)):
                self.__Mode = Modbus.Modes.Error
                
        def getName(self):
            if self.getMode() == Modbus.Modes.RTU:
                return self.__SerialPort
            if self.getMode() == Modbus.Modes.RTU:
                return self.__TCPAdress + ':' + str(self.__TCPPort)
            return ''

        def getSerialPort(self):
            return self.__SerialPort
        
        def getTCPAdress(self):
            return self.__TCPAdress
        
        def getTCPPort(self):
            return self.__TCPPort
          
        def getMode(self):
            return self.__Mode            
    
class File(Object):
    def __init__(self, name = None, buffer = None):
        Object.__init__(self)
        if name == None:
            self.__Name = '__ErrorFile__'
        else:
            self.__Name = name
        if buffer == None:
            self.__Buffer = range(0, 0)
        else:
            self.__Buffer = buffer
            
    def getName(self):
        return self.__Name    
        
    def getBuffer(self):
        return self.__Buffer
    
    def setName(self, name):
        self.__Name = name    
    
    def setBuffer(self, buffer):
        self.__Buffer = buffer
        
    def getType(self):
        return 'File'
            
class Directory(Object):
    def __init__(self, name = None):
        Object.__init__(self)
        if name == None:
            self.__Name = '__ErrorDirectory__'
        else:
            self.__Name = name
        self.__Entries = range(0, 0)
            
    def getName(self):
        return self.__Name    
    
    def setName(self, name):
        self.__Name = name    
        
    def addEntry(self, name = None, type = None, instance = None):
        var = None
        if not (name == None) and not (type == None) and (instance == None):
            if not self.existEntry(name) and not (name == ''):
                if type == 'File':
                    var = File(name = name)
                if type == 'Directory':
                    var = Directory(name = name)
                if not (var == None):
                    self.__Entries.append(var)
                return var
        if (name == None) and not (instance == None):
            if not self.existEntry(instance.getName()) and not (instance.getName() == ''):
                self.__Entries.append(instance)
                return var
        return None

    def existEntry(self, name):
        if not (name == None):
            for var in self.__Entries:
                if var.getName() == name:
                    return True
            return False
        else:
            return False

    def getEntry(self, name = None, index = None):
        if not (name == None) and (index == None):
            for var in self.__Entries:
                if var.getName() == name:
                    return var
        if not (index == None) and (name == None):
            if (len(self.__Entries) > 0) and (index < len(self.__Entries)):
                return self.__Entries[index]
        return None
    
    def getEntries(self):
        return self.__Entries

    def setEntries(self, entries):
        self.__Entries = entries
    
    def removeEntry(self, name = None, index = None):
        if not (name == None) and (index == None):
            for i in range(len(self.__Entries)):
                if self.__Entries[i].getName() == name:
                    del self.__Entries[i] 
                    return 
        if not (index == None) and (name == None):
            if (len(self.__Entries) > 0) and (index < len(self.__Entries)):
                del self.__Entries[index]        
        
    def getType(self):
        return 'Directory'

class ServerInformation(Object):
    def __init__(self):
        Object.__init__(self)
        vmem = psutil.virtual_memory()
        swap = psutil.swap_memory() 
        self.__isLinux = sys.platform.startswith('linux')
        self.__isWindows = sys.platform == 'win32'
        self.__isMacOSX = sys.platform == 'darwin'
        self.__isRaspberryPi = Utilities.isRaspberryPi()
        self.__is64Bit = sys.maxsize > 2**32            
        self.__Processor = platform.machine()
        self.__SerialPorts = Utilities.listSerialPorts()
        self.__RunableProjects = range(0, 0)
        self.__CPUCores = psutil.NUM_CPUS
        self.__MemoryTotal = vmem.total
        self.__MemoryUsed = vmem.total - vmem.available
        self.__SwapTotal = swap.total
        self.__SwapUsed = swap.total - swap.free
        espees_server_dir = os.path.join(getSaveFolder(), 'Server')
        if not os.path.exists(espees_server_dir):
            Utilities.makeDirectory(espees_server_dir)
            self.__AvailableProjects = range(0, 0)
        else:
            self.__AvailableProjects = Utilities.listDirectory(espees_server_dir)
            for i in range(len(self.__AvailableProjects)):
                if os.path.exists( espees_server_dir + os.sep + self.__AvailableProjects[i] + os.sep + 'build' + os.sep + self.__AvailableProjects[i] + '.so') or os.path.exists( espees_server_dir + os.sep + self.__AvailableProjects[i] + os.sep + 'build' + os.sep + self.__AvailableProjects[i] + '.dll'):
                    self.__RunableProjects.append(self.__AvailableProjects[i])
        self.__AvailableProjects.sort()
        self.__RunableProjects.sort()
                   
    def isLinux(self):
        return self.__isLinux
        
    def isWindows(self):
        return self.__isWindows
        
    def isMacOSX(self):
        return self.__isMacOSX
        
    def isRaspberryPi(self):
        return self.__isRaspberryPi
        
    def is32Bit(self):
        if self.__is64Bit == True:
            return False
        else:
            return True
        
    def is64Bit(self):
        return self.__is64Bit
        
    def getOperatingSystem(self):
        if self.isLinux() == True:
            return 'Linux'
        if self.isWindows() == True:
            return 'Windows'
        if self.isMacOSX() == True:
            return 'MacOSX'
        if self.isRaspberryPi() == True:
            return 'RaspberryPi'
        return 'Unknown'
        
    def getTarget(self):
        if self.isRaspberryPi() == True:
            return Targets.RaspberryPi
        if self.isLinux() == True:
            if self.is32Bit == True:
                return Targets.Linux32Bit
            else:
                return Targets.Linux64Bit
        if self.isWindows() == True:
            return Targets.Windows
        return 'Unknown'
        
    def getProcessor(self):
        return self.__Processor
        
    def getCPUCores(self):
        return self.__CPUCores
        
    def getMemoryTotal(self):
        return self.__MemoryTotal
    
    def getMemoryUsed(self):
        return self.__MemoryUsed
        
    def getSwapTotal(self):
        return self.__SwapTotal
    
    def getSwapUsed(self):
        return self.__SwapUsed
    
    def getSerialPorts(self):
        return self.__SerialPorts
    
    def getAvailableProjects(self):
        return self.__AvailableProjects
    
    def existProject(self, name):
        for i in range(len(self.__AvailableProjects)):
            if self.__AvailableProjects[i] == name:
                return True
        return False
    
    def addProject(self, name):
        if self.existProject(name) == False:
            self.__AvailableProjects.append(name)
            self.__AvailableProjects.sort()
            
    def removeProject(self, name):
        for i in range(len(self.__AvailableProjects)):
            if self.__AvailableProjects[i] == name:
                del self.__AvailableProjects[i]
                return True
        return False 
    
    def getRunableProjects(self):
        return self.__RunableProjects
    
    def getInfoText(self):
        info = ''
        info += '<!DOCTYPE html>'
        info += '<html>'
        info += '  <head>'
        info += '    <meta content="text/html; charset=windows-1252" http-equiv="content-type">'
        info += '    <title></title>'
        info += '  </head>'
        info += '  <body>'
        info += '    <table style="width: 100%;" border="0">'
        info += '      <tbody>'
        info += '        <tr>'
        info += '          <td>Computer:</td>'
        info += '          <td>'
        if self.isRaspberryPi() == True:
            info += 'Raspberry Pi'
        else:
            info += 'PC'
        info += '</td>'
        info += '        </tr>'
        info += '        <tr>'
        info += '          <td>OS:</td>'
        info += '          <td>'
        if self.isLinux() == True:
            info += 'Linux'
        if self.isWindows() == True:
            info += 'Windows'
        if self.isMacOSX() == True:
            info += 'Mac OSX'
        if self.is64Bit() == True:
            info += ' / 64-Bit'
        else:
            info += ' / 32-Bit'
        info += '</td>'
        info += '        </tr>'
        info += '        <tr>'
        info += '          <td>CPU:</td>'
        info += '          <td>'
        info += self.getProcessor()
        info += '</td>'
        info += '        </tr>'
        info += '        <tr>'
        info += '          <td>CPU-Cores:</td>'
        info += '          <td>'
        info += str(self.getCPUCores())
        info += '</td>'
        info += '        </tr>'
        info += '        <tr>'
        info += '          <td>Memory:</td>'
        info += '          <td>'
        info += str(self.getMemoryUsed() / (1024 * 1024)) + 'MB / ' + str(self.getMemoryTotal() / (1024 * 1024)) + 'MB'
        info += '</td>'
        info += '        </tr>'
        info += '        <tr>'
        info += '          <td>Swap:</td>'
        info += '          <td>'
        info += str(self.getSwapUsed() / (1024 * 1024)) + 'MB / ' + str(self.getSwapTotal() / (1024 * 1024)) + 'MB'
        info += '</td>'
        info += '        </tr>'
        info += '      </tbody>'
        info += '    </table>'
        info += '    <br>'
        info += '  </body>'
        info += '</html>'
        return info

class Server(object):  
    def __init__(self):
        self.__PLCProcess = None
        self.__PLCIsRunningBeremiz = False
        self.__PLCProject = ''

    def getServerInformation(self):
        serverInformation = ServerInformation()
        data = Utilities.packData(serverInformation)
        return data
    
    def downloadProject(self, name):
        projectData = ProjectData(name = name)
        espees_server_dir = os.path.join(getSaveFolder(), 'Server')
        if(os.path.exists(os.path.join(espees_server_dir, name))):
            projectData.load(espees_server_dir)
        data = Utilities.packData(projectData)
        return data
        
    def uploadProject(self, projectData):
        projectData = Utilities.unpackData(projectData)
        espees_server_dir = os.path.join(getSaveFolder(), 'Server')
        if(os.path.exists(os.path.join(espees_server_dir, projectData.getName()))):
            self.removeProject(projectData.getName())
        projectData.save(espees_server_dir)
        return True
        
    def removeProject(self, name):
        projectData = ProjectData(name = name)
        espees_server_dir = os.path.join(getSaveFolder(), 'Server')
        if(os.path.exists(os.path.join(espees_server_dir, name))):
            projectData.remove(espees_server_dir)
        return True
        
    def startPLC_Project(self, project):
        if ProcessManagement.Instance().plcIsRunning() == False:
            self.__PLCProject = project
            return ProcessManagement.Instance().startPLC_Project(project)
        else:
            return False
        
    def startPLC_Beremiz(self):
        if ProcessManagement.Instance().plcIsRunning() == False:
            self.__PLCIsRunningBeremiz = True
            return ProcessManagement.Instance().startPLC_Beremiz()
        else:
            return False
        
    def stopPLC(self):
        if ProcessManagement.Instance().plcIsRunning() == True:
            self.__PLCIsRunningBeremiz = False
            self.__PLCProject = ''
            return ProcessManagement.Instance().stopPLC()
        else:
            return False
        
    def plcIsRunning(self):
        if ProcessManagement.Instance().plcIsRunning() == True:
            if self.__PLCIsRunningBeremiz == True:
                return 1
            else:
                return 2
        else:
            return 0
            
    def plcProject(self):
        return self.__PLCProject

class Client(object):
    def __init__(self, ipadress, port, event = None, useWx = False):
        self.__IPAdress = ipadress
        self.__Port = port
        self.__Connection = None
        self.__ModbusScanEvent = None
        self.__isConnected = False
        self.__Event = event
        self.__UseWx = useWx
      
    def getIPAdress(self):
        return self.__IPAdress
    
    def getPort(self):
        return self.__Port
    
    def isConnected(self):
        return self.__isConnected
    
    def connect(self):
        try:
            self.__Connection = SOAPProxy('http://' + self.__IPAdress + ':' + str(self.__Port) + '/')
            self.__isConnected = True
            return True
        except Exception, e:
            self.__isConnected = False
            return False
        
    def disconnect(self):
        if self.__isConnected == True:
            try:
                self.__Connection = None        
            except Exception, e:
                self.__isConnected = False
            self.__isConnected = False
            
    def transmissionBroked(self, event):
        if not (self.__Event == None):
            if self.__UseWx == True:
                wx.CallAfter(self.__Event, event)
            else:
                self.__Event(event)
        
    def getServerInformation(self):
        try:
            package = self.__Connection.getServerInformation()
            data = Utilities.unpackData(package)
            return data
        except Exception, e:
            self.__isConnected = False
            self.transmissionBroked('getServerInformation()')
            return None   
        
    def downloadProject(self, name):
        try:
            package = self.__Connection.downloadProject(name)
            data = Utilities.unpackData(package)
            return data
        except Exception, e:
            self.transmissionBroked('downloadProject()')
            return None
        
    def uploadProject(self, projectData):
        try:
            if self.__Connection.uploadProject(Utilities.packData(projectData)) == True:
                return True
            else:
                return False
        except Exception, e:
            self.__isConnected = False
            self.transmissionBroked('uploadProject()')
            return False
            
    def removeProject(self, name):
        try:
            success = self.__Connection.removeProject(name)
            return success
        except Exception, e:
            self.transmissionBroked('removeProject()')
            self.__isConnected = False
            return None
            
    def startPLC_Project(self, projectPath):
        try:
            success = self.__Connection.startPLC_Project(projectPath)
            return success
        except Exception, e:
            self.__isConnected = False
            self.transmissionBroked('startPLC_Project()')
            return None
            
    def startPLC_Beremiz(self):
        try:
            success = self.__Connection.startPLC_Beremiz()
            return success
        except Exception, e:
            self.__isConnected = False
            self.transmissionBroked('startPLC_Beremiz()')
            return None
            
    def stopPLC(self):
        try:
            success = self.__Connection.stopPLC()
            return success
        except Exception, e:
            self.__isConnected = False
            self.transmissionBroked('stopPLC()')
            return None
            
    def plcIsRunning(self):
        try:
            success = self.__Connection.plcIsRunning()
            return success
        except Exception, e:
            self.__isConnected = False
            self.transmissionBroked('plcIsRunning()')
            return None
            
    def plcProject(self):
        try:
            success = self.__Connection.plcProject()
            return success
        except Exception, e:
            self.__isConnected = False
            self.transmissionBroked('plcProject()')
            return None
            
class Library(Object):
    def __init__(self, name):
        Object.__init__(self)
        self.__Headers = range(0, 0)
        self.__HeaderNames = range(0, 0)
        self.__CContents = range(0, 0)
        self.__CContentNames = range(0, 0)
        
        self.__Name = name
        files = Utilities.listDirectory(getSaveFolder() + os.sep + 'Libraries' + os.sep + self.__Name)
        for i in range(len(files)):
            if (Utilities.isFileOrDirectory(getSaveFolder() + os.sep + 'Libraries' + os.sep + self.__Name +  os.sep + files[i]) == 'File') and ((files[i].endswith('.h') == True) or (files[i].endswith('.H') == True)):
                self.__Headers.append(Utilities.readFromFile(getSaveFolder() + os.sep + 'Libraries' + os.sep + self.__Name +  os.sep + files[i]))
                self.__HeaderNames.append(files[i])
            if (Utilities.isFileOrDirectory(getSaveFolder() + os.sep + 'Libraries' + os.sep + self.__Name +  os.sep + files[i]) == 'File') and ((files[i].endswith('.c') == True) or (files[i].endswith('.C') == True)):
                self.__CContents.append(Utilities.readFromFile(getSaveFolder() + os.sep + 'Libraries' + os.sep + self.__Name +  os.sep + files[i]))
                self.__CContentNames.append(files[i])
    
    def getName(self):
        return self.__Name
        
    def getHeader(self, name):
        for i in range(len(self.__HeaderNames)):
            if self.__HeaderNames[i] == name:
                return self.__Headers[i]
        return ''
        
    def getContent(self, name, targetHeader):
        for i in range(len(self.__CContentNames)):
            if self.__CContentNames[i] == name:
                return targetHeader + self.__CContents[i]
        return ''
        
    def existHeader(self, name):
        for i in range(len(self.__HeaderNames)):
            if self.__HeaderNames[i] == name:
                return True
        return False
        
    def existContent(self, name):
        for i in range(len(self.__CContentNames)):
            if self.__CContentNames[i] == name:
                return True
        return False

    def listHeaders(self):
        return self.__HeaderNames
        
    def listContents(self):
        return self.__CContentNames
        
@Singleton
class Libraries(object):
    def __init__(self):
        self.__Libraries = range(0, 0)
        self.__initialize__()
        self.__TargetDevice = None
    
    def __initialize__(self):
        if not os.path.exists(getSaveFolder() + os.sep + 'Libraries'):
            shutil.copytree(os.getcwd() + os.sep + 'Libraries', getSaveFolder() + os.sep + 'Libraries')
        files = Utilities.listDirectory(getSaveFolder() + os.sep + 'Libraries')
        for i in range(len(files)):
            if (Utilities.isFileOrDirectory(getSaveFolder() + os.sep + 'Libraries' + os.sep + files[i]) == 'Directory'):
                self.__Libraries.append(Library(files[i]))
                
    def existLibrary(self, name):
        for i in range(len(self.__Libraries)):
            if self.__Libraries[i].getName() == name:
                return True
        return False
    
    def getLibrary(self, name):
        for i in range(len(self.__Libraries)):
            if self.__Libraries[i].getName() == name:
                return self.__Libraries[i]
        return None
        
    def getLibraries(self):
        return self.__Libraries
        
    def getTargetDevice(self):
        return self.__TargetDevice
    
    def setTargetDevice(self, targetDevice):
        self.__TargetDevice = targetDevice
        
    def listLibraries(self):
        libs = range(0, 0)
        for i in range(len(self.__Libraries)):
            libs.append(self.__Libraries[i].getName())
        return libs
        
    def existHeader(self, name):
        for i in range(len(self.__Libraries)):
            if self.__Libraries[i].existHeader(name) == True:
                return True
        return False
        
    def existContent(self, name):
        for i in range(len(self.__Libraries)):
            if self.__Libraries[i].existContent(name) == True:
                return True
        return False
     
    def getHeader(self, name):
        if name == 'EsPeEs.h':
            nc = self.getTargetDevice().getHeaderCode()
            return self.replaceHeaders(nc)
        for i in range(len(self.__Libraries)):
            header = self.__Libraries[i].getHeader(name)
            if not (header == ''):
                return self.replaceHeaders(header)
        return ''
        
    def listHeaders(self):
        availableHeaders = range(0, 0)
        availableHeaders.append('EsPeEs.h')
        for i in range(len(self.__Libraries)):
            headers = self.__Libraries[i].listHeaders()
            for h in range(len(headers)):
                availableHeaders.append(headers[h])
        return availableHeaders
                
    def getContent(self, name):
        for i in range(len(self.__Libraries)):
            content = self.__Libraries[i].getContent(name, self.getTargetDevice().getTargetHeaderCode())
            if not (content == ''):
                return self.replaceHeaders(content)
        return ''
     
    def replaceHeaders(self, ccontent):
        headers = self.listHeaders()
        for i in range(len(headers)):
            if not (ccontent.find('#include "' + headers[i] + '"') == -1):
                try:
                    ccontent = ccontent.replace('#include "' + headers[i] + '"', self.getHeader(headers[i]))
                except:
                    #try:
                        ccontent = ccontent.encode('utf-8').replace('#include "' + headers[i] + '"', self.getHeader(headers[i]))
                    #except Exception, e:
                    #    print headers[i], 'Exception'
                    #    print e
                
        return ccontent
    
class Drivers(object):
    class Shields(object):
        @staticmethod
        def getDriver(driver):
            if driver == '__PC__':
                return Drivers.Shields.__PC__()
            if driver == 'None':
                return Drivers.Shields.__None__()
            if driver == 'GPIO':
                return Drivers.Shields.__GPIO__()
            return None
        
        @staticmethod
        def listNames():
            list = range(0, 0)
            list.append('None')
            list.append('GPIO')
            return list
            
        @staticmethod
        def listTree():
            l = range(0,0)
            espees_dev_dir = os.path.join(getSaveFolder(), 'Shields')
            rootPath = espees_dev_dir
            pattern = '*.drv'
            print '\nShields:\n'
            for root, dirs, files in os.walk(rootPath):
                for filename in fnmatch.filter(files, pattern):
                    entry = os.path.join(root, filename).replace(espees_dev_dir, '').replace('.drv', '').split(os.sep)
                    del entry[0]
                    l.append(entry)
            return l
            
                   
        @staticmethod
        def listDrivers():
            list = range(0, 0)
            list.append(Drivers.Shields.__None__())
            list.append(Drivers.Shields.__GPIO__())
            return list
        
        @staticmethod
        def __PC__():
            
            # Variables to define the shield
            name = 'PC'
            
            # Create shield instance.
            shield = Shield(name, True, False, False)
            shield.__setDeviceName__(name)
            return shield
        
        @staticmethod
        def __None__():
            
            # Variables to define the shield
            name = 'None'
            
            # Create shield instance.
            shield = Shield(name, True, False, False)
            shield.__setDeviceName__(name)
            
            return shield
        
        @staticmethod
        def __GPIO__():
            
            # Variables to define the shield
            name = 'GPIO'
            
            # Create shield instance.
            shield = Shield(name, True, False, False)
            shield.__setDeviceName__(name)
            
            globalCode = 'int16_t __GPIO_pinMode__;\n'
            initializeCode = 'wiringPiSetup();\n'
            pinMode_PublishCode = '__GPIO_pinMode__ = 0;'
            digitalInput_RetrieveCode = ''
            digitalOutput_PublishCode = ''
            
            # Create c-files.
            pinMode = shield.addCFile(name = 'PinMode')
            digitalInput = shield.addCFile(name = 'DigitalInput')
            digitalOutput = shield.addCFile(name = 'DigitalOutput')
            
            for i in range(0, 7):
                pinMode.addVariable(name = 'PM' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Memory)
                digitalInput.addVariable(name = 'DI' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Input)
                digitalOutput.addVariable(name = 'DO' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Output)
                pinMode_PublishCode += 'if(PM' + str(i) + ' == HIGH)\n{\n\n  pinMode(' + str(i) + ', OUTPUT);\n  pullUpDnControl(' + str(i) + ', PUD_OFF);\n}\nelse\n{\n  digitalWrite(' + str(i) + ', LOW);\n  pinMode(' + str(i) + ', INPUT);\n  pullUpDnControl(' + str(i) + ', PUD_DOWN);\n}\nbitWrite(__GPIO_pinMode__, ' + str(i) + ', PM' + str(i) + ');\n'
                digitalInput_RetrieveCode += 'if(bitRead(__GPIO_pinMode__, ' + str(i) + ') == LOW)\n{\n  DI' + str(i) + ' = digitalRead(' + str(i) + ');\n}\n'
                digitalOutput_PublishCode += 'if(bitRead(__GPIO_pinMode__, ' + str(i) + ') == HIGH)\n{\n  digitalWrite(' + str(i) + ', DO' + str(i) + ');\n}\n'
                initializeCode += 'pinMode(' + str(i) + ', INPUT);\npullUpDnControl(' + str(i) + ', PUD_DOWN);\n'
            for i in range(17, 21):
                pinMode.addVariable(name = 'PM' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Memory)
                digitalInput.addVariable(name = 'DI' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Input)
                digitalOutput.addVariable(name = 'DO' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Output)
                pinMode_PublishCode += 'if(PM' + str(i) + ' == HIGH)\n{\n\n  pinMode(' + str(i) + ', OUTPUT);\n  pullUpDnControl(' + str(i) + ', PUD_OFF);\n}\nelse\n{\n  digitalWrite(' + str(i) + ', LOW);\n  pinMode(' + str(i) + ', INPUT);\n  pullUpDnControl(' + str(i) + ', PUD_DOWN);\n}\nbitWrite(__GPIO_pinMode__, ' + str(i) + ', PM' + str(i) + ');\n'
                digitalInput_RetrieveCode += 'if(bitRead(__GPIO_pinMode__, ' + str(i) + ') == LOW)\n{\n  DI' + str(i) + ' = digitalRead(' + str(i) + ');\n}\n'
                digitalOutput_PublishCode += 'if(bitRead(__GPIO_pinMode__, ' + str(i) + ') == HIGH)\n{\n  digitalWrite(' + str(i) + ', DO' + str(i) + ');\n}\n'
                initializeCode += 'pinMode(' + str(i) + ', INPUT);\npullUpDnControl(' + str(i) + ', PUD_DOWN);\n'
                
            pinMode.setPublishCode(pinMode_PublishCode)
            pinMode.setGlobalCode(globalCode)
            pinMode.setInitializeCode(initializeCode)
            digitalInput.setRetrieveCode(digitalInput_RetrieveCode)
            digitalInput.setGlobalCode(globalCode)
            digitalOutput.setPublishCode(digitalOutput_PublishCode)
            digitalOutput.setGlobalCode(globalCode)
            
            return shield

    class ModbusDevices(object):
        @staticmethod
        def getDriver(driver):
            if driver == 'ArduinoDuemilanove':
                return Drivers.ModbusDevices.__ArduinoDuemilanove__()
            return None

        @staticmethod
        def listNames():
            list = range(0, 0)
            list.append('ArduinoDuemilanove')
            return list
            
        @staticmethod
        def listTree():
            l = range(0,0)
            espees_drivers_dir = os.path.join(getSaveFolder(), 'Drivers')
            espees_dev_dir = os.path.join(espees_drivers_dir, 'Modbus modules')
            rootPath = espees_dev_dir
            pattern = '*.drv'
            print '\nModbus modules:\n'
            for root, dirs, files in os.walk(rootPath):
                for filename in fnmatch.filter(files, pattern):
                    entry = os.path.join(root, filename).replace(espees_dev_dir, '').replace('.drv', '').split(os.sep)
                    del entry[0]
                    l.append(entry)
            return l
                            
        @staticmethod
        def listDrivers():
            list = range(0, 0)
            list.append(Drivers.ModbusDevices.__ArduinoDuemilanove__())
            return list

        @staticmethod
        def __ArduinoDuemilanove__():
            
            # Variables to define the modbus-device
            name = 'ArduinoDuemilanove'
            registerCode = 'enum { AnalogIn0, AnalogIn1, AnalogIn2, AnalogIn3, AnalogIn4, AnalogIn5, PinMode, DigitalInput, DigitalOutput, TotalErrors, TotalRegistersSize };\n'
            registerSize = 10
            pinMode_PublishCode = 'int16_t bits = 0;\n'
            analogInput_RetrieveCode = ''
            digitalInput_RetrieveCode = ''
            digitalOutput_PublishCode = 'int16_t bits = 0;\n'
            
            # Create modbus-device instance.
            device = ModbusDevice(name = name,
                                  registerCode = registerCode,
                                  registerSize = registerSize)
            device.__setDeviceName__(name)
            
            # Create c-files.
            pinMode = device.addCFile(name = 'PinMode')
            analogInput = device.addCFile(name = 'AnalogInput')
            digitalInput = device.addCFile(name = 'DigitalInput')
            digitalOutput = device.addCFile(name = 'DigitalOutput')
            
            # Add variables and c-code to all c-file instances.
            for i in range(2, 14):
                pinMode.addVariable(name = 'PM' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Memory)
                digitalInput.addVariable(name = 'DI' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Input)
                digitalOutput.addVariable(name = 'DO' + str(i),
                                    dataType = DataTypes.BOOL,
                                    memoryType = MemoryTypes.Output)
                pinMode_PublishCode += 'bitWrite(bits, ' + str(i) + ', PM' + str(i) + ');\n'
                digitalInput_RetrieveCode += 'DI' + str(i) + ' = bitRead(Registers[DigitalInput], ' + str(i) + ');\n'
                digitalOutput_PublishCode += 'bitWrite(bits, ' + str(i) + ', DO' + str(i) + ');\n'
            for i in range(0, 6):
                analogInput.addVariable(name = 'AI' + str(i),
                                    dataType = DataTypes.UINT,
                                    memoryType = MemoryTypes.Input)
                analogInput_RetrieveCode += 'AI' + str(i) + ' = Registers[AnalogIn' + str(i) + '];\n'
            pinMode_PublishCode += 'Registers[PinMode] = bits;\n';
            digitalOutput_PublishCode += 'Registers[DigitalOutput] = bits;\n';
            pinMode.setPublishCode(pinMode_PublishCode)
            analogInput.setRetrieveCode(analogInput_RetrieveCode)
            digitalInput.setRetrieveCode(digitalInput_RetrieveCode)
            digitalOutput.setPublishCode(digitalOutput_PublishCode)
            
            return device
        
    class SPIDevices(object):
        @staticmethod
        def getDriver(driver):
            return None
        
        @staticmethod
        def listNames():
            list = range(0, 0)
            return list
            
        @staticmethod
        def listTree():
            l = range(0,0)
            espees_drivers_dir = os.path.join(getSaveFolder(), 'Drivers')
            espees_dev_dir = os.path.join(espees_drivers_dir, 'SPI modules')
            rootPath = espees_dev_dir
            pattern = '*.drv'
            print '\nSPI modules:\n'
            for root, dirs, files in os.walk(rootPath):
                for filename in fnmatch.filter(files, pattern):
                    entry = os.path.join(root, filename).replace(espees_dev_dir, '').replace('.drv', '').split(os.sep)
                    del entry[0]
                    l.append(entry)
            return l
        
        @staticmethod
        def listDrivers():
            list = range(0, 0)
            return list
        
    class I2CDevices(object):
        @staticmethod
        def getDriver(driver):
            return None
        
        @staticmethod
        def listNames():
            list = range(0, 0)
            return list
        
        @staticmethod
        def listDrivers():
            list = range(0, 0)
            return list
            
    @staticmethod
    def listModuleTypes():
        l = range(0, 0)
        l.append('Modbus modules')
        l.append('SPI modules')
        l.append('Shields')
        return l
        
    @staticmethod
    def listTree():
        rootPath = '/home/clausismus/.EsPeEs/Drivers/Modbus modules'
        pattern = '*.drv'
        for root, dirs, files in os.walk(rootPath):
            for filename in fnmatch.filter(files, pattern):
                print( os.path.join(root, filename).replace('/home/clausismus/.EsPeEs/Drivers/Modbus modules/', ''))

@Singleton
class DriverManager(object):
    
    class Type(object):
        NotExist = 'NotExist'
        Directory = 'Directory'
        Driver = 'Driver'
        CFile = 'CFile'
    
    def __init__(self):
        if not os.path.exists(os.path.join(getSaveFolder(), 'Drivers')):
            shutil.copytree(os.getcwd() + os.sep + 'Drivers', os.path.join(getSaveFolder(), 'Drivers'))
        if os.path.exists(self.__getDriverPath__(CExtension.Type.ModbusDevice)) == False:
            os.makedirs(self.__getDriverPath__(CExtension.Type.ModbusDevice))
        if os.path.exists(self.__getDriverPath__(CExtension.Type.SPIDevice)) == False:
            os.makedirs(self.__getDriverPath__(CExtension.Type.SPIDevice))
        if os.path.exists(self.__getDriverPath__(CExtension.Type.Shield)) == False:
            os.makedirs(self.__getDriverPath__(CExtension.Type.Shield))
        if os.path.exists(self.__getDriverPath__(CExtension.Type.I2CDevice)) == False:
            os.makedirs(self.__getDriverPath__(CExtension.Type.I2CDevice))
        if os.path.exists(self.__getDriverPath__(CExtension.Type.TargetDevice)) == False:
            os.makedirs(self.__getDriverPath__(CExtension.Type.TargetDevice))
        self.__reloadDrivers__(CExtension.Type.ModbusDevice)
        self.__reloadDrivers__(CExtension.Type.SPIDevice)
        self.__reloadDrivers__(CExtension.Type.I2CDevice)
        self.__reloadDrivers__(CExtension.Type.Shield)
        self.__reloadDrivers__(CExtension.Type.TargetDevice)
        
    def getPCShield(self):
        # Variables to define the shield
        name = '__PC__'
            
        # Create shield instance.
        shield = Shield(name, True, False, False)
        shield.__setDeviceName__(name)
        return shield
        
    def getEntryType(self, path, cextensionType):
        if self.directoryExist(path, cextensionType):
            return 'Directory'
        if self.driverExist(path, cextensionType):
            return 'Driver'
        if self.cfileExist(path, cextensionType):
            return 'CFile'
        return 'NotExist'
        
    def directoryExist(self, path, cextensionType):
        return os.path.isdir(self.__getAbsolutePath__(path, cextensionType))
        
    def listDirectories(self, cextensionType):
        l = range(0, 0)
        if cextensionType == CExtension.Type.ModbusDevice:
            return self.__ModbusDirectories
        if cextensionType == CExtension.Type.SPIDevice:
            return self.__SPIDirectories
        if cextensionType == CExtension.Type.I2CDevice:
            return self.__I2CDirectories
        if cextensionType == CExtension.Type.Shield:
            return self.__ShieldDirectories
        if cextensionType == CExtension.Type.TargetDevice:
            return self.__TargetDirectories
        return l
        
    def createDirectory(self, path, cextensionType):
        if self.directoryExist(path, cextensionType) == False:
            os.makedirs(self.__getAbsolutePath__(path, cextensionType))
            self.__reloadDrivers__(cextensionType)
            
    def removeDirectory(self, path, cextensionType):
        if self.directoryExist(path, cextensionType) == True:
            Utilities.removeDirectory(self.__getAbsolutePath__(path, cextensionType))
            self.__reloadDrivers__(cextensionType)
            
    def renameDirectory(self, newName, path, cextensionType):
        if self.childExist(newName, self.removePath(path), cextensionType) == False:
            Utilities.moveDirectory(self.__getAbsolutePath__(path, cextensionType), self.__getAbsolutePath__(self.joinPath(self.removePath(path), newName), cextensionType))
            self.__reloadDrivers__(cextensionType)
        
    def driverExist(self, path, cextensionType):
        return os.path.isfile(self.__getAbsolutePath__(path, cextensionType) + '.drv')
        
    def listDrivers(self, cextensionType):
        l = range(0, 0)
        if cextensionType == CExtension.Type.ModbusDevice:
            l = self.__ModbusDrivers_Paths
        if cextensionType == CExtension.Type.SPIDevice:
            l = self.__SPIDrivers_Paths
        if cextensionType == CExtension.Type.I2CDevice:
            l = self.__I2CDrivers_Paths
        if cextensionType == CExtension.Type.Shield:
            l = self.__ShieldDrivers_Paths
        if cextensionType == CExtension.Type.TargetDevice:
            l = self.__TargetDrivers_Paths
        return l
        
    def listChilds(self, path, cextensionType):
        l = range(0, 0)
        if self.getEntryType(path, cextensionType) == 'Directory':
            abspath = self.__getAbsolutePath__(path, cextensionType)
            entries = Utilities.listDirectory(abspath)
            newEntries = range(0, 0)
            for i in range(len(entries)):
                if Utilities.isFileOrDirectory(os.path.join(abspath, entries[i])) == 'Directory':
                    newEntries.append(entries[i])
                else:
                    if entries[i].endswith('.drv'):
                        newEntries.append(entries[i].replace('.drv', ''))
            return newEntries
        if self.getEntryType(path, cextensionType) == 'Driver':
            return self.getDriver(path, cextensionType).listCFiles()
        return l
        
    def childExist(self, name, path, cextensionType):
        childs = self.listChilds(path, cextensionType)
        for i in range(len(childs)):
            if childs[i] == name:
                return True
        return False
        
    def hasChilds(self, path, cextensionType):
        if len(self.listChilds(path, cextensionType)) ==  0:
            return False
        else:
            return True
            
    def listAvailablePLCs(self, target):
        l = range(0, 0)
        plcs = self.listDrivers(CExtension.Type.TargetDevice)
        drv = None
        for plc in plcs:
            drv = self.getDriver(plc, CExtension.Type.TargetDevice)
            if target == drv.getTarget():
                l.append(plc)
        return l
        
    def createDriver(self, path, cextensionType, registers = None, isModbusCompatible = None, isSPICompatible = None, isI2CCompatible = None, adress = 0, hasTenBitAdress = False, hasSubAdress = False, target = None, libraries = None):
        if self.driverExist(path, cextensionType) == False:
            if cextensionType == CExtension.Type.ModbusDevice:
                modbusDevice = ModbusDevice(name = path[-1])
                modbusDevice.__setDeviceName__(path[-1])
                if not (registers == None):
                    modbusDevice.setRegisters(registers)
                text = Utilities.objectToJson(modbusDevice)
                Utilities.writeToFile(text, self.__getAbsolutePath__(path, cextensionType) + '.drv')
                self.__reloadDrivers__(cextensionType)
                
            if cextensionType == CExtension.Type.SPIDevice:
                spiDevice = SPIDevice(name = path[-1])
                spiDevice.__setDeviceName__(path[-1])
                text = Utilities.objectToJson(spiDevice)
                Utilities.writeToFile(text, self.__getAbsolutePath__(path, cextensionType) + '.drv')
                self.__reloadDrivers__(cextensionType)
                
            if cextensionType == CExtension.Type.TargetDevice:
                mc = False
                sc = False
                ic = False
                if not (isModbusCompatible == None):
                    mc = isModbusCompatible
                if not (isSPICompatible == None):
                    sc = isSPICompatible
                if not (isI2CCompatible == None):
                    ic = isI2CCompatible
                targetDevice = TargetDevice(name = path[-1], target = target, libraries = libraries, modbusCompatible = mc, spiCompatible = sc, i2cCompatible = ic)
                targetDevice.__setDeviceName__(path[-1])
                text = Utilities.objectToJson(targetDevice)
                Utilities.writeToFile(text, self.__getAbsolutePath__(path, cextensionType) + '.drv')
                self.__reloadDrivers__(cextensionType)
                
            if cextensionType == CExtension.Type.I2CDevice:
                i2cDevice = I2CDevice(name = path[-1])
                i2cDevice.__setDeviceName__(path[-1])
                i2cDevice.setHasTenBitAdress(hasTenBitAdress)
                i2cDevice.setHasSubAdress(hasSubAdress)
                i2cDevice.setAdress(adress)
                text = Utilities.objectToJson(i2cDevice)
                Utilities.writeToFile(text, self.__getAbsolutePath__(path, cextensionType) + '.drv')
                self.__reloadDrivers__(cextensionType)
                
            if cextensionType == CExtension.Type.Shield:
                mc = False
                sc = False
                ic = False
                
                if not (isModbusCompatible == None):
                    mc = isModbusCompatible
                if not (isSPICompatible == None):
                    sc = isSPICompatible
                if not (isI2CCompatible == None):
                    ic = isI2CCompatible
                    
                shield = Shield(name = path[-1], modbusCompatible = mc, spiCompatible = sc, i2cCompatible = ic)
                shield.__setDeviceName__(path[-1])
                text = Utilities.objectToJson(shield)
                Utilities.writeToFile(text, self.__getAbsolutePath__(path, cextensionType) + '.drv')
                self.__reloadDrivers__(cextensionType)
                
    def removeDriver(self, path, cextensionType):
         if self.driverExist(path, cextensionType) == True:
            Utilities.removeFile(self.__getAbsolutePath__(path, cextensionType) + '.drv')
            self.__reloadDrivers__(cextensionType)
            
    def getDriver(self, path, cextensionType):
        if cextensionType == CExtension.Type.ModbusDevice:
            if self.driverExist(path, cextensionType) == True:
                for i in range(len(self.__ModbusDrivers_Paths)):
                    if self.__getAbsolutePath__(path, cextensionType) == self.__getAbsolutePath__(self.__ModbusDrivers_Paths[i], cextensionType):
                        return self.__ModbusDrivers[i].clone()
        
        if cextensionType == CExtension.Type.SPIDevice:
            if self.driverExist(path, cextensionType) == True:
                for i in range(len(self.__SPIDrivers_Paths)):
                    if self.__getAbsolutePath__(path, cextensionType) == self.__getAbsolutePath__(self.__SPIDrivers_Paths[i], cextensionType):
                        return self.__SPIDrivers[i].clone()
                        
        if cextensionType == CExtension.Type.I2CDevice:
            if self.driverExist(path, cextensionType) == True:
                for i in range(len(self.__I2CDrivers_Paths)):
                    if self.__getAbsolutePath__(path, cextensionType) == self.__getAbsolutePath__(self.__I2CDrivers_Paths[i], cextensionType):
                        return self.__I2CDrivers[i].clone()
            
        if cextensionType == CExtension.Type.Shield:
            if self.driverExist(path, cextensionType) == True:
                for i in range(len(self.__ShieldDrivers_Paths)):
                    if self.__getAbsolutePath__(path, cextensionType) == self.__getAbsolutePath__(self.__ShieldDrivers_Paths[i], cextensionType):
                        return self.__ShieldDrivers[i].clone()
                        
        if cextensionType == CExtension.Type.TargetDevice:
            if self.driverExist(path, cextensionType) == True:
                for i in range(len(self.__TargetDrivers_Paths)):
                    if self.__getAbsolutePath__(path, cextensionType) == self.__getAbsolutePath__(self.__TargetDrivers_Paths[i], cextensionType):
                        return self.__TargetDrivers[i].clone()
        return None
        
    def setDriver(self, path, driver):
        if not (driver == None):
            Utilities.removeFile(self.__getAbsolutePath__(self.joinPath(self.removePath(path), driver.getDeviceName()), driver.getType()) + '.drv')
            driver.setName(path[-1])
            driver.__setDeviceName__(path[-1])
            text = ''
            text += Utilities.objectToJson(driver)
            Utilities.writeToFile(text, self.__getAbsolutePath__(path, driver.getType()) + '.drv')
            self.__reloadDrivers__(driver.getType())
        
    def cfileExist(self, path, cextensionType):
        drv = self.getDriver(self.removePath(path), cextensionType)
        if not (drv == None):
            return drv.existCFile(path[len(path) - 1])
        return False
        
    def listCFiles(self, cextensionType):
        l = range(0, 0)
        if cextensionType == CExtension.Type.ModbusDevice:
            l = self.__ModbusFiles
        if cextensionType == CExtension.Type.SPIDevice:
            l = self.__SPICFiles
        if cextensionType == CExtension.Type.I2CDevice:
            l = self.__I2CCFiles
        if cextensionType == CExtension.Type.Shield:
            l = self.__ShieldCFiles
        if cextensionType == CExtension.Type.TargetDevice:
            l = self.__TargetCFiles
        return l
       
    def createCFile(self, path, cextensionType):
        name = path[len(path) - 1]
        newPath = self.removePath(path)
        if self.cfileExist(path, cextensionType) == False:
            drv = self.getDriver(newPath, cextensionType)
            if not (drv == None):
                drv.addCFile(name = name)
        self.setDriver(newPath, drv)
        
    def removeCFile(self, path, cextensionType):
        name = path[len(path) - 1]
        newPath = self.removePath(path)
        if self.cfileExist(path, cextensionType) == True:
            drv = self.getDriver(newPath, cextensionType)
            if not (drv == None):
                drv.removeCFile(name = name)
            self.setDriver(newPath, drv)
        
    def getCFile(self, path, cextensionType):
        name = path[len(path) - 1]
        newPath = self.removePath(path)
        if self.cfileExist(path, cextensionType) == True:
            drv = self.getDriver(newPath, cextensionType)
            if not (drv == None):
                return drv.getCFile(name = name)
        return None
        
    def setCFile(self, path, cextensionType, cfile):
        name = path[len(path) - 1]
        newPath = self.removePath(path)
        if self.cfileExist(path, cextensionType) == True:
            drv = self.getDriver(newPath, cextensionType)
            if not (drv == None) and not (cfile == None):
                drv.setCFile(name = name, cfile = cfile)
                
    def joinPath(self, path, name):
        l = range(0, 0)
        for i in range(len(path)):
            l.append(path[i])
        l.append(name)
        return l
        
    def removePath(self, path):
        l = range(0, 0)
        if len(path) > 0:
            for i in range(len(path) - 1):
                l.append(path[i])
        return l
    
    def __getDriverPath__(self, cextensionType):
        espees_drivers_dir = os.path.join(getSaveFolder(), 'Drivers')
        if cextensionType == CExtension.Type.ModbusDevice:
            return os.path.join(espees_drivers_dir, 'Modbus modules')   
        if cextensionType == CExtension.Type.SPIDevice:
            return os.path.join(espees_drivers_dir, 'SPI modules')
        if cextensionType == CExtension.Type.I2CDevice:
            return os.path.join(espees_drivers_dir, 'I2C modules')
        if cextensionType == CExtension.Type.Shield:
            return os.path.join(espees_drivers_dir, 'Shields')
        if cextensionType == CExtension.Type.TargetDevice:
            return os.path.join(espees_drivers_dir, 'Programmable Logic Controllers')
            
    def __getAbsolutePath__(self, path, cextensionType):
        newPath = self.__getDriverPath__(cextensionType)
        for i in range(len(path)):
            newPath += os.sep + path[i]
        return newPath
        
    def __listDirectories__(self, cextensionType):
        l = range(0,0)
        rootPath = self.__getDriverPath__(cextensionType)
        for root, dirs, files in os.walk(rootPath):
            for filename in dirs:
                entry = os.path.join(root, filename).replace(rootPath, '').split(os.sep)
                del entry[0]
                l.append(entry)
        return l
        
    def __listDrivers__(self, cextensionType):
        l = range(0,0)
        rootPath = self.__getDriverPath__(cextensionType)
        pattern = '*.drv'
        for root, dirs, files in os.walk(rootPath):
            for filename in fnmatch.filter(files, pattern):
                entry = os.path.join(root, filename).replace(rootPath, '').replace('.drv', '').split(os.sep)
                del entry[0]
                l.append(entry)
        return l
        
    def __listCFiles__(self, cextensionType):
        cfiles = range(0, 0)
        drivers = self.listDrivers(cextensionType)
        if cextensionType == CExtension.Type.ModbusDevice:
			for i in range(len(self.__ModbusDrivers)):
				l = self.__ModbusDrivers[i].listCFiles()
				for g in range(len(l)):
					path = self.joinPath(self.__ModbusDrivers_Paths[i], l[g])
					cfiles.append(path)
                        
        if cextensionType == CExtension.Type.SPIDevice:
			for i in range(len(self.__SPIDrivers)):
				l = self.__SPIDrivers[i].listCFiles()
				for g in range(len(l)):
					path = self.joinPath(self.__SPIDrivers_Paths[i], l[g])
					cfiles.append(path)
                    
        if cextensionType == CExtension.Type.I2CDevice:
			for i in range(len(self.__I2CDrivers)):
				l = self.__I2CDrivers[i].listCFiles()
				for g in range(len(l)):
					path = self.joinPath(self.__I2CDrivers_Paths[i], l[g])
					cfiles.append(path)
                        
        if cextensionType == CExtension.Type.Shield:
			for i in range(len(self.__ShieldDrivers)):
				l = self.__ShieldDrivers[i].listCFiles()
				for g in range(len(l)):
					path = self.joinPath(self.__ShieldDrivers_Paths[i], l[g])
					cfiles.append(path)
                    
        if cextensionType == CExtension.Type.TargetDevice:
			for i in range(len(self.__TargetDrivers)):
				l = self.__TargetDrivers[i].listCFiles()
				for g in range(len(l)):
					path = self.joinPath(self.__TargetDrivers_Paths[i], l[g])
					cfiles.append(path)
        return cfiles
        
    def __loadDriver__(self, path, cextensionType):
        if self.driverExist(path, cextensionType) == True:
            text = Utilities.readFromFile(self.__getAbsolutePath__(path, cextensionType) + '.drv')
            drv = Utilities.jsonToObject(text)
            return drv
        return None
        
    def __reloadDrivers__(self, cextensionType):
        if cextensionType == CExtension.Type.ModbusDevice:
            self.__ModbusDrivers_Paths = self.__listDrivers__(cextensionType)
            self.__ModbusDrivers = range(0, 0)
            for i in range(len(self.__ModbusDrivers_Paths)):
                self.__ModbusDrivers.append(self.__loadDriver__(self.__ModbusDrivers_Paths[i], cextensionType))
            self.__ModbusCFiles = self.__listCFiles__(cextensionType)
            self.__ModbusDirectories = self.__listDirectories__(cextensionType)
            
        if cextensionType == CExtension.Type.SPIDevice:
            self.__SPIDrivers_Paths = self.__listDrivers__(cextensionType)
            self.__SPIDrivers = range(0, 0)
            for i in range(len(self.__SPIDrivers_Paths)):
                self.__SPIDrivers.append(self.__loadDriver__(self.__SPIDrivers_Paths[i], cextensionType))
            self.__SPICFiles = self.__listCFiles__(cextensionType)
            self.__SPIDirectories = self.__listDirectories__(cextensionType)
            
        if cextensionType == CExtension.Type.I2CDevice:
            self.__I2CDrivers_Paths = self.__listDrivers__(cextensionType)
            self.__I2CDrivers = range(0, 0)
            for i in range(len(self.__I2CDrivers_Paths)):
                self.__I2CDrivers.append(self.__loadDriver__(self.__I2CDrivers_Paths[i], cextensionType))
            self.__I2CCFiles = self.__listCFiles__(cextensionType)
            self.__I2CDirectories = self.__listDirectories__(cextensionType)
            
        if cextensionType == CExtension.Type.Shield:
            self.__ShieldDrivers_Paths = self.__listDrivers__(cextensionType)
            self.__ShieldDrivers = range(0, 0)
            for i in range(len(self.__ShieldDrivers_Paths)):
                self.__ShieldDrivers.append(self.__loadDriver__(self.__ShieldDrivers_Paths[i], cextensionType))
            self.__ShieldCFiles = self.__listCFiles__(cextensionType)
            self.__ShieldDirectories = self.__listDirectories__(cextensionType)
            
        if cextensionType == CExtension.Type.TargetDevice:
            self.__TargetDrivers_Paths = self.__listDrivers__(cextensionType)
            self.__TargetDrivers = range(0, 0)
            for i in range(len(self.__TargetDrivers_Paths)):
                self.__TargetDrivers.append(self.__loadDriver__(self.__TargetDrivers_Paths[i], cextensionType))
            self.__TargetCFiles = self.__listCFiles__(cextensionType)
            self.__TargetDirectories = self.__listDirectories__(cextensionType)
                
class Utilities(object):
    
    __Ports = None
    
    @staticmethod
    def isRaspberryPi():
        if sys.platform.startswith('linux') == True:
            isRPi = True
            if not os.path.exists('/dev/ttyAMA0'):
                isRPi = False
            if not os.path.exists('/dev/spidev0.0'):
                isRPi = False
            if not os.path.exists('/dev/spidev0.1'):
                isRPi = False
            if not os.path.exists('/dev/i2c-0'):
                isRPi = False
            if not os.path.exists('/dev/i2c-1'):
                isRPi = False
            return isRPi
        else:
            return False
    
    @staticmethod
    def makeDirectory(directory):
        """
        Creates a directory by the path.

           Args:
               * directory (str) : Path of the directory.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    @staticmethod
    def copyFile(pathFrom, pathTo, maxfileload=10000000):
        fileFrom = open(pathFrom, 'rb')           # read big files in chunks
        fileTo   = open(pathTo,   'wb')           # need b mode here too
        while 1:
            bytesFrom = fileFrom.read(blksize)    # get one block, less at end
            if not bytesFrom: break               # empty after last chunk
            fileTo.write(bytesFrom)
    
    @staticmethod
    def copyDirectory(dirFrom, dirTo, dcount = 0, fcount = 0):
        """
        copy contents of dirFrom and below to dirTo
        """
        for file in os.listdir(dirFrom):                   
            pathFrom = os.path.join(dirFrom, file)
            pathTo   = os.path.join(dirTo,   file)          
            if not os.path.isdir(pathFrom):                  
                try:
                    Utilities.copyFile(pathFrom, pathTo)
                except:
                    pass
            else:
                try:
                    os.mkdir(pathTo) 
                    Utilities.copyDirectory(pathFrom, pathTo)    
                except:
                    pass

            
    @staticmethod
    def removeFile(file):
        """
        Removes a file by the path.

           Args:
               * file (str) : Path of the file
        """
        if os.path.exists(file):
            os.remove(file)
    
    @staticmethod
    def removeDirectory(directory):
        """
        Removes a directory recursively by the path.

           Args:
               * directory (str) : Path of the directory.
        """
        if os.path.exists(directory):
            shutil.rmtree(directory) 
            
    @staticmethod
    def moveDirectory(src, dst):
        if os.path.isdir(src) and not os.path.exists(dst):
            shutil.move(src, dst)
            
    @staticmethod
    def listDirectory(directory):
        """
        List the content of a directory.

           Args:
               * directory (str) : Path of the directory.
        """
        return os.listdir(directory)
    
    @staticmethod
    def isFileOrDirectory(path):
        """
        List the content of a directory.

           Args:
               * directory (str) : Path of the directory.
        """
        if os.path.isdir(path):
            return 'Directory'
        if os.path.isfile(path):
            return 'File'
        return 'None'
    
    @staticmethod
    def writeToFile(text, filename):
        """
        Writes a text to a file.

           Args:
               * text (str): Text to save.
               * filename (str): Filename of the file.
        """
        if Utilities.isASCII(text) == False:
            text = text.decode('ascii', 'ignore')
        with open(filename,'w') as f:
            f.write(text)
            f.close()
            
    @staticmethod
    def isASCII(text):
        try:
            text.decode('ascii')
            return True
        except:
            return False

    @staticmethod
    def readFromFile(filename):
        """
        Reads a text from a file.

           Args:
               * filename (str): Filename of the file.
            
           Returns:
               Text from file (str).
        """
        with open(filename,'r') as f:
            t = f.read()
            f.close()
            return t

    @staticmethod
    def objectToJson(obj):
        """
        Converts an object to a json string.

           Args:
               * obj (obj): Object.
            
           Returns:
               Converted json string (str).
        """
        return jsonpickle.encode(obj, unpicklable=True)

    @staticmethod
    def jsonToObject(json):
        """
        Converts a json string to an object.

           Args:
               * json (str) : Json string.
            
           Returns:
               Converted object (obj).
        """
        return jsonpickle.decode(json)

    @staticmethod
    def compressJson(obj):
        """
        Compresses a json string with zlib.

           Args:
               * json (str) : Json string.
            
           Returns:
               Compressed json string (str).
        """
        return obj.encode('zlib')

    @staticmethod
    def decompressJson(obj):
        """
        Decompresses a compressed json string with zlib.

           Args:
               * obj (str) : Compressed json string.
            
           Returns:
               Decompressed json string (str).
        """
        return obj.decode('zlib')
            
    @staticmethod
    def packData(unpackedData):
        """
        This function serialize a instance to a json string
        and compress it with zlib.

           Args:
               * unpackedData (str) : Instance, that should be 
                                      serialized and compressed.
            
           Returns:
               The compressed (I think 'int', but I don't really know, because I'm using it as byte).
        """
        ser = Utilities.objectToJson( unpackedData )
        b64 = base64.b64encode(ser)
        return b64

    @staticmethod
    def unpackData(packedData):
        ser = base64.b64decode(packedData)
        obj = Utilities.jsonToObject(ser)
        return obj

    @staticmethod
    def listSerialPorts():
        #if Utilities.__Ports == None:
            if os.name == 'nt':
                available = []
                for i in range(256):
                    try:
                        s = serial.Serial(i)
                        available.append('COM'+str(i + 1))
                        s.close()
                    except serial.SerialException:
                        pass
                return available
            else:
                ports = [port[0] for port in serial.tools.list_ports.comports()]
                if Utilities.isRaspberryPi() == True:
                    exists = False
                    for i in range(len(ports)):
                        if ports[i] == '/dev/ttyAMA0':
                            exists = True
                    if exists == False:
                        ports.append('/dev/ttyAMA0')
                Utilities.__Ports = ports
                return ports
        #else:
        #    return Utilities.__Ports
    
    @staticmethod
    def getLibModbusHeader():
        """
        Returns the header of libModbus.
        
           Returns:
               Header of libModbus (str).
        """
        return Utilities.readFromFile('EsPeEs4Beremiz/EsPeEs_Modbus.h')
    
    @staticmethod
    def getLibModbusContent():
        """
        Returns the content of libModbus.
        
           Returns:
               Content of libModbus (str).
        """
        return Utilities.readFromFile('EsPeEs4Beremiz/EsPeEs_Modbus.c').replace('#include "EsPeEs_Modbus.h"',
                                       Utilities.getLibModbusHeader())
    
    @staticmethod
    def getLibEsPeEsHeader():
        """
        Returns the header of lib
        
           Returns:
               Header of libEsPeEs (str).
        """
        return Utilities.readFromFile('EsPeEs4Beremiz/EsPeEs.h').replace('#include "EsPeEs_Modbus.h"',
                                       Utilities.getLibModbusHeader())
    
    @staticmethod
    def getLibEsPeEsContent():
        """
        Returns the content of lib
        
           Returns:
               Content of libEsPeEs (str).
        """
        return Utilities.readFromFile('EsPeEs4Beremiz/EsPeEs.c').replace('#include "EsPeEs.h"', Utilities.getLibEsPeEsHeader())
 
@Singleton
class ProcessManagement(object):
    def __init__(self):
        self.__EsPeEsServerProcess = None
        self.__EsPeEsCoderProcess = None
        self.__EsPeEsCoderProcess_StopEvent = None
        self.__PLCProcess = None
    
    def startEsPeEsCoder(self,projectPath):
        if self.espeesCoderRunning() == False:
            args = '"' + self.__getPythonExecutablePath__() + '" "' + os.getcwd() + os.sep + 'Peasy-PLC' + os.sep + 'Peasy-PLC.py" "' + os.path.join(os.getcwd() + os.sep + 'EsPeEs-Coder', projectPath) + '"'
            if sys.platform == 'win32':
                self.__EsPeEsCoderProcess = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False, **self.__getProcessArgs__())
            else:
                self.__EsPeEsCoderProcess = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True, **self.__getProcessArgs__())
            self.__EsPeEsCoderProcess.wait()
            self.__EsPeEsCoderProcess = None
    
    def stopEsPeEsCoder(self):
        if not (self.__EsPeEsCoderProcess == None):
            try:
                if sys.platform == 'win32':
                    args = 'tskill ' + str(self.__EsPeEsCoderProcess.pid)
                    kill = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
                    kill.wait()
                else:
                    os.killpg(self.__EsPeEsCoderProcess.pid, signal.SIGKILL)
            except:
                return False
            self.__EsPeEsCoderProcess = None
    
    def espeesCoderRunning(self):
        if self.__EsPeEsCoderProcess == None:
            return False
        else:
            return True
        
    def startEsPeEsServer(self, port):
        if self.espeesServerRunning() == False:
            args = '"' + self.__getPythonExecutablePath__() + '" "' + os.getcwd() + os.sep + 'EsPeEs-Server.py" "--port=' + str(port) + '"'
            if sys.platform == 'win32':
                self.__EsPeEsServerProcess = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False, **self.__getProcessArgs__())
            else:
                self.__EsPeEsServerProcess = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True, **self.__getProcessArgs__())
            
        
    def stopEsPeEsServer(self):
        if not (self.__EsPeEsServerProcess == None):
            try:
                if sys.platform == 'win32':
                    args = 'tskill ' + str(self.__EsPeEsServerProcess.pid)
                    kill = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
                    kill.wait()
                else:
                    os.killpg(self.__EsPeEsServerProcess.pid, signal.SIGKILL)
            except:
                return False
            self.__EsPeEsServerProcess = None
    
    def espeesServerRunning(self):
        if self.__EsPeEsServerProcess == None:
            return False
        else:
            return True
    
    def startPLC_Project(self, project):
        espees_server = os.path.join(getSaveFolder(), 'Server')  
        espees_plc = os.path.join(getSaveFolder(), 'PLC')
        if sys.platform == 'win32':
            projectPath = os.path.join(espees_server, project + os.sep + 'build' + os.sep + project + '.so')
        else:
            projectPath = os.path.join(espees_server, project + os.sep + 'build' + os.sep + project + '.dll')
        if os.path.exists(espees_plc) == True:
            Utilities.removeDirectory(espees_plc)
        Utilities.makeDirectory(espees_plc)
        if sys.platform == 'win32':
            shutil.copyfile(projectPath, espees_plc + os.sep + project + '.dll')
        else:
            shutil.copyfile(projectPath, espees_plc + os.sep + project + '.so')
        Utilities.writeToFile('', os.path.join(espees_plc, 'extra_files.txt'))
        Utilities.writeToFile(project, os.path.join(espees_plc, 'lasttransferedPLC.md5'))
        if self.plcIsRunning() == False:
            args = '"' + self.__getPythonExecutablePath__() + '" "' + os.getcwd() + os.sep + 'Peasy-PLC' + os.sep + 'Peasy-Software-PLC.py" ' + '"-a 1" "-x 0" "-t 0" "' + espees_plc + '"'
            if sys.platform == 'win32':
                self.__PLCProcess = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False, **self.__getProcessArgs__())
            else:
                self.__PLCProcess = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True, **self.__getProcessArgs__())
            
            return True
        else:
            return False
    
    def startPLC_Beremiz(self):
        if self.plcIsRunning() == False:
            espees_plc = os.path.join(getSaveFolder(), 'PLC')
            if os.path.exists(espees_plc) == True:
                Utilities.removeDirectory(espees_plc)
            Utilities.makeDirectory(espees_plc)
            args = '"' + self.__getPythonExecutablePath__() + '" "' + os.getcwd() + os.sep + 'Peasy-PLC' + os.sep + 'Peasy-Software-PLC.py"' + ' "-x 0" "-t 0" "' + espees_plc + '"'
            if sys.platform == 'win32':
                self.__PLCProcess = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False, **self.__getProcessArgs__())
            else:
                self.__PLCProcess = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True, **self.__getProcessArgs__())
            return True
        else:
            return False
    
    def stopPLC(self):
        if self.plcIsRunning() == True:
            try:
                if sys.platform == 'win32':
                    args = 'tskill ' + str(self.__PLCProcess.pid)
                    kill = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
                    kill.wait()
                else:
                    os.killpg(self.__PLCProcess.pid, signal.SIGKILL)
            except:
                return False
            self.__PLCProcess = None
            return True
        else:
            return False
            
    def __getProcessArgs__(self):
        kwargs = {}
        if sys.platform == 'win32':
            CREATE_NEW_PROCESS_GROUP = 0x00000200  # note: could get it from subprocess
            DETACHED_PROCESS = 0x00000008          # 0x8 | 0x200 == 0x208
            kwargs.update(creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)  
        elif sys.version_info < (3, 2):  # assume posix
            kwargs.update(preexec_fn=os.setsid)
        else:  # Python 3.2+ and Unix
            kwargs.update(start_new_session=True)
        return kwargs
    
    def plcIsRunning(self):
        if self.__PLCProcess == None:
            return False
        else:
            return True
            
    def grabEsPeEsCoderProcess(self):
        return self.__grabProcess__('EsPeEs-Coder.py')
        
    def grabEsPeEsServerProcess(self):
        return self.__grabProcess__('EsPeEs-Server.py')

    def grabPLCProcess(self):
        return self.__grabProcess__('Beremiz_server.py')
        
    def countEsPeEsCoderProcesses(self):
        counter = 0
        for proc in psutil.process_iter():
            try:
                if self.__existProcess__('EsPeEs-Coder.py', proc.cmdline) == True:
                    counter = counter + 1
            except psutil.AccessDenied:
                pass
        return counter 
        
    def countEsPeEsServerProcesses(self):
        counter = 0
        for proc in psutil.process_iter():
            try:
                if self.__existProcess__('EsPeEs-Server.py', proc.cmdline) == True:
                    counter = counter + 1
            except psutil.AccessDenied:
                pass
        return counter
        
    def countPLCProcesses():
        counter = 0
        for proc in psutil.process_iter(self):
            try:
                if self.__existProcess__('Beremiz_service.py', proc.cmdline) == True:
                    counter = counter + 1
            except psutil.AccessDenied:
                pass
        return counter
        
    def takeEsPeEsServerProcess(self):
        self.__EsPeEsServerProcess = self.grabEsPeEsServerProcess()
        
    def processesHaveToBeRepaired(self):
        haveToBeRepaired = False
        if self.countEsPeEsCoderProcesses() > 0:
            haveToBeRepaired = True
        if self.countEsPeEsServerProcesses() > 1:
            haveToBeRepaired = True
        if self.countPLCProcesses() > 1:
            haveToBeRepaired = True
        return haveToBeRepaired
    
    def repairProcesses(self):
        killAlsoBeremizService = False
        if self.countEsPeEsCoderProcesses() > 0:
            for proc in psutil.process_iter():
                try:
                    if self.__existProcess__('EsPeEs-Coder.py', proc.cmdline) == True:
                        self.killProcess(proc.pid)
                except psutil.AccessDenied:
                    pass
        if self.countEsPeEsServerProcesses() > 1:
            killAlsoBeremizService = True
            for proc in psutil.process_iter():
                try:
                    if self.__existProcess__('EsPeEs-Server.py', proc.cmdline) == True:
                        self.killProcess(proc.pid)
                except psutil.AccessDenied:
                    pass
        if (self.countPLCProcesses() > 1) or (killAlsoBeremizService == True):
            for proc in psutil.process_iter():
                try:
                    if self.__existProcess__('Beremiz_service.py', proc.cmdline) == True:
                        self.killProcess(proc.pid)
                except psutil.AccessDenied:
                    pass
        return None
        
    def killProcess(self, pid):
        os.killpg(pid, signal.SIGKILL)
        
    def __grabProcess__(self, processName):
        for proc in psutil.process_iter():
            try:
                if self.__existProcess__(processName, proc.cmdline) == True:
                    return proc
            except psutil.AccessDenied:
                pass
        return None
        
    def __existProcess__(self, processName, args):
        pythonExecuteableExist = False
        processNameExist = False
        for i in range(len(args)):
            if not (args[i].find(processName) == -1):
                processNameExist = True
            if not (args[i].find(self.__getPythonExecutablePath__()) == -1):    
                pythonExecuteableExist = True
        return (pythonExecuteableExist and processNameExist)
        
    def __getPythonExecutablePath__(self):
        serverInformation = ServerInformation()
        if serverInformation.isRaspberryPi() == True:
            return 'python'
            #return os.getcwd() + os.sep + 'python' + os.sep + 'python.exe'
        if serverInformation.isLinux() == True:
            return 'python'
            #return os.getcwd() + os.sep + 'python' + os.sep + 'python.exe'
        if serverInformation.isWindows() == True:
            return os.getcwd() + os.sep + 'python' + os.sep + 'python.exe'
        if serverInformation.isMacOSX() == True:
            return 'python'
        return 'python'
        
def executeFunctionAsyncron(function, failedEvent, successEvent, useWx = None):
    class __FunctionAsyncron__(Thread):
        def __init__(self, function, failedEvent, successEvent, useWx = None):
            self.__Function = function
            self.__FailedEvent = failedEvent
            self.__SuccessEvent = successEvent
            self.__UseWx = useWx
            Thread.__init__(self)
            
        def run(self):
            try:
                if self.__Function == None:
                    if not (self.__FailedEvent == None):
                        if self.__UseWx == True:
                            wx.CallAfter(self.__FailedEvent, None)
                        else:
                            self.__FailedEvent(None)
                else:
                    value = self.__Function()
                    if value == None:
                        if not (self.__FailedEvent == None):
                            if self.__UseWx == True:
                                wx.CallAfter(self.__FailedEvent, None)
                            else:
                                self.__FailedEvent(None)
                    else:
                        if self.__UseWx == True:
                            wx.CallAfter(self.__SuccessEvent, value)
                        else:
                            self.__SuccessEvent(value)
            except:
                pass
    functionAsync = __FunctionAsyncron__(function, failedEvent, successEvent, useWx = useWx)
    functionAsync.start()
    return functionAsync

def printObj(obj):
    print Utilities.objectToJson(obj)

def getSaveFolder():
    if sys.platform == 'win32':
        return os.environ['APPDATA'] + os.sep + '.EsPeEs'
    return os.environ['HOME'] + os.sep + '.EsPeEs'

def hasPort(adress):
    if (adress.find(':') == adress.rfind(':')) and not (adress.find(':') == -1):
        return True
    else:
        return False

def legalTCPAdress(adress):
    try:
        if adress.find(':') == -1:
            if __legalIP__(adress) == True:
                return True
            else:
                return __legalHostName__(adress)
        else:
            if not (adress.find(':') == adress.rfind(':')):
                return False
            args = adress.split(':')
            if __legalIP__(args[0]) == True:
                return legalPort(int(args[1]))
            else:
                return __legalHostName__(args[0]) and legalPort(int(args[1]))
    except:
        return False

def __legalIP__(adress):
    try:
        parts = adress.split(".")
        if len(parts) != 4:
            return False
        for item in parts:
            if not 0 <= int(item) <= 255:
                return False
        return True
    except:
        return False
    
def __legalHostName__(adress):
    if (len(adress) > 255) or (len(adress) < 1):
        return False
    if adress.find('.') == -1:
        return __legalLabel__(adress)
    else:
        args = adress.split('.')
        for label in args:
            if __legalLabel__(label) == False:
                return False        
        return True
    
def __legalLabel__(label):
    if (len(label) > 63) or (len(label) < 1):
        return False
    charFound = False
    allowedCharacters = ''
    allowedCharacters += '0123456789'
    allowedCharacters += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    allowedCharacters += 'abcdefghijklmnopqrstuvwxyz'
    allowedCharacters += '-'
    for nc in label:
        charFound = False
        for ac in allowedCharacters:
            if ac == nc:
                charFound = True
                break;
        if charFound == False:
            return False
    return True
    
def extractPort(adress):
    try:
        if adress.find(':') == -1:
            return Preferences.Modbus.DefaultPort
        else:
            if not (adress.find(':') == adress.rfind(':')):
                return None
            args = adress.split(':')
            port = int(args[1])
            return port
    except:
        return None
        
def extractAdress(adress):
    try:
        if adress.find(':') == -1:
            return adress
        else:
            if not (adress.find(':') == adress.rfind(':')):
                return None
            args = adress.split(':')
            return args[0]
    except:
        return None
        
def legalPort(port):
    try:
        if (port < 49152) or (port > 65535):
            return False
        else:
            return True
    except:
        return False
   
def legalName(name):
    if (len(name) > 32) or (len(name) < 1):
        return False
    charFound = False
    allowedCharacters = ''
    allowedCharacters += '0123456789'
    for nr in allowedCharacters:
        if name[0] == nr:
            return False
    allowedCharacters += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    allowedCharacters += 'abcdefghijklmnopqrstuvwxyz'
    allowedCharacters += '_'
    for nc in name:
        charFound = False
        for ac in allowedCharacters:
            if ac == nc:
                charFound = True
                break;
        if charFound == False:
            return False
    return True

__Counter__ = 0
def counterInt():
    global __Counter__
    __Counter__ = __Counter__ + 1
    return __Counter__
    
__Counter__ = 0
def counterStr():
    global __Counter__
    __Counter__ = __Counter__ + 1
    return str(__Counter__)
        
socket.setdefaulttimeout(Preferences.SOAP.TimeOut) 
