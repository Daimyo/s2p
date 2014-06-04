# -*- coding: utf-8 -*-

import re as re
import numpy as np
import matplotlib.pyplot as plt

class s2p():



    def __init__(self, full_name=None):
        
        self.full_name = full_name
        
        self.factor = ''
        self._factor = None
        
        self.format = ''
        self._format = None
        
        self.data = None
        
        self.power = None
        
        self.impedance = None



    def __str__(self):
        
        print 's2p class'



    def __repr__(self):
        
        a = 'File name: '+str(self.get_name())+'\n'
        a += '\n'
        a += '    Format of data:    '+str(self.get_format())+'\n'
        a += '    Impedance:    '+str(self.get_impedance())+'\n'
        
        return a




    def _get_format(self):
        '''Give the format of the file
            
            Input:
                - None
            
            Output:
                - format (String): Format of the file
        '''
        
        temp = self.full_name.split('/')[-1].split('.')
        
        return temp[-1]



    def get_name(self):
        '''Give the name of the file
            
            Input:
                - None
            
            Output:
                - name (String): Name of the file
        '''
        
        temp = self.full_name.split('/')[-1]
        
        return temp[0:len(temp)-len(self._get_format())-1]




    def get_number_point(self):
        '''Give the number of point
            
            Input:
                - None
            
            Output:
                - Number of point (Float)
        '''
        
        if self.data == None :
            self._get_data()
        
        return len(self.data)




    def _get_parameter(self):
        '''Give all the parameters of the s2p file
            
            Input:
                - None
            
            Output:
                - parameters (Array): 
                    - 1 : The frequency format ("HZ", "KHZ", "MHZ", "GHZ")
                    - 2 : The parameter measured ("S")
                    - 3 : The kind of measurement ("MA", "DB", "RI")
                    - 4 : R
                    - 5 : Impedance matching
        '''
        
        f = open(self.full_name, 'r')
        temp = ''
        for i in f.readlines() :
            
            if i[0] == '#' :
                temp = i
                break
        
        parameters = re.split('\s', temp)
        
        while parameters.count('') > 0:
            parameters.remove('')
        
        return parameters



    def get_frequency_factor(self, style='String'):
        '''Give the factor of the frequency and set the attribut factor
            
            Input:
                - Style (String) ["String" | "Float"] : Determined the style of the output
            
            Output:
                - factor (Float): factor of the frequency
                        1.  for  Hz
                        1e3 for KHz
                        1e6 for MHz
                        1e9 for GHz
                         (String): factor of the frequency
                             Hertz
                        Kilo Hertz
                        Mega Hertz
                        Giga Hertz
        '''
        
        freq = self._get_parameter()[1]
        
        answer = ''
        factor = 0
        
        if freq.lower() == 'ghz' :
            answer = 'Giga Hertz'
            factor = 1e9
        
        elif freq.lower() == 'mhz' :
            answer = 'Mega Hertz'
            factor = 1e6
            
        elif freq.lower() == 'khz' :
            answer = 'Kilo Hertz'
            factor = 1e3
            
        else :
            answer = 'Hertz'
            factor = 1.
        
        self.factor = answer
        self._factor = factor
        
        if style == 'String':
            
            return answer
        elif style == 'Float':
            
            return factor
        else :
            
            return 'The style input should be "String" or "Float"'




    def get_format(self):
        '''Give the format of the data and set the attribut format
            
            Input:
                - None
            
            Output:
                - format (String) : Give the format of the data
        '''
        
        kind = self._get_parameter()[3]
        answer = ''
        abrev = ''
        
        if kind.lower() == 'db' :
            answer = 'Decibel-Angle'
            abrev = 'DB'
        
        elif kind.lower() == 'ma' :
            answer = 'Magnitude-Angle'
            abrev = 'MA'
            
        elif kind.lower() == 'ri' :
            answer = 'Real-Imaginary'
            abrev = 'RI'
        else:
            
            raise ValueError('Error: Impossible to find what is the format of the s2p file (not "DB" "MA" or "RI")')
            answer = ''
            abre= None
        
        self.format = answer
        self._format = abrev
        
        return answer




    def get_impedance(self):
        '''Give the matching impedance and se the attribut "impedance"
            
            Input:
                - None
            
            Output:
                - impedance (float) : Value of the matching impedance
        '''
        
        impedance = self._get_parameter()[5]
        
        self.impedance = float(impedance)
        return float(impedance)




    def _get_data(self):
        '''Set the attribut data with all data of the s2p file formatted in a ndarray
            
            Input:
                - None
            
            Output:
                - None
        '''
        
        self.data = np.loadtxt(self.full_name, skiprows=9)




    def get_SParameters(self, S='S21', asked_format='MA'):
        '''get  S parameter from data
            
            Input:
                - S (String) ["S11", "S12", "S21", "S22"]: Set which parameter we want to get
                - asked_format ("String") ["MA", "DB", "RI"]: Set in which format we get data
            
            Output:
                - x, y, z (Tupple): 
                    x: Frequency in Hertz
                    y: if MA amplitude in V, if DB attenuation in dB, if RI real part
                    z: if MA or DB angle in degrees, if RI imaginary part
        '''
        
        self.get_format()
        
        #We check the parameter
        if not re.match('^[sS][12]{2}$', S) :
            
            raise ValueError('The argument "S" should be in the form : "S11", "S12", "S21", "S22"')
        
        if not re.match('^[mM][aA]$|^[rR][iI]$|^[dD][bB]$', asked_format) :
            
            raise ValueError('The argument "asked_format" should be in the form : "MA", "RI", "DB"')
        
        if self.data == None :
            self._get_data()
        
        if self._factor == None :
            self.get_frequency_factor()
        
        if self._format == None :
            self.get_format()
        
        if self._format == 'MA':
            
            if re.match('^[dD][bB]$', asked_format):
                
                if self.impedance == None :
                    self.get_impedance()
                
                if self.power == None :
                    raise ValueError('Error : You have to precise the attribut "power" in dBm')
                else :
                    if S == 'S11':
                        return self.data[:,0]*self._factor , 20.*np.log10(self.data[:,1]/np.sqrt(10.**(self.power/10.)*1e-3*self.impedance)), self.data[:,2]
                    elif S == 'S12':
                        return self.data[:,0]*self._factor , 20.*np.log10(self.data[:,3]/np.sqrt(10.**(self.power/10.)*1e-3*self.impedance)), self.data[:,4]
                    elif S == 'S21':
                        return self.data[:,0]*self._factor , 20.*np.log10(self.data[:,5]/np.sqrt(10.**(self.power/10.)*1e-3*self.impedance)), self.data[:,6]
                    elif S == 'S22':
                        return self.data[:,0]*self._factor , 20.*np.log10(self.data[:,7]/np.sqrt(10.**(self.power/10.)*1e-3*self.impedance)), self.data[:,8]
            
            elif re.match('^[rR][iI]$', asked_format):
                if S == 'S11':
                    return self.data[:,0]*self._factor , np.cos(np.radians(self.data[:,2]))*self.data[:,1], np.sin(np.radians(self.data[:,2]))*self.data[:,1]
                elif S == 'S12':
                    return self.data[:,0]*self._factor , np.cos(np.radians(self.data[:,4]))*self.data[:,3], np.sin(np.radians(self.data[:,4]))*self.data[:,3]
                elif S == 'S21':
                    return self.data[:,0]*self._factor , np.cos(np.radians(self.data[:,6]))*self.data[:,5], np.sin(np.radians(self.data[:,6]))*self.data[:,5]
                elif S == 'S22':
                    return self.data[:,0]*self._factor , np.cos(np.radians(self.data[:,8]))*self.data[:,7], np.sin(np.radians(self.data[:,8]))*self.data[:,7]
            else:
                if S == 'S11':
                    return self.data[:,0]*self._factor , self.data[:,1], self.data[:,2]
                elif S == 'S12':
                    return self.data[:,0]*self._factor , self.data[:,3], self.data[:,4]
                elif S == 'S21':
                    return self.data[:,0]*self._factor , self.data[:,5], self.data[:,6]
                elif S == 'S22':
                    return self.data[:,0]*self._factor , self.data[:,7], self.data[:,8]
        
        elif self._format == 'DB':
            
            if asked_format.lower() == 'ma' :
                if self.impedance is None :
                    self.get_impedance()
                
                if self.power == None :
                    raise ValueError('Error : You have to precise the attribut "power" in dBm')
                else :
                    if S == 'S11':
                        return self.data[:,0]*self._factor , 10.**(self.data[:,1]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance), self.data[:,2]
                    elif S == 'S12':
                        return self.data[:,0]*self._factor , 10.**(self.data[:,3]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance), self.data[:,4]
                    elif S == 'S21':
                        return self.data[:,0]*self._factor , 10.**(self.data[:,5]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance), self.data[:,6]
                    elif S == 'S22':
                        return self.data[:,0]*self._factor , 10.**(self.data[:,7]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance), self.data[:,8]
            elif re.match('^[rR][iI]$', asked_format):
                
                if self.impedance is None :
                    self.get_impedance()
                
                if self.power == None :
                    raise ValueError('Error : You have to precise the attribut "power" in dBm')
                else:
                    if S == 'S11':
                        return self.data[:,0]*self._factor , np.cos(np.radians(self.data[:,2]))*10.**(self.data[:,1]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance), np.sin(np.radians(self.data[:,2]))*10.**(self.data[:,1]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance)
                    elif S == 'S12':
                        return self.data[:,0]*self._factor , np.cos(np.radians(self.data[:,4]))*10.**(self.data[:,3]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance), np.sin(np.radians(self.data[:,4]))*10.**(self.data[:,3]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance)
                    elif S == 'S21':
                        return self.data[:,0]*self._factor , np.cos(np.radians(self.data[:,6]))*10.**(self.data[:,5]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance), np.sin(np.radians(self.data[:,6]))*10.**(self.data[:,5]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance)
                    elif S == 'S22':
                        return self.data[:,0]*self._factor , np.cos(np.radians(self.data[:,8]))*10.**(self.data[:,7]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance), np.sin(np.radians(self.data[:,8]))*10.**(self.data[:,7]/20.)*np.sqrt(10.**(self.power/10.)*1e-3*self.impedance)
            else:
                if S == 'S11':
                    return self.data[:,0]*self._factor , self.data[:,1], self.data[:,2]
                elif S == 'S12':
                    return self.data[:,0]*self._factor , self.data[:,3], self.data[:,4]
                elif S == 'S21':
                    return self.data[:,0]*self._factor , self.data[:,5], self.data[:,6]
                elif S == 'S22':
                    return self.data[:,0]*self._factor , self.data[:,7], self.data[:,8]
        
        elif self._format == 'RI':
            
            if re.match('^[aA][mM]$', asked_format):
                if S == 'S11':
                    return self.data[:,0]*self._factor , np.sqrt(self.data[:,1]**2 + self.data[:,2]**2), np.degrees(np.arctan(self.data[:,2]/self.data[:,1]))
                elif S == 'S12':
                    return self.data[:,0]*self._factor , np.sqrt(self.data[:,3]**2 + self.data[:,4]**2), np.degrees(np.arctan(self.data[:,4]/self.data[:,3]))
                elif S == 'S21':
                    return self.data[:,0]*self._factor , np.sqrt(self.data[:,5]**2 + self.data[:,6]**2), np.degrees(np.arctan(self.data[:,6]/self.data[:,5]))
                elif S == 'S22':
                    return self.data[:,0]*self._factor , np.sqrt(self.data[:,7]**2 + self.data[:,8]**2), np.degrees(np.arctan(self.data[:,8]/self.data[:,7]))
            
            elif re.match('^[dD][bB]$', asked_format):
                if S == 'S11':
                    return self.data[:,0]*self._factor , 20.*np.log10(np.sqrt(self.data[:,1]**2 + self.data[:,2]**2)), np.degrees(np.arctan(self.data[:,2]/self.data[:,1]))
                elif S == 'S12':
                    return self.data[:,0]*self._factor , 20.*np.log10(np.sqrt(self.data[:,3]**2 + self.data[:,4]**2)), np.degrees(np.arctan(self.data[:,4]/self.data[:,3]))
                elif S == 'S21':
                    return self.data[:,0]*self._factor , 20.*np.log10(np.sqrt(self.data[:,5]**2 + self.data[:,6]**2)), np.degrees(np.arctan(self.data[:,6]/self.data[:,5]))
                elif S == 'S22':
                    return self.data[:,0]*self._factor , 20.*np.log10(np.sqrt(self.data[:,7]**2 + self.data[:,8]**2)), np.degrees(np.arctan(self.data[:,8]/self.data[:,7]))
                
                
                else:
                if S == 'S11':
                    return self.data[:,0]*self._factor , self.data[:,1], self.data[:,2]
                elif S == 'S12':
                    return self.data[:,0]*self._factor , self.data[:,3], self.data[:,4]
                elif S == 'S21':
                    return self.data[:,0]*self._factor , self.data[:,5], self.data[:,6]
                elif S == 'S22':
                    return self.data[:,0]*self._factor , self.data[:,7], self.data[:,8]



    def plot_SParameters(self, S='S21' , style='MA'):
        '''plot  S parameter from data
            
            Input:
                - S (String) ["S11", "S12", "S21", "S22"]: Set which parameter you want to plot
                - asked_format ("String") ["MA", "DB", "RI"]: Set in which format we would like to have plot
            
            Output:
                - matplotlib 2d figure
        '''
        
        x, y, z = self.get_SParameters(S, style)
        
        factor = self.get_frequency_factor(style='Float')
    
        if factor == 1. :
            x_label = 'Frequency [Hz]'
        elif factor == 1e3 :
            x_label = 'Frequency [kHz]'
        elif factor == 1e6 :
            x_label = 'Frequency [MHz]'
        elif factor == 1e9 :
            x_label = 'Frequency [GHz]'
        
        fig = plt.figure()
        
        
        if re.match('^[mM][aA]$', style) :
            
            ax1 = fig.add_subplot(211)
            ax1.plot(x, y, label=S)
            plt.ylabel('Amplitude [V]')
            plt.grid()
        elif re.match('^[dD][bB]$', style) :
            
            ax1 = fig.add_subplot(211)
            ax1.plot(x, y, label=S)
            plt.ylabel('Attenuation [dB]')
            plt.grid()
        
        
        if re.match('^[dD][bB]$|^[mM][aA]$', style):
        
            ax2 = fig.add_subplot(212, sharex = ax1)
            ax2.plot(x, z, label=S)
            plt.ylabel('Phase [deg]')
            plt.xlabel(x_label)
        elif re.match('^[rR][iI]$', style):
        
            ax1 = fig.add_subplot(111)
            y = y*1./y.max()
            plt.polar(y, z, label=S)
            plt.title('Normalised amplitude')
            plt.ylabel('Real part')
            plt.ylabel('Imaginary part')
        
        
        plt.legend(loc='best')
        plt.grid()
        plt.show()
