# -*- coding: utf-8 -*-

import re as re
import numpy as np
import matplotlib.pyplot as plt

class s2p():



    def __init__(self, full_name, power = None):
        '''
            Initialize the class by reading all the information in the s2p file.
            
            Input:
                - full_name (string): path and name of the file.
                - power (float): Output power in decibel
            
            Output:
                - None.
        '''
        
        
        self._full_name = full_name
        
        self._frequency_unit = None
        self._format   = None
        self._data     = None
        self._power    = power
        self._R        = None
        
        #We get parameters of the file and we store them into private attributes
        self._get_parameter()
        
        #We get data and store them into private attribute
        self._get_data()



    def __str__(self):
        
        print 's2p class'



    def __repr__(self):
        
        a = 'File name: '+str(self.get_name())+'\n'
        a += '\n'
        a += '    Format of data:    '+str(self.get_format())+'\n'
        a += '    Impedance:    '+str(self.get_impedance())+'\n'
        
        return a




    def get_name(self):
        '''Give the name of the file
            
            Input:
                - None
            
            Output:
                - name (String): Name of the file
        '''
        
        return self._full_name.split('/')[-1].split('.')[0]




    def get_number_point(self):
        '''Give the number of point
            
            Input:
                - None
            
            Output:
                - Number of point (Float)
        '''
        
        return len(self._data)




    def _get_parameter(self):
        '''Give all the parameters of the s2p file
            
            Input:
                - None
            
            Output:
                - parameters (dictionary): 
                    - 1 : The frequency format ("hz", "khz", "mhz", "ghz")
                    - 2 : The parameter measured ("s", "y", "z", "h", "g")
                    - 3 : The kind of measurement ("ma", "rb", "ri")
                    - 5 : Impedance matching
        '''
        
        f = open(self._full_name, 'r')
        temp = ''
        for i in f.readlines() :
            if i[0] == '#' :
                temp = i[1:]
                break
        
        temp = temp.split()
        
        self._frequency_unit = temp[0].lower()
        self._parameter = temp[1].lower()
        self._format    = temp[2].lower()
        self._R         = float(temp[-1])



    def get_frequency_unit(self, style='String'):
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
        
        answer = ''
        factor = 0
        
        if self._frequency_unit == 'ghz' :
            answer = 'Giga Hertz'
            factor = 1e9
        
        elif self._frequency_unit == 'mhz' :
            answer = 'Mega Hertz'
            factor = 1e6
            
        elif self._frequency_unit == 'khz' :
            answer = 'Kilo Hertz'
            factor = 1e3
            
        else :
            answer = 'Hertz'
            factor = 1.
        
        if style.lower() == 'string':
            return answer
        elif style.lower() == 'float':
            return factor
        else :
            raise ValueError('The style input should be "String" or "Float"')




    def get_format(self):
        '''Give the format of the data and set the attribut format
            
            Input:
                - None
            
            Output:
                - format (String) : Give the format of the data
        '''
        
        if self._format == 'db' :
            return 'Decibel-Angle'
        
        elif self._format == 'ma' :
            return 'Magnitude-Angle'
            
        elif self._format == 'ri' :
            return 'Real-Imaginary'
        else:
            raise ValueError('Impossible to find what is the format of the s2p file (not "DB" "MA" or "RI")')




    def get_impedance(self):
        '''Give the matching impedance and se the attribut "impedance"
            
            Input:
                - None
            
            Output:
                - impedance (float) : Value of the matching impedance
        '''
        
        return self._R




    def _get_data(self):
        '''Set the attribut data with all data of the s2p file formatted in a ndarray
            
            Input:
                - None
            
            Output:
                - None
        '''
        
        self._data = np.loadtxt(self._full_name, skiprows=9)




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
        
        #We check the input parameters
        if not re.match('^[sS][12]{2}$', S) :
            raise ValueError('The argument "S" should be in the form : "S11", "S12", "S21", "S22"')
        
        if not re.match('^[mM][aA]$|^[rR][iI]$|^[dD][bB]$', asked_format) :
            raise ValueError('The argument "asked_format" should be in the form : "MA", "RI", "DB"')
        
        #For concision we create short variable names
        d = self._data
        f = self.get_frequency_unit('float')
        r = self._R
        
        if self._format == 'ma':
            
            if re.match('^[dD][bB]$', asked_format):
                
                if self._power == None :
                    raise ValueError('Error : You have to precise the attribut "power" in dBm')
                else :
                    if S.lower() == 's11':
                        return d[:,0]*f , 20.*np.log10(d[:,1]/np.sqrt(10.**(self._power/10.)*1e-3*r)), d[:,2]
                    elif S.lower() == 's12':
                        return d[:,0]*f , 20.*np.log10(d[:,3]/np.sqrt(10.**(self._power/10.)*1e-3*r)), d[:,4]
                    elif S.lower() == 's21':
                        return d[:,0]*f , 20.*np.log10(d[:,5]/np.sqrt(10.**(self._power/10.)*1e-3*r)), d[:,6]
                    elif S.lower() == 's22':
                        return d[:,0]*f , 20.*np.log10(d[:,7]/np.sqrt(10.**(self._power/10.)*1e-3*r)), d[:,8]
            
            elif re.match('^[rR][iI]$', asked_format):
                if S.lower() == 's11':
                    return d[:,0]*f , np.cos(np.radians(d[:,2]))*d[:,1], np.sin(np.radians(d[:,2]))*d[:,1]
                elif S.lower() == 's12':
                    return d[:,0]*f , np.cos(np.radians(d[:,4]))*d[:,3], np.sin(np.radians(d[:,4]))*d[:,3]
                elif S.lower() == 's21':
                    return d[:,0]*f , np.cos(np.radians(d[:,6]))*d[:,5], np.sin(np.radians(d[:,6]))*d[:,5]
                elif S.lower() == 's22':
                    return d[:,0]*f , np.cos(np.radians(d[:,8]))*d[:,7], np.sin(np.radians(d[:,8]))*d[:,7]
            else:
                if S.lower() == 's11':
                    return d[:,0]*f , d[:,1], d[:,2]
                elif S.lower() == 's12':
                    return d[:,0]*f , d[:,3], d[:,4]
                elif S.lower() == 's21':
                    return d[:,0]*f , d[:,5], d[:,6]
                elif S.lower() == 's22':
                    return d[:,0]*f , d[:,7], d[:,8]
        
        elif self._format == 'db':
            if asked_format.lower() == 'ma' :
                
                if self._power == None :
                    raise ValueError('Error : You have to precise the attribut "power" in dBm')
                else :
                    if S.lower() == 's11':
                        return d[:,0]*f , 10.**(d[:,1]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r), d[:,2]
                    elif S.lower() == 's12':
                        return d[:,0]*f , 10.**(d[:,3]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r), d[:,4]
                    elif S.lower() == 's21':
                        return d[:,0]*f , 10.**(d[:,5]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r), d[:,6]
                    elif S.lower() == 's22':
                        return d[:,0]*f , 10.**(d[:,7]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r), d[:,8]
            elif re.match('^[rR][iI]$', asked_format):
                
                if self._power == None :
                    raise ValueError('Error : You have to precise the attribut "power" in dBm')
                else:
                    if S.lower() == 's11':
                        return d[:,0]*f , np.cos(np.radians(d[:,2]))*10.**(d[:,1]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r), np.sin(np.radians(d[:,2]))*10.**(d[:,1]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r)
                    elif S.lower() == 's12':
                        return d[:,0]*f , np.cos(np.radians(d[:,4]))*10.**(d[:,3]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r), np.sin(np.radians(d[:,4]))*10.**(d[:,3]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r)
                    elif S.lower() == 's21':
                        return d[:,0]*f , np.cos(np.radians(d[:,6]))*10.**(d[:,5]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r), np.sin(np.radians(d[:,6]))*10.**(d[:,5]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r)
                    elif S.lower() == 's22':
                        return d[:,0]*f , np.cos(np.radians(d[:,8]))*10.**(d[:,7]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r), np.sin(np.radians(d[:,8]))*10.**(d[:,7]/20.)*np.sqrt(10.**(self._power/10.)*1e-3*r)
            else:
                if S.lower() == 's11':
                    return d[:,0]*f , d[:,1], d[:,2]
                elif S.lower() == 's12':
                    print 'rr'
                    return d[:,0]*f , d[:,3], d[:,4]
                elif S.lower() == 's21':
                    return d[:,0]*f , d[:,5], d[:,6]
                elif S.lower() == 's22':
                    return d[:,0]*f , d[:,7], d[:,8]
        
        elif self._format == 'ri':
            
            if re.match('^[aA][mM]$', asked_format):
                if S.lower() == 's11':
                    return d[:,0]*f , np.sqrt(d[:,1]**2 + d[:,2]**2), np.degrees(np.arctan(d[:,2]/d[:,1]))
                elif S.lower() == 's12':
                    return d[:,0]*f , np.sqrt(d[:,3]**2 + d[:,4]**2), np.degrees(np.arctan(d[:,4]/d[:,3]))
                elif S.lower() == 's21':
                    return d[:,0]*f , np.sqrt(d[:,5]**2 + d[:,6]**2), np.degrees(np.arctan(d[:,6]/d[:,5]))
                elif S.lower() == 's22':
                    return d[:,0]*f , np.sqrt(d[:,7]**2 + d[:,8]**2), np.degrees(np.arctan(d[:,8]/d[:,7]))
            
            elif re.match('^[dD][bB]$', asked_format):
                if S.lower() == 's11':
                    return d[:,0]*f , 20.*np.log10(np.sqrt(d[:,1]**2 + d[:,2]**2)), np.degrees(np.arctan(d[:,2]/d[:,1]))
                elif S.lower() == 's12':
                    return d[:,0]*f , 20.*np.log10(np.sqrt(d[:,3]**2 + d[:,4]**2)), np.degrees(np.arctan(d[:,4]/d[:,3]))
                elif S.lower() == 's21':
                    return d[:,0]*f , 20.*np.log10(np.sqrt(d[:,5]**2 + d[:,6]**2)), np.degrees(np.arctan(d[:,6]/d[:,5]))
                elif S.lower() == 's22':
                    return d[:,0]*f , 20.*np.log10(np.sqrt(d[:,7]**2 + d[:,8]**2)), np.degrees(np.arctan(d[:,8]/d[:,7]))
            else:
                if S.lower() == 's11':
                    return d[:,0]*f , d[:,1], d[:,2]
                elif S.lower() == 's12':
                    return d[:,0]*f , d[:,3], d[:,4]
                elif S.lower() == 's21':
                    return d[:,0]*f , d[:,5], d[:,6]
                elif S.lower() == 's22':
                    return d[:,0]*f , d[:,7], d[:,8]



    def plot_SParameters(self, S='S21' , style='MA'):
        '''plot  S parameter from data
            
            Input:
                - S (String) ["S11", "S12", "S21", "S22"]: Set which parameter you want to plot
                - asked_format ("String") ["MA", "DB", "RI"]: Set in which format we would like to have plot
            
            Output:
                - matplotlib 2d figure
        '''
        
        x, y, z = self.get_SParameters(S, style)
        
        factor = self.get_frequency_unit(style='Float')
    
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
