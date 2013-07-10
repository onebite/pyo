"""
Phase vocoder.

The phase vocoder is a digital signal processing technique of potentially 
great musical significance. It can be used to perform very high fidelity 
time scaling, pitch transposition, and myriad other modifications of sounds.

"""

"""
Copyright 2011 Olivier Belanger

This file is part of pyo, a python module to help digital signal
processing script creation.

pyo is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyo is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyo.  If not, see <http://www.gnu.org/licenses/>.
"""
from _core import *
from _maps import *
from _widgets import createSpectrumWindow
from pattern import Pattern

class PVAnal(PyoPVObject):
    """
    Phase Vocoder analysis object.

    PVAnal takes an input sound and performs the phase vocoder
    analysis on it. This results in two streams, one for the bin's 
    magnitudes and the other for the bin's true frequencies. These 
    two streams are used by the PVxxx object family to transform 
    the input signal using spectral domain algorithms. The last
    object in the phase vocoder chain must be a PVSynh to perform
    the spectral to time domain conversion.
    
    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoObject
            Input signal to process.
        size : int {pow-of-two > 4}, optional
            FFT size. Must be a power of two greater than 4.
            Defaults to 1024.

            The FFT size is the number of samples used in each
            analysis frame. 
        overlaps : int, optional
            The number of overlaped analysis block. Must be a
            power of two. Defaults to 4.
            
            More overlaps can greatly improved sound quality 
            synthesis but it is also more CPU expensive.
        wintype : int, optional
            Shape of the envelope used to filter each input frame.
            Possible shapes are:
                0. rectangular (no windowing)
                1. Hamming
                2. Hanning (default)
                3. Bartlett (triangular)
                4. Blackman 3-term
                5. Blackman-Harris 4-term
                6. Blackman-Harris 7-term
                7. Tuckey (alpha = 0.66)
                8. Sine (half-sine window)

    >>> s = Server().boot()
    >>> s.start()
    >>> a = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=0.7)
    >>> pva = PVAnal(a, size=1024, overlaps=4, wintype=2)
    >>> pvs = PVSynth(pva).mix(2).out()

    """
    def __init__(self, input, size=1024, overlaps=4, wintype=2):
        PyoPVObject.__init__(self)
        self._input = input
        self._size = size
        self._overlaps = overlaps
        self._wintype = wintype
        self._in_fader = InputFader(input)
        in_fader, size, overlaps, wintype, lmax = convertArgsToLists(self._in_fader, size, overlaps, wintype)
        self._base_objs = [PVAnal_base(wrap(in_fader,i), wrap(size,i), wrap(overlaps,i), wrap(wintype,i)) for i in range(lmax)]
 
    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.
            fadetime : float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        self._input = x
        self._in_fader.setInput(x, fadetime)

    def setSize(self, x):
        """
        Replace the `size` attribute.
        
        :Args:

            x : int
                new `size` attribute.
        
        """
        self._size = x
        x, lmax = convertArgsToLists(x)
        [obj.setSize(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setOverlaps(self, x):
        """
        Replace the `overlaps` attribute.
        
        :Args:

            x : int
                new `overlaps` attribute.
        
        """
        self._overlaps = x
        x, lmax = convertArgsToLists(x)
        [obj.setOverlaps(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setWinType(self, x):
        """
        Replace the `wintype` attribute.
        
        :Args:

            x : int
                new `wintype` attribute.
        
        """
        self._wintype = x
        x, lmax = convertArgsToLists(x)
        [obj.setWinType(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def input(self):
        """PyoObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def size(self):
        """int. FFT size."""
        return self._size
    @size.setter
    def size(self, x): self.setSize(x)

    @property
    def overlaps(self):
        """int. FFT overlap factor."""
        return self._overlaps
    @overlaps.setter
    def overlaps(self, x): self.setOverlaps(x)

    @property
    def wintype(self):
        """int. Windowing method."""
        return self._wintype
    @wintype.setter
    def wintype(self, x): self.setWinType(x)

class PVSynth(PyoObject):
    """
    Phase Vocoder synthesis object.

    PVSynth takes a PyoPVObject as its input and performed
    the spectral to time domain conversion on it. This step
    converts phase vocoder magnitude and true frequency's
    streams back to a real signal.
    
    :Parent: :py:class:`PyoObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process.
        wintype : int, optional
            Shape of the envelope used to filter each input frame. 
            Possible shapes are:
                0. rectangular (no windowing)
                1. Hamming
                2. Hanning (default)
                3. Bartlett (triangular)
                4. Blackman 3-term
                5. Blackman-Harris 4-term
                6. Blackman-Harris 7-term
                7. Tuckey (alpha = 0.66)
                8. Sine (half-sine window)

    >>> s = Server().boot()
    >>> s.start()
    >>> a = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=0.7)
    >>> pva = PVAnal(a, size=1024, overlaps=4, wintype=2)
    >>> pvs = PVSynth(pva).mix(2).out()

    """
    def __init__(self, input, wintype=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._wintype = wintype
        input, wintype, mul, add, lmax = convertArgsToLists(self._input, wintype, mul, add)
        self._base_objs = [PVSynth_base(wrap(input,i), wrap(wintype,i), wrap(mul,i), wrap(add,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setWinType(self, x):
        """
        Replace the `wintype` attribute.
        
        :Args:

            x : int
                new `wintype` attribute.
        
        """
        self._wintype = x
        x, lmax = convertArgsToLists(x)
        [obj.setWinType(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def wintype(self):
        """int. Windowing method."""
        return self._wintype
    @wintype.setter
    def wintype(self, x): self.setWinType(x)

class PVAddSynth(PyoObject):
    """
    Phase Vocoder additive synthesis object.

    PVAddSynth takes a PyoPVObject as its input and resynthesize
    the real signal using the magnitude and true frequency's 
    streams to control amplitude and frequency envelopes of an 
    oscillator bank.

    :Parent: :py:class:`PyoObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process.
        pitch : float or PyoObject, optional
            Transposition factor. Defaults to 1.
        num : int, optional
            Number of oscillators used to synthesize the
            output sound. Defaults to 100.
        first : int, optional
            The first bin to synthesize, starting from 0. 
            Defaults to 0.
        inc : int, optional
            Starting from bin `first`, resynthesize bins 
            `inc` apart. Defaults to 1. 
            

    >>> s = Server().boot()
    >>> s.start()
    >>> a = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=0.7)
    >>> pva = PVAnal(a, size=1024, overlaps=4, pitch=2)
    >>> pvs = PVAddSynth(pva, pitch=1.25, num=100, first=0, inc=2)

    """
    def __init__(self, input, pitch=1, num=100, first=0, inc=1, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._pitch = pitch
        self._num = num
        self._first = first
        self._inc = inc
        input, pitch, num, first, inc, mul, add, lmax = convertArgsToLists(self._input, pitch, num, first, inc, mul, add)
        self._base_objs = [PVAddSynth_base(wrap(input,i), wrap(pitch,i), wrap(num,i), wrap(first,i), wrap(inc,i), wrap(mul,i), wrap(add,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setPitch(self, x):
        """
        Replace the `pitch` attribute.
        
        :Args:

            x : float or PyoObject
                new `pitch` attribute.
        
        """
        self._pitch = x
        x, lmax = convertArgsToLists(x)
        [obj.setPitch(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setNum(self, x):
        """
        Replace the `num` attribute.
        
        :Args:

            x : int
                new `num` attribute.
        
        """
        self._num = x
        x, lmax = convertArgsToLists(x)
        [obj.setNum(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setFirst(self, x):
        """
        Replace the `first` attribute.
        
        :Args:

            x : int
                new `first` attribute.
        
        """
        self._first = x
        x, lmax = convertArgsToLists(x)
        [obj.setFirst(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setInc(self, x):
        """
        Replace the `inc` attribute.
        
        :Args:

            x : int
                new `inc` attribute.
        
        """
        self._inc = x
        x, lmax = convertArgsToLists(x)
        [obj.setInc(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0.25, 4, "lin", "pitch", self._pitch),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def pitch(self):
        """float or PyoObject. Transposition factor."""
        return self._pitch
    @pitch.setter
    def pitch(self, x): self.setPitch(x)

    @property
    def num(self):
        """int. Number of oscillators."""
        return self._num
    @num.setter
    def num(self, x): self.setNum(x)

    @property
    def first(self):
        """int. First bin to synthesize."""
        return self._first
    @first.setter
    def first(self, x): self.setFirst(x)

    @property
    def inc(self):
        """int. Synthesized bin increment."""
        return self._inc
    @inc.setter
    def inc(self, x): self.setInc(x)

class PVTranspose(PyoPVObject):
    """
    Transpose the frequency components of a pv stream.
    
    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process.
        transpo : float or PyoObject, optional
            Transposition factor. Defaults to 1.

    >>> s = Server().boot()
    >>> s.start()
    >>> sf = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.7)
    >>> pva = PVAnal(sf, size=1024)
    >>> pvt = PVTranspose(pva, transpo=1.5)
    >>> pvs = PVSynth(pvt).out()
    >>> dry = Delay(sf, delay=1024./s.getSamplingRate(), mul=.7).out(1)

    """
    def __init__(self, input, transpo=1):
        PyoPVObject.__init__(self)
        self._input = input
        self._transpo = transpo
        input, transpo, lmax = convertArgsToLists(self._input, transpo)
        self._base_objs = [PVTranspose_base(wrap(input,i), wrap(transpo,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setTranspo(self, x):
        """
        Replace the `transpo` attribute.
        
        :Args:

            x : int
                new `transpo` attribute.
        
        """
        self._transpo = x
        x, lmax = convertArgsToLists(x)
        [obj.setTranspo(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0.25, 4, "lin", "transpo", self._transpo)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def transpo(self):
        """float or PyoObject. Transposition factor."""
        return self._transpo
    @transpo.setter
    def transpo(self, x): self.setTranspo(x)

class PVVerb(PyoPVObject):
    """
    Spectral domain reverberation.

    :Parent: :py:class:`PyoPVObject`

    :Args:

        input : PyoPVObject
            Phase vocoder streaming object to process.
        revtime : float or PyoObject, optional
            Reverberation factor, between 0 and 1. 
            Defaults to 0.75.
        damp : float or PyoObject, optional
            High frequency damping factor, between 0 and 1. 
            1 means no damping and 0 is the most damping.
            Defaults to 0.75.

    >>> s = Server().boot()
    >>> s.start()
    >>> sf = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.5)
    >>> pva = PVAnal(sf, size=2048)
    >>> pvg = PVGate(pva, thresh=-36, damp=0)
    >>> pvv = PVVerb(pvg, revtime=0.95, damp=0.95)
    >>> pvs = PVSynth(pvv).mix(2).out()
    >>> dry = Delay(sf, delay=2048./s.getSamplingRate(), mul=.4).mix(2).out()

    """
    def __init__(self, input, revtime=0.75, damp=0.75):
        PyoPVObject.__init__(self)
        self._input = input
        self._revtime = revtime
        self._damp = damp
        input, revtime, damp, lmax = convertArgsToLists(self._input, revtime, damp)
        self._base_objs = [PVVerb_base(wrap(input,i), wrap(revtime,i), wrap(damp,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setRevtime(self, x):
        """
        Replace the `revtime` attribute.
        
        :Args:

            x : int
                new `revtime` attribute.
        
        """
        self._revtime = x
        x, lmax = convertArgsToLists(x)
        [obj.setRevtime(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setDamp(self, x):
        """
        Replace the `damp` attribute.
        
        :Args:

            x : int
                new `damp` attribute.
        
        """
        self._damp = x
        x, lmax = convertArgsToLists(x)
        [obj.setDamp(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0, 1, "lin", "revtime", self._revtime),
                          SLMap(0, 1, "lin", "damp", self._damp)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def revtime(self):
        """float or PyoObject. Reverberation factor."""
        return self._revtime
    @revtime.setter
    def revtime(self, x): self.setRevtime(x)
    
    @property
    def damp(self):
        """float or PyoObject. High frequency damping factor."""
        return self._damp
    @damp.setter
    def damp(self, x): self.setDamp(x)

class PVGate(PyoPVObject):
    """
    Spectral gate.

    :Parent: :py:class:`PyoObject`

    :Args:

        input : PyoPVObject
            Phase vocoder streaming object to process.
        thresh : float or PyoObject, optional
            Threshold factor in dB. Bins below that threshold
            will be scaled by `damp` factor. Defaults to -20.
        damp : float or PyoObject, optional
            Damping factor for low amplitude bins. Defaults to 0.

    >>> s = Server().boot()
    >>> s.start()
    >>> sf = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.5)
    >>> pva = PVAnal(sf, size=2048)
    >>> pvg = PVGate(pva, thresh=-50, damp=0)
    >>> pvs = PVSynth(pvg).mix(2).out()

    """
    def __init__(self, input, thresh=-20, damp=0.):
        PyoPVObject.__init__(self)
        self._input = input
        self._thresh = thresh
        self._damp = damp
        input, thresh, damp, lmax = convertArgsToLists(self._input, thresh, damp)
        self._base_objs = [PVGate_base(wrap(input,i), wrap(thresh,i), wrap(damp,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setThresh(self, x):
        """
        Replace the `thresh` attribute.
        
        :Args:

            x : int
                new `thresh` attribute.
        
        """
        self._thresh = x
        x, lmax = convertArgsToLists(x)
        [obj.setThresh(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setDamp(self, x):
        """
        Replace the `damp` attribute.
        
        :Args:

            x : int
                new `damp` attribute.
        
        """
        self._damp = x
        x, lmax = convertArgsToLists(x)
        [obj.setDamp(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(-120, 18, "lin", "thresh", self._thresh),
                          SLMap(0, 2, "lin", "damp", self._damp)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def thresh(self):
        """float or PyoObject. Threshold factor."""
        return self._thresh
    @thresh.setter
    def thresh(self, x): self.setThresh(x)
    
    @property
    def damp(self):
        """float or PyoObject. Damping factor for low amplitude bins."""
        return self._damp
    @damp.setter
    def damp(self, x): self.setDamp(x)

class PVCross(PyoPVObject):
    """
    Performs cross-synthesis between two phase vocoder streaming object.
    
    The amplitudes from `input` and `input2` (scaled by `fade` argument)
    are applied to the frequencies of `input`.

    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process. Frequencies from
            this pv stream are used to compute the output signal.
        input2 : PyoPVObject
            Phase vocoder streaming object which gives the second set of
            magnitudes. Frequencies from this pv stream are not used.
        fade : float or PyoObject, optional
            Scaling factor for the output amplitudes, between 0 and 1. 
            0 means amplitudes from `input` and 1 means amplitudes from `input2`. 
            Defaults to 1.

    .. note::
        
        The two input pv stream must have the same size and overlaps. It is
        the responsibility of the user to be sure they are consistent. To change
        the size (or the overlaps) of the phase vocoder process, one must
        write a function to change both at the same time (see the example below).
        Another possibility is to use channel expansion to analyse both sounds
        with the same PVAnal object.

    >>> s = Server().boot()
    >>> s.start()
    >>> sf = SineLoop(freq=[80,81], feedback=0.07, mul=.5)
    >>> sf2 = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.5)
    >>> pva = PVAnal(sf)
    >>> pva2 = PVAnal(sf2)
    >>> pvc = PVCross(pva, pva2, fade=1)
    >>> pvs = PVSynth(pvc).out()
    >>> def size(x):
    ...     pva.size = x
    ...     pva2.size = x
    >>> def olaps(x):
    ...     pva.overlaps = x
    ...     pva2.overlaps = x

    """
    def __init__(self, input, input2, fade=1):
        PyoPVObject.__init__(self)
        self._input = input
        self._input2 = input2
        self._fade = fade
        input, input2, fade, lmax = convertArgsToLists(self._input, self._input2, fade)
        self._base_objs = [PVCross_base(wrap(input,i), wrap(input2,i), wrap(fade,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setInput2(self, x):
        """
        Replace the `input2` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input2 = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput2(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setFade(self, x):
        """
        Replace the `fade` attribute.
        
        :Args:

            x : int
                new `fade` attribute.
        
        """
        self._fade = x
        x, lmax = convertArgsToLists(x)
        [obj.setFade(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0, 1, "lin", "fade", self._fade)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def input2(self):
        """PyoPVObject. Second set of amplitudes.""" 
        return self._input2
    @input2.setter
    def input2(self, x): self.setInput2(x)

    @property
    def fade(self):
        """float or PyoObject. Scaling factor."""
        return self._fade
    @fade.setter
    def fade(self, x): self.setFade(x)

class PVMult(PyoPVObject):
    """
    Multiply magnitudes from two phase vocoder streaming object.

    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process. Frequencies from
            this pv stream are used to compute the output signal.
        input2 : PyoPVObject
            Phase vocoder streaming object which gives the second set of
            magnitudes. Frequencies from this pv stream are not used.

    .. note::
        
        The two input pv stream must have the same size and overlaps. It is
        the responsibility of the user to be sure they are consistent. To change
        the size (or the overlaps) of the phase vocoder process, one must
        write a function to change both at the same time (see the example below).
        Another possibility is to use channel expansion to analyse both sounds
        with the same PVAnal object.

    >>> s = Server().boot()
    >>> s.start()
    >>> sf = FM(carrier=[100,150], ratio=[.999,.5005], index=20, mul=.4)
    >>> sf2 = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.5)
    >>> pva = PVAnal(sf)
    >>> pva2 = PVAnal(sf2)
    >>> pvc = PVMult(pva, pva2)
    >>> pvs = PVSynth(pvc).out()
    >>> def size(x):
    ...     pva.size = x
    ...     pva2.size = x
    >>> def olaps(x):
    ...     pva.overlaps = x
    ...     pva2.overlaps = x

    """
    def __init__(self, input, input2):
        PyoPVObject.__init__(self)
        self._input = input
        self._input2 = input2
        input, input2, lmax = convertArgsToLists(self._input, self._input2)
        self._base_objs = [PVMult_base(wrap(input,i), wrap(input2,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setInput2(self, x):
        """
        Replace the `input2` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input2 = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput2(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def input2(self):
        """PyoPVObject. Second set of magnitudes.""" 
        return self._input2
    @input2.setter
    def input2(self, x): self.setInput2(x)

class PVMorph(PyoPVObject):
    """
    Performs spectral morphing between two phase vocoder streaming object.
    
    According to `fade` argument, the amplitudes from `input` and `input2` 
    are interpolated linearly while the frequencies are interpolated
    exponentially.

    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object which gives the first set of
            magnitudes and frequencies.
        input2 : PyoPVObject
            Phase vocoder streaming object which gives the second set of
            magnitudes and frequencies.
        fade : float or PyoObject, optional
            Scaling factor for the output amplitudes and frequencies, 
            between 0 and 1. 0 is `input` and 1 in `input2`. Defaults to 0.5.

    .. note::
        
        The two input pv stream must have the same size and overlaps. It is
        the responsibility of the user to be sure they are consistent. To change
        the size (or the overlaps) of the phase vocoder process, one must
        write a function to change both at the same time (see the example below).
        Another possibility is to use channel expansion to analyse both sounds
        with the same PVAnal object.

    >>> s = Server().boot()
    >>> s.start()
    >>> sf = SineLoop(freq=[100,101], feedback=0.12, mul=.5)
    >>> sf2 = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.5)
    >>> pva = PVAnal(sf)
    >>> pva2 = PVAnal(sf2)
    >>> pvc = PVMorph(pva, pva2, fade=0.5)
    >>> pvs = PVSynth(pvc).out()
    >>> def size(x):
    ...     pva.size = x
    ...     pva2.size = x
    >>> def olaps(x):
    ...     pva.overlaps = x
    ...     pva2.overlaps = x

    """
    def __init__(self, input, input2, fade=0.5):
        PyoPVObject.__init__(self)
        self._input = input
        self._input2 = input2
        self._fade = fade
        input, input2, fade, lmax = convertArgsToLists(self._input, self._input2, fade)
        self._base_objs = [PVMorph_base(wrap(input,i), wrap(input2,i), wrap(fade,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setInput2(self, x):
        """
        Replace the `input2` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input2 = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput2(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setFade(self, x):
        """
        Replace the `fade` attribute.
        
        :Args:

            x : int
                new `fade` attribute.
        
        """
        self._fade = x
        x, lmax = convertArgsToLists(x)
        [obj.setFade(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0, 1, "lin", "fade", self._fade)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. First input signal.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def input2(self):
        """PyoPVObject. Second input signal.""" 
        return self._input2
    @input2.setter
    def input2(self, x): self.setInput2(x)

    @property
    def fade(self):
        """float or PyoObject. Scaling factor."""
        return self._fade
    @fade.setter
    def fade(self, x): self.setFade(x)

class PVFilter(PyoPVObject):
    """
    Spectral filter.
    
    PVFilter filters frequency components of a pv stream
    according to the shape drawn in the table given in
    argument.
    
    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process.
        table : PyoTableObject
            Table containing the filter shape. If the 
            table length is smaller than fftsize/2,
            remaining bins will be set to 0.
        gain : float or PyoObject, optional
            Gain of the filter applied to the input spectrum. 
            Defaults to 1.

    >>> s = Server().boot()
    >>> s.start()
    >>> t = ExpTable([(0,1),(61,1),(71,0),(131,1),(171,0),(511,0)], size=512)
    >>> src = Noise(.4)
    >>> pva = PVAnal(src, size=1024)
    >>> pvf = PVFilter(pva, t)
    >>> pvs = PVSynth(pvf).out()

    """
    def __init__(self, input, table, gain=1):
        PyoPVObject.__init__(self)
        self._input = input
        self._table = table
        self._gain = gain
        input, table, gain, lmax = convertArgsToLists(self._input, table, gain)
        self._base_objs = [PVFilter_base(wrap(input,i), wrap(table,i), wrap(gain,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setTable(self, x):
        """
        Replace the `table` attribute.
        
        :Args:

            x : PyoTableObject
                new `table` attribute.
        
        """
        self._table = x
        x, lmax = convertArgsToLists(x)
        [obj.setTable(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setGain(self, x):
        """
        Replace the `gain` attribute.
        
        :Args:

            x : int
                new `gain` attribute.
        
        """
        self._gain = x
        x, lmax = convertArgsToLists(x)
        [obj.setGain(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0, 1, "lin", "gain", self._gain)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def table(self):
        """PyoTableObject. Table containing the filter shape.""" 
        return self._table
    @table.setter
    def table(self, x): self.setTable(x)

    @property
    def gain(self):
        """float or PyoObject. Gain of the filter."""
        return self._gain
    @gain.setter
    def gain(self, x): self.setGain(x)

class PVDelay(PyoPVObject):
    """
    Spectral delays.
    
    PVDelay applies different delay times and feedbacks for
    each bin of a phase vocoder analysis. Delay times and 
    feedbacks are specified with PyoTableObjects.
    
    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process.
        deltable : PyoTableObject
            Table containing delay times, as integer multipliers
            of the FFT hopsize (fftsize / overlaps). 
            
            If the table length is smaller than fftsize/2,
            remaining bins will be set to 0.
        feedtable : PyoTableObject
            Table containing feedback values, between -1 and 1. 
            
            If the table length is smaller than fftsize/2,
            remaining bins will be set to 0.
        maxdelay : float, optional
            Maximum delay time in seconds. Available at initialization 
            time only. Defaults to 1.0.

    >>> s = Server().boot()
    >>> s.start()
    >>> SIZE = 1024
    >>> SIZE2 = SIZE / 2
    >>> OLAPS = 4
    >>> MAXDEL = 2.0 # two seconds delay memories
    >>> FRAMES = int(MAXDEL * s.getSamplingRate() / (SIZE / OLAPS))
    >>> # Edit tables with the graph() method. yrange=(0, FRAMES) for delays table
    >>> dt = DataTable(size=SIZE2, init=[i / float(SIZE2) * FRAMES for i in range(SIZE2)])
    >>> ft = DataTable(size=SIZE2, init=[0.5]*SIZE2)
    >>> src = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=0.5)
    >>> pva = PVAnal(src, size=SIZE, overlaps=OLAPS)
    >>> pvd = PVDelay(pva, dt, ft, maxdelay=MAXDEL)
    >>> pvs = PVSynth(pvd).out()

    """
    def __init__(self, input, deltable, feedtable, maxdelay=1.0):
        PyoPVObject.__init__(self)
        self._input = input
        self._deltable = deltable
        self._feedtable = feedtable
        self._maxdelay = maxdelay
        input, deltable, feedtable, maxdelay, lmax = convertArgsToLists(self._input, deltable, feedtable, maxdelay)
        self._base_objs = [PVDelay_base(wrap(input,i), wrap(deltable,i), wrap(feedtable,i), wrap(maxdelay,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setDeltable(self, x):
        """
        Replace the `deltable` attribute.
        
        :Args:

            x : PyoTableObject
                new `deltable` attribute.
        
        """
        self._deltable = x
        x, lmax = convertArgsToLists(x)
        [obj.setDeltable(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setFeedtable(self, x):
        """
        Replace the `feedtable` attribute.
        
        :Args:

            x : PyoTableObject
                new `feedtable` attribute.
        
        """
        self._feedtable = x
        x, lmax = convertArgsToLists(x)
        [obj.setFeedtable(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def deltable(self):
        """PyoTableObject. Table containing the delay times.""" 
        return self._deltable
    @deltable.setter
    def deltable(self, x): self.setDeltable(x)

    @property
    def feedtable(self):
        """PyoTableObject. Table containing feedback values."""
        return self._feedtable
    @feedtable.setter
    def feedtable(self, x): self.setFeedtable(x)

class PVBuffer(PyoPVObject):
    """
    Phase vocoder buffer and playback with transposition.
    
    PVBuffer keeps `length` seconds of pv analysis in memory
    and gives control on playback position and transposition.
    
    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process.
        index : PyoObject
            Playback position, as audio stream, normalized 
            between 0 and 1. 
        pitch : float or PyoObject, optional
            Transposition factor. Defaults to 1.
        length : float, optional
            Memory length in seconds. Available at initialization 
            time only. Defaults to 1.0.

    .. note::
        
        The play() method can be called to start a new recording of 
        the current pv input.

    >>> s = Server().boot()
    >>> s.start()
    >>> f = SNDS_PATH+'/transparent.aif'
    >>> f_len = sndinfo(f)[1]
    >>> src = SfPlayer(f, mul=0.5)
    >>> index = Phasor(freq=1.0/f_len*0.25, phase=0.9)
    >>> pva = PVAnal(src, size=1024, overlaps=8)
    >>> pvb = PVBuffer(pva, index, pitch=1.25, length=f_len)
    >>> pvs = PVSynth(pvb).out()

    """
    def __init__(self, input, index, pitch=1.0, length=1.0):
        PyoPVObject.__init__(self)
        self._input = input
        self._index = index
        self._pitch = pitch
        self._length = length
        input, index, pitch, length, lmax = convertArgsToLists(self._input, index, pitch, length)
        self._base_objs = [PVBuffer_base(wrap(input,i), wrap(index,i), wrap(pitch,i), wrap(length,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setIndex(self, x):
        """
        Replace the `index` attribute.
        
        :Args:

            x : PyoObject
                new `index` attribute.
        
        """
        self._index = x
        x, lmax = convertArgsToLists(x)
        [obj.setIndex(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setPitch(self, x):
        """
        Replace the `pitch` attribute.
        
        :Args:

            x : float or PyoObject
                new `pitch` attribute.
        
        """
        self._pitch = x
        x, lmax = convertArgsToLists(x)
        [obj.setPitch(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0.25, 4, "lin", "pitch", self._pitch)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def index(self):
        """PyoObject. Reader's normalized position.""" 
        return self._index
    @index.setter
    def index(self, x): self.setIndex(x)

    @property
    def pitch(self):
        """float or PyoObject. Transposition factor."""
        return self._pitch
    @pitch.setter
    def pitch(self, x): self.setPitch(x)

class PVShift(PyoPVObject):
    """
    Spectral domain frequency shifter.
    
    PVShift linearly moves the analysis bins by the amount, in Hertz,
    specified by the the `shift` argument. 
    
    :Parent: :py:class:`PyoPVObject`
    
    :Args:
    
        input : PyoPVObject
            Phase vocoder streaming object to process.
        shift : float or PyoObject, optional
            Frequency shift factor. Defaults to 0.

    >>> s = Server().boot()
    >>> s.start()
    >>> sf = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.7)
    >>> pva = PVAnal(sf, size=1024)
    >>> pvt = PVShift(pva, shift=500)
    >>> pvs = PVSynth(pvt).out()

    """
    def __init__(self, input, shift=0):
        PyoPVObject.__init__(self)
        self._input = input
        self._shift = shift
        input, shift, lmax = convertArgsToLists(self._input, shift)
        self._base_objs = [PVShift_base(wrap(input,i), wrap(shift,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setShift(self, x):
        """
        Replace the `shift` attribute.
        
        :Args:

            x : int
                new `shift` attribute.
        
        """
        self._shift = x
        x, lmax = convertArgsToLists(x)
        [obj.setShift(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(-5000, 5000, "lin", "shift", self._shift)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def shift(self):
        """float or PyoObject. Frequency shift factor."""
        return self._shift
    @shift.setter
    def shift(self, x): self.setShift(x)

class PVAmpMod(PyoPVObject):
    """
    Performs frequency independent amplitude modulations.
    
    PVAmpMod modulates the magnitude of each bin of a pv 
    stream with an independent oscillator. `basefreq` and 
    `spread` are used to derive the frequency of each 
    modulating oscillator.
    
    Internally, the following operations are applied to
    derive oscillator frequencies (`i` is the bin number):
        
        spread = spread * 0.001 + 1.0

        f_i = basefreq * pow(spread, i)

    :Parent: :py:class:`PyoPVObject`

    :Args:

        input : PyoPVObject
            Phase vocoder streaming object to process.
        basefreq : float or PyoObject, optional
            Base modulation frequency, in Hertz. 
            Defaults to 1.
        spread : float or PyoObject, optional
            Spreading factor for oscillator frequencies, between
            -1 and 1. 0 means every oscillator has the same frequency.

    >>> s = Server().boot()
    >>> s.start()
    >>> src = PinkNoise(.3)
    >>> pva = PVAnal(src, size=1024, overlaps=4)
    >>> pvm = PVAmpMod(pva, basefreq=4, spread=0.5)
    >>> pvs = PVSynth(pvm).out()

    """
    def __init__(self, input, basefreq=1, spread=0):
        PyoPVObject.__init__(self)
        self._input = input
        self._basefreq = basefreq
        self._spread = spread
        input, basefreq, spread, lmax = convertArgsToLists(self._input, basefreq, spread)
        self._base_objs = [PVAmpMod_base(wrap(input,i), wrap(basefreq,i), wrap(spread,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setBasefreq(self, x):
        """
        Replace the `basefreq` attribute.
        
        :Args:

            x : int
                new `basefreq` attribute.
        
        """
        self._basefreq = x
        x, lmax = convertArgsToLists(x)
        [obj.setBasefreq(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setSpread(self, x):
        """
        Replace the `spread` attribute.
        
        :Args:

            x : int
                new `spread` attribute.
        
        """
        self._spread = x
        x, lmax = convertArgsToLists(x)
        [obj.setSpread(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def reset(self):
        """
        Resets modulation pointers to 0.

        """
        [obj.reset() for obj in self._base_objs]
        
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0.1, 20, "log", "basefreq", self._basefreq),
                          SLMap(-1, 1, "lin", "spread", self._spread)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def basefreq(self):
        """float or PyoObject. Modulator's base frequency."""
        return self._basefreq
    @basefreq.setter
    def basefreq(self, x): self.setBasefreq(x)
    
    @property
    def spread(self):
        """float or PyoObject. Modulator's frequency spreading factor."""
        return self._spread
    @spread.setter
    def spread(self, x): self.setSpread(x)

class PVFreqMod(PyoPVObject):
    """
    Performs frequency independent frequency modulations.
    
    PVFreqMod modulates the frequency of each bin of a pv 
    stream with an independent oscillator. `basefreq` and 
    `spread` are used to derive the frequency of each 
    modulating oscillator.
    
    Internally, the following operations are applied to
    derive oscillator frequencies (`i` is the bin number):
        
        spread = spread * 0.001 + 1.0

        f_i = basefreq * pow(spread, i)

    :Parent: :py:class:`PyoPVObject`

    :Args:

        input : PyoPVObject
            Phase vocoder streaming object to process.
        basefreq : float or PyoObject, optional
            Base modulation frequency, in Hertz. 
            Defaults to 1.
        spread : float or PyoObject, optional
            Spreading factor for oscillator frequencies, between
            -1 and 1. 0 means every oscillator has the same frequency.
        depth : float or PyoObject, optional
            Amplitude of the modulating oscillators, between 0 and 1. 
            Defaults to 0.1.

    >>> s = Server().boot()
    >>> s.start()
    >>> src = SfPlayer(SNDS_PATH+"/accord.aif", loop=True, mul=0.5)
    >>> pva = PVAnal(src, size=1024, overlaps=4)
    >>> pvm = PVFreqMod(pva, basefreq=8, spread=0.75, depth=0.05)
    >>> pvs = PVSynth(pvm).out()

    """
    def __init__(self, input, basefreq=1, spread=0, depth=0.1):
        PyoPVObject.__init__(self)
        self._input = input
        self._basefreq = basefreq
        self._spread = spread
        self._depth = depth
        input, basefreq, spread, depth, lmax = convertArgsToLists(self._input, basefreq, spread, depth)
        self._base_objs = [PVFreqMod_base(wrap(input,i), wrap(basefreq,i), wrap(spread,i), wrap(depth,i)) for i in range(lmax)]
 
    def setInput(self, x):
        """
        Replace the `input` attribute.
        
        :Args:

            x : PyoObject
                New signal to process.

        """
        self._input = x
        x, lmax = convertArgsToLists(x)
        [obj.setInput(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setBasefreq(self, x):
        """
        Replace the `basefreq` attribute.
        
        :Args:

            x : int
                new `basefreq` attribute.
        
        """
        self._basefreq = x
        x, lmax = convertArgsToLists(x)
        [obj.setBasefreq(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setSpread(self, x):
        """
        Replace the `spread` attribute.
        
        :Args:

            x : int
                new `spread` attribute.
        
        """
        self._spread = x
        x, lmax = convertArgsToLists(x)
        [obj.setSpread(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setDepth(self, x):
        """
        Replace the `depth` attribute.
        
        :Args:

            x : int
                new `depth` attribute.
        
        """
        self._depth = x
        x, lmax = convertArgsToLists(x)
        [obj.setDepth(wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def reset(self):
        """
        Resets modulation pointers to 0.

        """
        [obj.reset() for obj in self._base_objs]
        
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0.1, 20, "log", "basefreq", self._basefreq),
                          SLMap(-1, 1, "lin", "spread", self._spread),
                          SLMap(0, 1, "lin", "depth", self._depth)]
        PyoPVObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoPVObject. Input signal to process.""" 
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def basefreq(self):
        """float or PyoObject. Modulator's base frequency."""
        return self._basefreq
    @basefreq.setter
    def basefreq(self, x): self.setBasefreq(x)
    
    @property
    def spread(self):
        """float or PyoObject. Modulator's frequencies spreading factor."""
        return self._spread
    @spread.setter
    def spread(self, x): self.setSpread(x)

    @property
    def depth(self):
        """float or PyoObject. Amplitude of the modulators."""
        return self._depth
    @depth.setter
    def depth(self, x): self.setDepth(x)