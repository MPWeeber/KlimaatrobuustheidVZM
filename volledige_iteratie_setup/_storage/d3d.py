"""
Delft-3D Python Toolbox.
"""
import copy
import datetime
import itertools
import math
import os
import re
import shlex
import struct
import sys
import unittest
from collections import deque
from collections import OrderedDict
from operator import itemgetter

from abc import abstractmethod

try:
	import matplotlib.pyplot as plt
except ImportError:
	pass

try:
	import numpy as np
except ImportError:
	pass

DEBUG   = False
VERSION = "0.1dev"

# Use this as g = test_gen()
# print( next(g) )
# print( next(g) )
#
#
def test_gen():
	for i in range(10):
		yield i

def _log(message):
	if DEBUG: print(message)

#-------------------------------------------------------------------------------
# Files
#-------------------------------------------------------------------------------
class _File(object):
	"""
	Base class.

	f = _File("dir/subdir/root.ext)

	f.fullname  = "dir/subdir/root.ext"
	f.path      = "dir/subdir"
	f.name      = "root.ext"
	f.name_root = "root"
	f.name_ext  = "ext"
	"""

	def __init__(self, filename=None):
		self._fullname = filename
		self.path      = None
		self.name      = None
		self.name_root = None
		self.name_ext  = None
		if self.fullname is not None:
			self._fileinfo()

	@property
	def fullname(self):
		return self._fullname

	@fullname.setter
	def fullname(self, fullname):
		self.__init__(fullname)

	def _fileinfo(self):
		"""
		Set file info.
		"""
		if os.sep in self.fullname:
			s = self.fullname.split(os.sep)
			self.path = os.sep.join(s[:-1])
			self.name  = s[-1]
		else:
			self.path = "."
			self.name = self._fullname
		if '.' in self.name:
			s = self.name.split('.')
			self.name_root = '.'.join(s[:-1])
			self.name_ext  = s[ -1]
		else:
			self.name_root = self.name
			self.name_ext  = ''

	def dump(self, fileout=None):
		"""
		Dump file contents to csv.

		Only available if implemented in child classes.
		If filout is None, output file will be filename.dmp.
		"""
		raise NotImplementedError('This type of file cannot be dumped.')


class DelwaqComFile(_File):

	def __init__():
		pass


class DelwaqHDFile(_File):
	"""
	Delwaq hydrodynamic input file.

	*filename*	: Delwaq hydrodynamic file name
	*noseg*     : number of segments (e.g. for volumes, surface)
	*noq*       : number of exchanges (e.g. for flows, areas, velocs, ...)

	Exactly one of the two keyword arguments must be specified in order to
	interpret the file's data.
	"""
	def __init__(self, filename, noseg=None, noq=None):
		_File.__init__(self, filename)
		if noseg is None and noq is None:
			raise ValueError('Specify one of the "noseg" or "noq" arguments.')
		elif None not in (noseg, noq):
			raise ValueError('Specify only one of the "noseg" and "noq" arguments.')
		self._noseg  = noseg
		self._noq    = noq
		self._ntimes = None   # number of times
		self._dim    = None   # alias for self._noseg or self._noq
		self._f      = None   # iterator file pointer
		self._t      = None   # iterator time counter
		if filename is not None:
			self._scan()

	@property
	def ntimes(self):
		return self._ntimes

	@property
	def noseg(self):
		return self._noseg

	@property
	def noq(self):
		return self._noq

	def dimname(self):
		"""
		Tells if file has dimension "segment" or "exchange".

		Returns "segment" or "exchange".
		"""
		if self._noseg is None:
			return "exchange"
		else:
			return "segment"

	def _scan(self):
		"""
		Quick file scan during initialization to check and set file properties.
		"""
		with open(self.fullname, 'rb') as f:
			n = f.seek(0,2) / 4
		assert (int(n)) == n
		# number of times
		if self._noseg is None:
			self._dim = self._noq
		else:
			self._dim = self._noseg
		nt = n / (1 + self._dim)
		self._ntimes = int(nt)
		assert self.ntimes == nt

	def __str__(self):
		frmt = "<DelwaqHDFile {}, {} timesteps, {} {}s>"
		return frmt.format(self.name, self.ntimes, self._dim, self.dimname())

	def __iter__(self):
		if self._f is not None:
			self._f.close()
		self._f = open(self.fullname, 'rb')
		self._t = 1
		return self

	def __next__(self):
		if self._t > self.ntimes:
			self._f.close()
			raise StopIteration
		self._t += 1
		time = struct.unpack('i', self._f.read(4))[0]
		return time, np.array(struct.unpack('%if'%self._dim, self._f.read(self._dim*4)))

	def read(self):
		"""
		Return numpy array of file contents.
		"""
		# read data
		with open(self.fullname, 'rb') as f:
			data = f.read()
		# process data
		d = -np.ones((self._ntimes, self._dim), dtype=np.float)
		for itime in range(self._ntimes):
			offset = (self._dim + 1) * 4 * itime
			ibeg = offset + 4
			iend = offset + 4 + self._dim * 4
			d[itime, :] = struct.unpack('%if'%self._dim, data[ibeg:iend])
		return d

	def dump(self, fileout=None, transpose=False):
		"""
		Dump file contents to csv.

		*fileout*	: output file name. If None output is written to filein.dmp
		*transpose*	: time columns instead of time rows if True
		"""
		if fileout is None:
			fileout = self.fullname + '.dmp'
		d = self.read()
		row_hdr = 'time'
		col_hdr = self.dimname()
		if transpose:
			d = d.T
			row_hdr = col_hdr
			col_hdr = 'time'
		nrows, ncols = d.shape
		dimname = self.dimname()
		with open(fileout, 'w') as f:
			f.write("CSV dump of file: '%s'\n"%self.fullname) # TODO: absolute path
			f.write("Number of %s rows: %i\n"%(row_hdr, nrows))
			f.write("Number of %s columns: %i\n"%(col_hdr, ncols))
			f.write("%ss\\%ss;"%(row_hdr, col_hdr) + ';'.join([str(i+1) for i in range(ncols)]) + "\n")
			frmt = "{}" + ncols * ";{:e}" + "\n"
			for irow in range(nrows):
				f.write(frmt.format(irow+1, *d[irow, :]))

	def iter_times(self):
		with open(self.fullname, 'rb') as f:
			offset = self._dim *4
			for i in range(self._ntimes):
				yield struct.unpack('i', f.read(4))[0]
				f.seek(offset, 1)

	def iter_data(self, tbeg=0, tend=None):
		with open(self.fullname, 'rb') as f:
			offset = self._dim *4
			for i in range(self._ntimes):
				time = struct.unpack('i', f.read(4))[0]
				print(i, time)
				if time < tbeg:
					f.seek(offset, 1)
				elif time > tend:
					break
				else:
					print('yielding')
					yield time, np.array(struct.unpack('%if'%self._dim, f.read(self._dim*4)))


class DelwaqHisFile(_File):
	"""
	Delwaq history output file.

	To open a *.his file:

		>>> f = DelwaqHISFile("example.his")
		>>> print(f)
		<DelwaqHisFile 'example.his', 10 timesteps, 3 substances, 4 areas>

	Accessing data:

		>>> data =
	"""

	def __init__(self, filename):
		_File.__init__(self, filename)
		self._moname = None
		self._notot  = None
		self._nodump = None
		self._syname = None
		self._duname = None
		self.ntimes  = None # number of timesteps
		self._dim    = None # number of values per timestep (notot * nodump)
		self._datptr = None # pointer to start of data block in file
		if filename is not None:
			self._scan()

	def __str__(self):
		frmt = "<DelwaqHisFile '{}', {} timesteps, {} substances, {} areas>"
		return frmt.format(self.name, self.ntimes, self._notot, self._nodump)

	def _scan(self):
		with open(self.fullname, 'rb') as f:
			self._moname    = [f.read(40) for i in range(4)]
			self._notot     = struct.unpack('i', f.read(4))[0]
			self._nodump    = struct.unpack('i', f.read(4))[0]
			self._syname    = [f.read(20).decode().strip() for i in range(self._notot)]
			self._duname    = []
			self._duindx    = []
			for i in range(self._nodump):
				index = struct.unpack('i', f.read(4))[0]
				name  = f.read(20).decode().strip()
				self._duindx.append(index)
				self._duname.append(name)
			self._datptr = f.tell()
			data_block_size = f.seek(0, 2) - self._datptr
			self._dim = self._notot * self._nodump
			ntimes = data_block_size / ((self._dim + 1) * 4)
			assert int(ntimes) == ntimes
			self.ntimes = int(ntimes)


	def get(self, times=None, itimes=None, subs=None, areas=None):
		"""
		Return data in numpy array.

		*times*  : seconds since reference time T0
		*itimes* : time index (starting at 0)
		*subs*   : str or list of substance id's
		*areas*  : str or list of monitoring areas

		Specify eiter *times* or *itimes*.
		"""
		assert times is None or itimes is None # cannot specify both
		if times is not None:
			if isinstance(times, int):
				times = [times]
			nt = len(times)
		elif itimes is not None:
			if isinstance(itimes, int):
				itimes = [itimes]
			nt = len(itimes)
		else:
			nt = self.ntimes
		if subs is None:
			subs = self._syname
		if isinstance(subs, str):
			subs = [subs]
		isubs = [self._syname.index(sub) for sub in subs]
		if areas is None:
			areas = self._duname
		if isinstance(areas, str):
			areas = [areas]
		iareas = [self._duname.index(area) for area in areas]
		d = -9999 * np.ones( (nt, len(subs), len(areas)), dtype=np.float)
		with open(self.fullname, 'rb') as f:
			for it in range(nt):
				if times is not None:
					self._seek_time(f, time)
				else:
					f.seek(self._datptr + it*self._dim*4 + (it+1)*4 , 0)
				data = np.array(struct.unpack('%if'%self._dim, f.read(self._dim*4)))
				for _isub, isub in enumerate(isubs):
					for _iarea, iarea in enumerate(iareas):
						d[it, _isub, _iarea] = data[iarea*len(self._syname) + isub]
		return d



	def _seek_time(self, f, time):
		f.seek(self._datptr, 0)
		for i in range(self.ntimes):
			t = struct.unpack('i', f.read(4))[0]
			if t < time:
				f.seek(self._dim * 4, 1)
			elif t > time:
				raise RuntimeError('Could not find exact time match.')
			else:
				break


class DelwaqMapFile(_File):
	"""
	Delwaq history output file.
	"""

	def __init__(self, filename=None):
		_File.__init__(self, filename)
		self._moname = None
		self._notot  = None
		self._noseg  = None
		self._syname = None
		self.ntimes  = None # number of timesteps
		self._dim    = None # number of values per timestep (notot * noseg)
		self._datptr = None # pointer to start of data block in file
		if filename is not None:
			self._scan()

	def _scan(self):
		with open(self.fullname, 'rb') as f:
			self._moname    = [f.read(40) for i in range(4)]
			self._notot     = struct.unpack('i', f.read(4))[0]
			self._noseg     = struct.unpack('i', f.read(4))[0]
			self._syname    = [f.read(20) for i in range(self._notot)]
			self._datptr = f.tell()
			data_block_size = f.seek(0, 2) - self._datptr
			self._dim = self._notot * self._noseg
			ntimes = data_block_size / ((self._dim + 1) * 4)
			assert int(ntimes) == ntimes
			self.ntimes = int(ntimes)

	def get(self, time  : 'seconds since reference time T0',
	              subs  : 'str or list of substance names',
	              areas : 'str or list of monitoring areas'):
		""" Return data in numpy array. """
		with open(self.fullname, 'rb') as f:
			self._seek_time(f, time)

	def _seek_time(self, f, time):
		f.seek(self._datptr, 1)
		for i in range(self.ntimes):
			t = struct.unpack('i', f.read(4))[0]
			if t < time:
				f.read(self._dim * 4)
			elif t > time:
				raise RuntimeError('Could not find exact time match.')
			else:
				break

	def __str__(self):
		frmt = "<DelwaqMapFile '{}', {} timesteps, {} substances>"
		return frmt.format(self.name, self.ntimes, self._notot)


#-------------------------------------------------------------------------------
# Flow
#-------------------------------------------------------------------------------
class FlowRun(object):
	"""
	Represents a Flow run.

	fr = FlowRun('your_mdf_filename')
	"""

	def __init__(self, mdf=None):
		self.mdf = mdf # mdf filename
		if self.mdf is not None:
			self._load()

	def _load(self):
		"""
		Parse mdf file and load data.
		"""
		assert 0 # not implemented yet


#-------------------------------------------------------------------------------
# Delwaq
#-------------------------------------------------------------------------------
class DelwaqGrid(object):
	"""
	Delwaq grid processing (lga & cco files).
	"""
	def __init__(self, lga=None, cco=None):
		# files
		self._cco   = None # cco file
		self._lga   = None # cco file
		# lga & cco (make sure those are equal for in both files)
		self._mmax  = None # number of grid points in m direction
		self._nmax  = None # number of grid points in n direction
		self._nlay  = None # number of layers
		# lga specific
		self._nm    = None # number of active grid points
		self._noq1  = None # number of exchanges in first direction (horizontal)
		self._noq2  = None # number of exchanges in second direction (horizontal)
		self._noq3  = None # number of exchanges in third direction (vertical)
		self._segs  = None # segments numbers
		# cco specific
		self._x0    = None # x coordinate of origin
		self._y0    = None # y coordinate of origin
		self._coxs  = None # corner x coordinates
		self._coys  = None # corner y coordinates
		self._alpha = None # cco attribute always zero
		self._npart = None # cco attribute always zero
		# cco derived
		self._cexs  = None # center x coordinates
		self._ceys  = None # center y coordinates
		self._nocen = None # number of cell centers
		if lga is not None:
			self.lga = lga
		if cco is not None:
			self.cco = cco

	#---------------------------------------------------------------------------
	# grid properties
	#---------------------------------------------------------------------------
	@property
	def cco(self):
		return self._cco

	@cco.setter
	def cco(self, filename):
		self._cco = filename
		self._load_cco()

	@property
	def lga(self):
		return self._lga

	@lga.setter
	def lga(self, filename):
		self._lga = filename
		self._load_lga()

	@property
	def noseg(self):
		"""
		Number of active segments.
		"""
		if self.lga is None:
			raise ValueError("*.lga file required to determine number of active segments.")
		n = 0
		for i in self._segs:
			if i > 0: n +=1
		return n*self._nlay

	@property
	def info(self):
		"""
		return a description string
		"""
		s = ''
		s += 'cco : %s\n'%self._cco
		s += 'lga : %s\n'%self._lga
		s += 'mmax: %i\n'%self._mmax
		s += 'nmax: %i\n'%self._nmax
		s += 'nm  : %i\n'%self._nm
		s += 'nlay: %i\n'%self._nlay
		return s

	def __str__(self):
		if self.lga is None:
			return "<DelwaqGrid {}x{}x{} noseg= ?? (missing *.lga)>".format(self._mmax, self._nmax, self._nlay)
		else:
			return "<DelwaqGrid {}x{}x{} noseg={}>".format(self._mmax, self._nmax, self._nlay, self.noseg)

	#---------------------------------------------------------------------------
	# grid interface functions
	#---------------------------------------------------------------------------
	def xy2seg(self, xys):
		"""
		Get 2D segment number from coordinate(s).

		*xys*	: coordinates ((x,y), ...)

		The segment corresponding to coordinates is the one whose center is closest
		to given coordinates (i.e. not necessarily a segment containing the coordinates).
		"""
		# find indexes of closest centers
		cen_indexes = [self._closest_center(c[0], c[1]) for c in xys]
		# convert center indexes to lga indexes
		lga_indexes = self._centerindex_to_lgaindex(cen_indexes)
		# convert lga indexes to 2D segment numbers
		segs = [self._segs[i] for i in lga_indexes]
		return segs

	def seg2xy(self, segs, center=True):
		"""
		Convert xy coordinate to segment number.

		*segs*	: segment number
		*center*: if true, return coordinates of segment center (x, y)
				  if flase, return coordinates of segment corners as
				  ((x0, y0), (x1, y1), (x2, y2), (x3, y3))
					3---2
			  		|   |
			  		0---1
		"""
		segs = self.seg2d(segs)
		lga_index = [self._segs.index(seg) for seg in segs]
		cco_index = self._lgaindex_to_cco_index(lga_index)[0]
		x = (self._coxs[cco_index],
			 self._coxs[cco_index + self._nmax],
			 self._coxs[cco_index + self._nmax +1],
			 self._coxs[cco_index + 1])
		y = (self._coys[cco_index],
			 self._coys[cco_index + self._nmax],
		 	 self._coys[cco_index + self._nmax +1],
			 self._coys[cco_index + 1])
		xys = tuple(pair for pair in zip(x,y))
		if center:
			xys = (sum(x)/4, sum(y)/4)
		return xys

	def seg2d(self, segs):
		"""
		Convert 3D segment number(s) to 2D segment number(s).

		*segs*	: int or sequence | segment number(s)

		Segment numbers in top layer are returned unchanged.
		"""
		if isinstance(segs, int): segs = (segs,)
		return tuple(s % self._nm for s in segs)

	def seg3d(self, segs, lyrs):
		"""
		Convert 2D segment number(s) to 3D segment number(s).

		*segs*	: int or sequence | segment number(s) to convert
		*lyrs*	: int or sequence | corresponding layer numbers (1=surface, n=bottom)

		If *lyrs* is a single value, it is used for all *seg* values.
		"""
		if isinstance(segs, int): segs = (segs,)
		if isinstance(lyrs, int): lyrs = [lyrs for s in segs]
		assert len(segs) == len(lyrs)
		return tuple(segs[i] + (lyrs[i]-1) * self._nm for i in range(len(segs)) )

	#---------------------------------------------------------------------------
	# grid private functions
	#---------------------------------------------------------------------------
	def _load_cco(self):
		if self._cco is None:
			return
		_log("loading cco from file %s"%self._cco)
		with open(self._cco, 'rb') as f:
			# read attributes
			mmax        = struct.unpack('i', f.read(4))[0]
			nmax        = struct.unpack('i', f.read(4))[0]
			self._x0    = struct.unpack('f', f.read(4))[0]
			self._y0    = struct.unpack('f', f.read(4))[0]
			self._alpha = struct.unpack('f', f.read(4))[0] # always zero
			self._npart = struct.unpack('i', f.read(4))[0] # always zero
			nlay  = struct.unpack('i', f.read(4))[0]
			# make sure this cco matches the lga
			if self._lga is not None:
				assert self._mmax == mmax
				assert self._nmax == nmax
				assert self._nlay == nlay
			else:
				self._mmax = mmax
				self._nmax = nmax
				self._nlay = nlay
			# skip 9 zeros
			f.read(4*9)
			# read coords
			n = mmax * nmax
			self._coxs = struct.unpack('%if'%n, f.read(4 * n))
			self._coys = struct.unpack('%if'%n, f.read(4 * n))
		self._compute_centered_coordinates()

	def _load_lga(self):
		if self._lga is None:
			return
		_log("loading lga from file %s"%self._lga)
		with open(self._lga, 'rb') as f:
			# read attributes
			nmax       = struct.unpack('i', f.read(4))[0]
			mmax       = struct.unpack('i', f.read(4))[0]
			self._nm   = struct.unpack('i', f.read(4))[0]
			nlay       = struct.unpack('i', f.read(4))[0]
			self._noq1 = struct.unpack('i', f.read(4))[0]
			self._noq2 = struct.unpack('i', f.read(4))[0]
			self._noq3 = struct.unpack('i', f.read(4))[0]
			# make sure this lga matches the cco
			if self._cco is not None:
				assert self._mmax == mmax
				assert self._nmax == nmax
				assert self._nlay == nlay
			else:
				self._mmax = mmax
				self._nmax = nmax
				self._nlay = nlay
			# read segment numbers
			n = nmax * mmax
			self._segs = struct.unpack('%ii'%n, f.read(4*n))

	def _compute_centered_coordinates(self):
		"""
		Computes center coordinates from corner coordinates.
		"""
		_log("computing centered coordinates from cco")
		self._cexs = []
		self._ceys = []
		self._nocen = (self._mmax-2) * (self._nmax-2)
		for i in range(self._nocen):
			cor_index = self._centerindex_to_cornerindex(i)[0]
			self._cexs.append( sum((self._coxs[cor_index],
				                    self._coxs[cor_index + self._nmax],
				                    self._coxs[cor_index + self._nmax + 1],
				                    self._coxs[cor_index + 1])) / 4.0 )
			self._ceys.append( sum((self._coys[cor_index],
				                    self._coys[cor_index + self._nmax],
				                    self._coys[cor_index + self._nmax + 1],
				                    self._coys[cor_index + 1])) / 4.0 )
		assert self._nocen == len(self._cexs)
		self._cexs = tuple(self._cexs)
		self._ceys = tuple(self._ceys)

	def _centerindex_to_cornerindex(self, index):
		if isinstance(index, int):
			index = (index,)
		return tuple(i + i // (self._nmax-2) * 2 for i in index)

	def _centerindex_to_lgaindex(self, index):
		if isinstance(index, int):
			index = (index,)
		return tuple(i + i // (self._nmax-2) * 2 + self._nmax + 1 for i in index)

	def _lgaindex_to_cco_index(self, index):
		if isinstance(index, int):
			index = (index,)
		return tuple(i - self._nmax - 1 for i in index)

	def _closest_center(self, x, y):
		"""
		Returns index of center coordinates closest to given coordinates.
		"""
		return self._closest(self._cexs, self._ceys, x, y)

	def _closest_corner(self, x, y):
		"""
		Returns index of corner coordinates closest to given coordinates.
		"""
		return self._closest(self._coxs, self._coys, x, y)

	def _closest(self, xs, ys, x, y):
		"""
		Return i so that (xs[i], ys[i]) is closest to (xx, yy).
		"""
		n = len(xs)
		distances = [math.sqrt((x - xs[i]) * (x - xs[i]) + (y - ys[i]) * (y - ys[i])) for i in range(n)]
		return distances.index(min(distances))


class DelwaqRun(object):
	"""
	Represents a Delwaq run.


	dr = DelwaqRun('your_input_filename')
	"""

	def __init__(self, inp=None):
		self.inp = inp
		# block 1
		self.mxlnln_inp    = None # maximum line length in input file
		self.mxlnln_dia    = None # maximum line length in diagnostic file
		self.comment       = None # comment char
		self.version       = None # delwaq version string
		self.print_opt     = None # print output option
		self.title         = None # four model title strings
		self.masspm2       = None # True if 'MASS/M2' found in positions 34-40
		                          # of 3rd title string
		self.t0            = None # python datetime equivalent of t0 string
		self.systimer      = None # system timer in seconds
		self.nasub         = None # number of active substances
		self.npsub         = None # number of passive substances
		self.substances    = None # substance names
		# block 2
		self.timer_factor  = None # factor between system and process timers
		self.timer_strings = None # time format strings for system and processes
		self.int_opt       = None # integration option str
		self.int_subopt    = None # integration suboption str
		self.int_kwrds     = None # integration keywords
		self.mdp           = None # part mdp filename
		self.start_str     = None # integration starttime string
		self.stop_str      = None # integration stoptime string
		self.dt_option     = None # 0 for constant, 1 for time-varying
		self.dt_str        = None # time step string(s)
		self.mon_nareas    = None # number of monitoring points/areas
		self.mon_areas     = None # monitoring areas
		self.mon_ntrans    = None # number of monitoring transects
		self.mon_trans     = None # monitoring transects
		self.mon_timer     = None # output timer dict() for monitoring file
		self.his_timer     = None # output timer dict() for map file
		self.map_timer     = None # output timer dict() for history file
		# block 3
		self.noseg         = None # number of segments
		self.nolay         = None # number of layers
		self.multigrid     = None # boolean for use of multiple grids
		self.zmodel        = None # boolean for use of z-layers
		self.subgrids      = None
		self.bottomgrids   = None
		self.processgrids  = None

		# block 7
		self.constants     = None # OrderedDict
		self.parameters    = None # TODO
		self.functions     = None # TODO
		self.seg_functions = None # TODO



		# for convenience
		self.dt         = None # time step in seconds

		self.area       = None
		self.flow       = None
		self.length     = None
		self.surface    = None
		self.volume     = None
		self.flowdt     = None # seconds

		self.pointer_file  = None
		self.pointers      = None # np.array(noq, 4)

		self.bnd_list_file = None
		self.nobnd         = None
		self.bnd_types     = None
		self.bnd_itypes    = None
		self.bnd_iqs       = None


	@property
	def noq(self):
		if None in (self.noq1, self.noq2, self.noq3):
			print (self.noq1, self.noq2, self.noq3)
			raise RuntimeError('Calling noq property while noq1, noq2 and/or noq3 not set.')
		return self.noq1 + self.noq2 + self.noq3

	@staticmethod
	def valid_integration_kwrds():
		kwrds = OrderedDict({
		'NODISP-AT-NOFLOW':'todo: add info string',
		'DISP-AT-NOFLOW':'todo: add info string',
		'NODISP-AT-BOUND':'todo: add info string',
		'DISP-AT-BOUND':'todo: add info string',
		'LOWER-ORDER-AT-BOUND':'todo: add info string',
		'HIGHER-ORDER-AT-BOUND':'todo: add info string',
		'BALANCES-OLD-STYLE':'todo: add info string',
		'NO-BALANCES':'todo: add info string',
		'BALANCES-GPP-STYLE':'todo: add info string',
		'BALANCES-SOBEK-STYLE':'todo: add info string',
		'FORESTER':'todo: add info string',
		'NO-FORESTER':'todo: add info string',
		'ANTICREEP':'todo: add info string',
		'NO-ANTICREEP':'todo: add info string',
		'BAL_NOLUMPPROCESSES':'todo: add info string',
		'BAL_LUMPPROCESSES':'todo: add info string',
		'BAL_NOLUMPLOADS':'todo: add info string',
		'BAL_LUMPLOADS':'todo: add info string',
		'BAL_NOLUMPTRANSPORT':'todo: add info string',
		'BAL_LUMPTRANSPORT':'todo: add info string',
		'BAL_UNITAREA':'todo: add info string',
		'BAL_UNITVOLUME':'todo: add info string',
		'BAL_NOSUPPRESSSPACE':'todo: add info string',
		'BAL_SUPPRESSSPACE':'todo: add info string',
		'BAL_NOSUPPRESSTIME':'todo: add info string',
		'BAL_SUPPRESSTIME':'todo: add info string',
		'SCHEME15_UNSTRUCTURED':'todo: add info string',
		'SCHEME15_STRUCTURED':'todo: add info string',
		'ANTIDIFFUSION':'todo: add info string',
		'NO-ANTIDIFFUSION':'todo: add info string',
		'PARTICLE_TRACKING':'todo: add info string'})
		return kwrds


	#---------------------------------------------------------------------------
	# DelwaqRun Loaders
	#---------------------------------------------------------------------------
	def _load(self):
		"""
		Load data from input file.
		"""
		pass

	def _tokenize(self, content):
		"""
		Convert input file to tokens.

		Works only after setting self.comment.

		Puts parsed tokens into self._tokens deque object.
		"""
		lex = shlex.shlex(content)
		lex.commenters = self.comment
		lex.whitespace_split = True
		return list(lex)

	def _gettkn(self):
		""" Returns next token and deals with include statements. """
		token = self._tokens.popleft()
		if token == 'INCLUDE':
			filename = self._tokens.popleft()
			with open(filename, 'r') as f:
				content = f.read()
			q = deque(self._tokenize(content))
			q.extend(self._tokens)
			self._tokens = q
			token = self._gettkn()
		return token

	def _puttkn(self, token):
		""" Puts an unused token back in the token buffer. """
		self._tokens.appendleft(token)

	def _parse_inp(self):
		"""
		Parse input file.

		TODO: Call parse functions without arguments and have them fetch tokens
		      from the token queue directly. This way the number of tokens to be
		      fetched does not have to be determined in advance.
		      Modify unit tests so that they fill self._q before the calling the
		      tested parse funtions.

		"""
		assert self.inp is not None
		with open(self.inp, 'r') as f:
			# first 3 lines:
			# call f.readline directly instead of _gettkn because those lines
			# contain or start with a comment character.
			self._parse_0_first_line(f.readline())
			self._parse_0_delwaq_version(f.readline())
			self._parse_0_print_output_option(f.readline())
			content = f.read()
		self._tokens = deque()
		self._tokens.extend(self._tokenize(content))
		# block 1 --------------------------------------------------------------
		self._parse_1_title()
		self._parse_1_number_of_substances()
		self._parse_assert_block_end(1)
		# block 2 --------------------------------------------------------------
		self._parse_2_timer_settings()
		self._parse_2_integration()
		self._parse_2_integration_timers()
		self._parse_2_monitoring_locations()
		self._parse_2_output_timers
		self._parse_assert_block_end(2)
		# block 3 --------------------------------------------------------------
		self._parse_3_noseg()
		self._parse_3_multigrids()
		# block 7 --------------------------------------------------------------
		self._parse_7_process_steering()


		# clean up
		del self._tokens

	def _parse_0_first_line(self, line):
		"""
		Parse first line of input file.

		Sets:
		 - self.mxlnln_inp
		 - self.mxlnln_dia
		 - self.comment
		"""
		tokens = re.findall(r'\s*(\S+)\s*', line)
		assert len(tokens) == 3
		self.mxlnln_inp = int(tokens[0])
		self.mxlnln_dia = int(tokens[1])
		self.comment    = tokens[2][1:-1]

	def _parse_0_delwaq_version(self, line):
		"""
		Parse delwaq version line.

		Sets:
		 - self.version
		"""
		assert "DELWAQ_VERSION" in line
		self.version = re.findall('DELWAQ_VERSION_(\S+)\s+', line)[0]

	def _parse_0_print_output_option(self, line):
		"""
		Parse delwaq print output option line.

		Sets:
		 - self.print_opt
		"""
		assert "PRINT_OUTPUT_OPTION" in line
		self.print_opt = re.findall('PRINT_OUTPUT_OPTION_(\d)', line)[0]

	def _parse_1_title(self):
		"""
		Parse four title lines.

		Sets:
		 - self.title

		Calls:
		 - self._parse_1_masspm2
		 - self._parse_1_t0
		"""
		tokens = [self._tokens.popleft() for i in range(4)]
		# remove quotes
		tokens = [tok[1:-1] for tok in tokens]
		self.title = tokens
		self._parse_1_masspm2(tokens[2])
		self._parse_1_t0(tokens[3])

	def _parse_1_masspm2(self, line):
		"""
		Called by _parse_1_title

		Sets:
	     - masspm2
		"""
		self.masspm2 = False
		if len(line) == 40:
			self.masspm2 = line[33:] == "MASS/M2"

	def _parse_1_t0(self, line):
		"""
		Called by _parse_1_title

		Sets:
	     - self.t0
		"""
		if line[0:2] == 'T0' and len(line) == 40:
			self.t0_str = line
			r = r"T0: (\d{4})[.](\d\d)[.](\d\d) (\d\d):(\d\d):(\d\d)  \(scu=\s*(-?\d+)s\)"
			ints = [int(token) for token in re.findall(r, line)[0]]
			self.t0 = datetime.datetime(*ints[:-1])
			self.systimer = ints[-1]

	def _parse_1_number_of_substances(self):
		self.nasub = int(self._tokens.popleft())
		self.npsub = int(self._tokens.popleft())

	def _parse_1_subtances(self):
		"""
		Parse substance tokens.

		Sets:
		 - self.substances = list of substance names ordered by indexed and with
		                     appended names if multipliers are used (see section
		                     1.5.1 of the Delwaq Input File Manual)
		"""
		_subs = []
		for i in range(self.nasub + self.npsub):
			index = int(self._tokens.popleft())
			name  = self._tokens.popleft()
			if '*' in self._tokens[0]:
				multiplier = int(self._tokens.popleft()[1:])
			else:
				multiplier = None
			_subs.append((index, name, multiplier))
		# sort tuples on first element i.e. the substance index
		_subs = sorted(_subs,key=itemgetter(0))
		# make a tuple of substance names sorted by index
		subs = []
		for sub in _subs:
			if sub[2] is None:
				# no multiplier
				subs.append(sub[1])
			else:
				multiplier = sub[2]
				root       = sub[1]
				if    multiplier < 10 : frmt = "%02i"
				elif  multiplier < 100: frmt = "%02i"
				else                  : frmt = "%03i"
				subs.extend([root + frmt%i for i in range(1, multiplier+1)])
		self.substances = tuple(subs)

	def _parse_assert_block_end(self, iblock):
		"""
		Assert end of block *iblock* is reached.
		"""
		assert self._tokens.popleft() == "#%i"%iblock

	def _parse_2_timer_settings(self):
		"""
		Parse timer settings.

		Sets:
		 - self.timer_factor
		 - self.timer_strings
		"""
		self.timer_factor = int(self._tokens.popleft())
		self.timer_strings = tuple(self._tokens.popleft() for i in range(2))

	def _parse_2_integration(self):
		"""
		Parse integration information.

		Sets:
		 - self.int_opt
		 - self.int_subopt
		 - self.int_kwrds
		 - self.mdp
		"""
		self.int_opt, self.int_subopt = self._gettkn().split('.')
		self.int_kwrds  = []
		valid_kwrds = DelwaqRun.valid_integration_kwrds().keys()
		while(1):
			token = self._gettkn()
			if token == 'PARTICLE_TRACKING':
				self.mdp = self._gettkn()
			elif token in valid_kwrds:
				self.int_kwrds.append(token)
			else:
				self._puttkn(token)
				break

	def _parse_2_integration_timers(self):
		"""
		Parse integration timers.

		Sets:
		 - self.start_str
		 - self.stop_str
		 - self.timestep_opt
		 - self.timestep
		"""
		self.start_str = self._gettkn()
		self.stop_str  = self._gettkn()
		self.dt_option = int(self._gettkn())
		assert self.dt_option in (0, 1)
		if self.dt_option == 0:
			self.dt_str = self._gettkn()
		else:
			self.dt_str = []
			n = int(self._gettkn())
			for i in range(n):
				d, dt = self._gettkn(), self._gettkn()
				self.dt_str.append( (d, dt) )

	def _parse_2_monitoring_locations(self):
		"""
		Parse monitoring locations.

		Sets:
		self.mon_nareas
		self.mon_areas
		self.mon_ntrans
		self.mon_trans

		TODO: create monitoring locations from coordinates.
		"""
		# areas
		self.mon_nareas = int(self._gettkn())
		self.mon_areas = []
		for i in range(self.mon_nareas):
			area = {}
			area['name'] = self._gettkn()
			token = self._gettkn()
			if token == 'NO_BALANCE':
				area['balance'] = False
				n = int(self._gettkn())
			else:
				area['balance'] = True
				n = int(token)
			area['segments'] = tuple(int(self._gettkn()) for i in range(n))
			self.mon_areas.append( area )
		# transects
		self.mon_ntrans = int(self._gettkn())
		self.mon_trans = []
		for i in range(self.mon_ntrans):
			tran = {}
			tran['name'] = self._gettkn()
			tran['option'] = int(self._gettkn())
			n    = int(self._gettkn())
			tran['exchanges'] = tuple(int(self._gettkn()) for i in range(n))
			self.mon_trans.append( tran )

	def _parse_2_output_timers(self):
		"""
		Parse output timers.

		Sets:
		 - self.mon_timer
		 - self.his_timer
		 - self.map_timer
		"""
		self.mon_timer, self.his_timer, self.map_timer = {}, {}, {}
		for timer in (self.mon_timer, self.map_timer, self.his_timer):
			timer['start'] = self._gettkn()
			timer['stop']  = self._gettkn()
			timer['step']  = self._gettkn()

	def _parse_3_noseg(self):
		"""
		Parse number of segments.

		Sets:
		 - self.noseg
		"""
		self.noseg = int(self._tokens.popleft())

	def _parse_3_grid(self):
		"""
		Parse grid information.

		Sets:
		 - self.nolay
		 - self.zmodel
		 - self.multigrid
		"""
		self.zmodel = False
		self.multigrid = False
		while(1):
			token = self._tokens.popleft()
			if   token == 'NOLAY':
				self.nolay = int(self._tokens.popleft())
			elif token == 'ZMODEL':
				self.zmodel = True
			elif token == 'MULTIGRID':
				self.multigrid = True
				self._parse_3_multigrids()
			else:
				break

	def _parse_3_multigrid(self):
		"""
		Parse multigrid block.

		Sets:
		 - self.subgrids
		"""
		pass

	def _parse_7_process_steering(self):
		while(1):
			tok = self._gettkn().lower()
			if   tok == "constants"    : self._parse_7_constants()
			elif tok == "parameters"   : self._parse_7_parameters()
			elif tok == "functions"    : self._parse_7_functions()
			elif tok == "seg_functions": self._parse_7_segment_functions()
			elif tok == "#7":
				break
			else:
				raise ValueError("Unexpected keyword in block 7.")

	def _parse_7_constants(self):
		# read constant names
		names = []
		while(1):
			tok = self._gettkn()
			if tok.lower() == 'data':
				break
			names.append(tok[1:-1]) # discard quotes
		# read values
		values = []
		for i in range(len(names)):
			values.append(float(self._gettkn()))
		# store in self.constants
		if self.constants is None:
			self.constants = OrderedDict()
		for n,v in zip(names, values):
			self.constants[n] = v

	def _load_pointers(self):
		"""
		Read pointer file and load pointers into a (noq, 4) numpy array.
		"""
		p = np.zeros((self.noq, 4), dtype=np.int32)
		with open(self.pointer_file, 'r') as f:
			lines = f.readlines()
		lines = [line.strip() for line in lines]
		lines = [line for line in lines if line[0] != ';']
		assert len(lines) == self.noq
		for iq in range(self.noq):
			p[iq, :] = [int(i) for i in re.findall('-?\d+', lines[iq])]
		self.pointers = p

	def _load_boundary_list(self):
		"""
		Read boudanry list file and load into:
		   self.bnd_types : tuple of sorted unique boundary types
		   self.bnd_itypes: np array with index to self.bnd_types for each boundary
		   self.bnd_iqs   : np array with index to self.pointers for each boundary
		"""
		assert self.bnd_list_file is not None
		assert self.pointers is not None

		with open(self.bnd_list_file, 'r') as f:
			content = f.read()
		# boundary types
		all_types = re.findall("^\s*'\S+'\s+'\S+'\s+'(\S+)'\s*", content, re.MULTILINE)
		types = list(set(all_types))
		types.sort()
		self.bnd_types = tuple(types)
		self.nobnd     = len(all_types)
		# boundary type indexes
		type2index = {t:i for i, t in enumerate(types)}
		self.bnd_itypes = np.array([type2index[t] for t in all_types], dtype=np.int)
		# boundary exchange indexes
		mask    = np.logical_or(self.pointers[:, 0] < 0, self.pointers[:, 1] < 0)
		indexes = np.nonzero(mask)[0]
		self.bnd_iqs = np.array([indexes[i] for i in range(self.nobnd)], dtype=np.int)

	#---------------------------------------------------------------------------
	# DelwaqRun Masks
	#---------------------------------------------------------------------------
	def qmask(self, seg=None, fto=None, ext=None, bnd=None):
		"""
		Return a mask to self.pointers.

			*seg*     : int or list of ints
			            select pointers from or to segment nr. *seg*

			*fto*     : 'from' or 'to'
			            Select pointers from or to a segment if seg is specified.
			            Select pointers from or to all segment if seg is not
			            specified AND bnd is not False.
			            Otherwise, fto has no effect.

			*ext*     : - None  -> no effect (default)
			            - False -> only internal exchanges in case of multiple segments
			            - True  -> only external exchanges in case of multiple segments.

			*bnd*     : - True  -> only boundaries
			            - False -> no boundaries (only internal exchanges)
			            - str from self.bnd_types -> only boundaries of given type

		Forbidden combinations:
		    - fto                 : fto alone has no meaning
		    - fto & bnd=False     : this is equivalent to fto alone
		    - fto & ext=False     : idem
		    - fto & bnd=ext=False : idem

		Examples:
			qmask(seg=1, fto='to')
				-> all exchanges to segment 1

			qmask(seg=1, fto='from', bnd=False)
				-> all exchanges from segment 1 to other segments

			qmask(seg=1, fto='from', bnd=True)
				-> all exchanges from segment 1 to a boundary

			qmask(fto='to', bnd=true)
				-> all exchanges from a boundary to a segment

			qmask(seg=[1,2,3], fto='from')
				-> all exchanges from segment other than 1,2,3 to segments 1,2,3
		"""
		# segment filtering
		frmsk = np.ones((self.noq), dtype=np.int)
		tomsk = np.ones((self.noq), dtype=np.int)
		if isinstance(seg, int):
			seg = [seg]
		if seg is not None:
			frmsk = frmsk * 0
			tomsk = tomsk * 0
			for s in seg:
				assert (s > 0 and s <= self.noseg)
				frmsk = np.logical_or(frmsk, self.pointers[:, 0] == s)
				tomsk = np.logical_or(tomsk, self.pointers[:, 1] == s)
		# extfiltering
		if ext == False:
			# remove external fluxes
			assert (bnd != False) # Forbidden combination, see docstring
			intmsk = frmsk == tomsk
			frmsk = intmsk
			tomsk = intmsk
		elif ext == True:
			# remove internal flows
			intmsk = frmsk == tomsk
			frmsk[intmsk] = 0
			tomsk[intmsk] = 0
		segmsk = np.logical_or(frmsk, tomsk)
		# from/to filtering
		if fto is None:
			ftomsk = np.ones((self.noq), dtype=np.int)
		else:
			assert fto in ('from', 'to')
			assert (bnd != False or ext == True) # Forbidden combination, see docstring
			assert (ext != False) # Forbidden combination, see docstring
			if seg is not None:
				if fto == 'from':
					ftomsk = frmsk
				else:
					ftomsk = tomsk
			elif bnd is not None and bnd != False:
				if fto == 'from':
					ftomsk = self.pointers[:, 1] < 0
				else:
					ftomsk = self.pointers[:, 0] < 0
		# boundary filtering
		if bnd is None:
			bndmsk = np.ones((self.noq), dtype=np.int)
		else:
			assert (bnd in (self.bnd_types)) or bnd in (True, False)
			if bnd in self.bnd_types:
				itype   = self.bnd_types.index(bnd)
				bndiqs  = self.bnd_iqs[self.bnd_itypes == itype]
				bndmsk = np.zeros((self.noq), dtype=np.int)
				bndmsk[bndiqs] = 1
			elif bnd == True:
				bndmsk = np.logical_or(self.pointers[:, 0] < 0, self.pointers[:, 1] < 0)
			elif bnd == False:
				bndmsk = np.logical_and(self.pointers[:, 0] > 0, self.pointers[:, 1] > 0)
		# merge masks
		msk = np.logical_and(segmsk, ftomsk)
		msk = np.logical_and(msk   , bndmsk)
		return msk

	def qindx(self, seg=None, fto=None, bnd=None):
		"""
		Return pointer indexes corresponding to qamsk(...)
		"""
		return np.nonzero(qmask(seg=seg, fto=fto, bnd=bnd))[0]

	def smask(self, seg=None, bnd_type=None):
		"""
		Returns a segment mask.
		"""
		if isinstance(seg, int):
			seg = [seg]
		if seg is None:
			segmsk = np.ones((self.noseg), dtype=np.int)
		else:
			segmsk = np.zeros((self.noseg), dtype=np.int)
			for s in seg:
				segmsk[s] = 1
		if bnd_type is None:
			pass
		else:
			raise NotImplementedError('TODO')
		return segmsk

	def sindx(self, seg=None, fto=None, bnd=None):
		"""
		Return pointer indexes corresponding to qmask(...)
		"""
		assert 0 # not implemented yet

	#---------------------------------------------------------------------------
	# DelwaqRun Pointers
	#---------------------------------------------------------------------------
	def segment_pointers(self, seg):
		"""
		Returns direct exchange pointers relating to segment *seg*.
		"""
		assert seg > 0
		assert self.pointers is not None

		# direct exchanges (not n-1 or n+1)
		mask    = np.logical_or(self.pointers[:, 0] == seg, self.pointers[:, 1] == seg)
		indexes = np.nonzero(mask)[0]
		return [(i, self.pointers[i,0], self.pointers[i,1]) for i in indexes.tolist()]

	#---------------------------------------------------------------------------
	# DelwaqRun Readers
	#---------------------------------------------------------------------------
	def _read_flows(self):
		# read flow data
		with open(self.flow, 'rb') as f:
			_f = f.read()
		# number of times
		_ntimes = len(_f) / 4 / (1 + self.noq)
		ntimes = int(_ntimes)
		assert ntimes == _ntimes
		# init array
		f = -np.ones((ntimes, self.noq), dtype=np.float)
		# fill array
		for itime in range(ntimes):
			offset = (self.noq + 1) * 4 * itime
			ibeg = offset + 4
			iend = offset + 4 + self.noq * 4
			f[itime, :] = struct.unpack('%if'%self.noq, _f[ibeg:iend])
		return f

	def _read_volumes(self):
		# read volume data
		with open(self.volume, 'rb') as f:
			_v = f.read()
		# number of times
		_ntimes = len(_v) / 4 / (1 + self.noseg)
		ntimes = int(_ntimes)
		assert ntimes == _ntimes
		# init array
		v = -np.ones((ntimes, self.noseg), dtype=np.float)
		# fill array
		for itime in range(ntimes):
			offset = (self.noseg + 1) * 4 * itime
			ibeg = offset + 4
			iend = offset + 4 + self.noseg * 4
			v[itime, :] = struct.unpack('%if'%self.noseg, _v[ibeg:iend])
		return v

	#---------------------------------------------------------------------------
	# DelwaqRun Balances
	#---------------------------------------------------------------------------
	def hdbal():
		pass

	def _hdbal_gen(self, domain=None, lmpbnd=True, lmpint=True):
		"""
		Hydrodynamic balance generator.
		"""
		# input checks
		if domain is None:
			domain = [i+1 for i in irange(self.noseg)]
		elif isinstance(domain, int):
			domain = [domain]
		assert self.flow.ntimes == self.volume.ntimes
		# initialize generators
		storage  = self._hdbal_gen_storage(domain)
		internal = self._hdbal_gen_internal(domain, lmpint)
		boundary = self._hdbal_gen_boundary(domain, lmpbnd)
		# headers
		inthdr = self._hdbal_hdr_internal(domain, lmpint)
		bndhdr = self._hdbal_hdr_boundary(domain, lmpbnd)
		# counts
		nint = len(inthdr) * 2
		nbnd = len(bndhdr) * 2
		# time loop
		for t in range(1, self.flow.ntimes):
			vol, dvol = next(storage)
			intbal = next(internal).reshape(nint)
			bndbal = next(boundary).reshape(nbnd)
			bal = np.hstack((intbal, bndbal))
			err = dvol - bal.sum()
			yield np.hstack((err, vol, dvol, bal))

	def _hdbal_gen_storage(self, domain):
		""" Storage balance generator. """
		domain_volumes = np.zeros((self.volume.ntimes), dtype=np.float)
		segment_indexes = [segnr-1 for segnr in domain]
		for i, items in enumerate(self.volume):
			time, vols = items
			domain_volumes[i] = vols[segment_indexes].sum()
		# yield volume and dvol at each iteration
		for t in range(1,self.volume.ntimes):
			vol  = domain_volumes[t]                         # m3
			dvol = (vol - domain_volumes[t-1]) / self.flowdt # m3/s
			yield vol, dvol

	def _hdbal_gen_internal(self, domain, lump):
		"""
		Internal flows balance generator.

		*domain*  : list of segment numbers.
		*lump*    : lump flows if True
		"""
		msk_to_domain = self.qmask(seg=domain, fto='to'  , ext=True, bnd=False)
		msk_fr_domain = self.qmask(seg=domain, fto='from', ext=True, bnd=False)
		msk_frto      = np.logical_or(msk_to_domain, msk_fr_domain)
		# segment numbers from and to domain
		segs_frto = np.zeros((self.noq), dtype=np.int)
		segs_frto[msk_to_domain] = self.pointers[msk_to_domain, 0]
		segs_frto[msk_fr_domain] = self.pointers[msk_fr_domain, 1]
		# unique segment numbers corresponding to column headers of balance array
		segs = np.unique(segs_frto[segs_frto != 0])
		segs.sort()
		# balance post indexes
		idx = np.zeros((self.noq), dtype=np.int) + self.noq+1
		for i, seg in enumerate(segs):
			idx[segs_frto == seg] = np.where(segs == seg)
		# time loop skipping last timestep (flows of last timestep are not used
		# because the resulting volume at last t+1 is obviously unknown.)
		flow_file = copy.copy(self.flow)
		for t, data in enumerate(flow_file):
			time, flows = data
			if t > self.flow.ntimes-2:
				continue
			msk_pos = flows >= 0
			msk_neg = flows <  0
			msk_fr_domain_pos = np.logical_and(msk_fr_domain, msk_pos)
			msk_fr_domain_neg = np.logical_and(msk_fr_domain, msk_neg)
			msk_to_domain_pos = np.logical_and(msk_to_domain, msk_pos)
			msk_to_domain_neg = np.logical_and(msk_to_domain, msk_neg)
			q = np.zeros( (segs.shape[0], 2), dtype=np.float)
			if msk_to_domain_pos.any(): q[idx[msk_to_domain_pos], 0] += flows[msk_to_domain_pos] # in
			if msk_to_domain_neg.any(): q[idx[msk_to_domain_neg], 1] += flows[msk_to_domain_neg] # out
			if msk_fr_domain_neg.any(): q[idx[msk_fr_domain_neg], 0] -= flows[msk_fr_domain_neg] # in
			if msk_fr_domain_pos.any(): q[idx[msk_fr_domain_pos], 1] -= flows[msk_fr_domain_pos] # out
			if lump:
				q = q.sum(axis=0)
			yield q

	def _hdbal_hdr_internal(self, domain, lump):
		if lump:
			return ['Internal']
		msk_to_domain = self.qmask(seg=domain, fto='to'  , ext=True, bnd=False)
		msk_fr_domain = self.qmask(seg=domain, fto='from', ext=True, bnd=False)
		segs  = np.unique(np.hstack((self.pointers[msk_to_domain, 0], self.pointers[msk_fr_domain, 1])))
		segs.sort()
		return ["%i"%i for i in segs]

	def _hdbal_gen_boundary(self, domain, lump):
		"""
		Boundary flows balance generator.

		*domain*  : list of segment numbers.
		*lump*    : lump flows if True
		"""
		msk_to_domain = self.qmask(seg=domain, fto='to'  , bnd=True)
		msk_fr_domain = self.qmask(seg=domain, fto='from', bnd=True)
		msk_frto      = np.logical_or(msk_to_domain, msk_fr_domain)
		# boundary numbers from and to domain
		bnds_frto = np.zeros((self.noq), dtype=np.int)
		bnds_frto[msk_to_domain] = self.pointers[msk_to_domain, 0]
		bnds_frto[msk_fr_domain] = self.pointers[msk_fr_domain, 1]
		# unique boundary numbers corresponding to column headers of balance array
		bnds = np.unique(bnds_frto[bnds_frto != 0])
		bnds.sort()
		bnds = bnds[::-1]
		# balance post indexes
		idx = np.zeros((self.noq), dtype=np.int) + self.noq+1
		for i, bnd in enumerate(bnds):
			idx[bnds_frto == bnd] = np.where(bnds == bnd)
		# time loop skipping last timestep (flows of last timestep are not used
		# because the resulting volume at last t+1 is obviously unknown.)
		flow_file = copy.copy(self.flow)
		for t, data in enumerate(flow_file):
			time, flows = data
			if t > self.flow.ntimes-2:
				continue
			msk_pos = flows >= 0
			msk_neg = flows <  0
			msk_fr_domain_pos = np.logical_and(msk_fr_domain, msk_pos)
			msk_fr_domain_neg = np.logical_and(msk_fr_domain, msk_neg)
			msk_to_domain_pos = np.logical_and(msk_to_domain, msk_pos)
			msk_to_domain_neg = np.logical_and(msk_to_domain, msk_neg)
			q = np.zeros( (bnds.shape[0], 2), dtype=np.float)
			if msk_to_domain_pos.any(): q[idx[msk_to_domain_pos], 0] += flows[msk_to_domain_pos] # in
			if msk_to_domain_neg.any(): q[idx[msk_to_domain_neg], 1] += flows[msk_to_domain_neg] # out
			if msk_fr_domain_neg.any(): q[idx[msk_fr_domain_neg], 0] -= flows[msk_fr_domain_neg] # in
			if msk_fr_domain_pos.any(): q[idx[msk_fr_domain_pos], 1] -= flows[msk_fr_domain_pos] # out
			if lump:
				q = q.sum(axis=0)
			yield q

	def _hdbal_hdr_boundary(self, domain, lump):
		if lump:
			return ['Boundary']
		msk_to_domain = self.qmask(seg=domain, fto='to'  , bnd=True)
		msk_fr_domain = self.qmask(seg=domain, fto='from', bnd=True)
		bnds = np.unique(np.hstack((self.pointers[msk_to_domain, 0], self.pointers[msk_fr_domain, 1])))
		bnds.sort()
		bnds = bnds[::-1]
		return ["%i"%i for i in bnds]

	def print_hdbal(self, domain=None, lmpbnd=True, lmpint=True):
		"""
		Prints formatted water balance.

		See self.hdbal() for meaning of arguments.
		"""
		hdrs, b = self.hdbal(domain=domain, lmpbnd=lmpbnd, lmpint=lmpint)
		nrows, ncols = b.shape
		nexch = ncols-2
		# print column headers
		frmt  = "{:^12} |"
		frmt += "{:^12} |" * nexch
		frmt += "{:^12} | {:^12}"
		line = frmt.format('timestep', *hdrs)
		print('-'*len(line))
		print(line)
		print('-'*len(line))
		# print first data line
		frmt  = "{:>12} |{:^12} |{:< 1.5e} |{:^12} |"
		frmt += "{:< 1.5e} |" * (nexch-3)
		frmt += "{:< 1.5e} | {:< 1.5e}"
		line = frmt.format(0, '-', b[0, 1], '-', *b[0, 3:] )
		print(line)
		# print rest of data
		frmt  = "{:>12} |"
		frmt += "{:< 1.5e} |" * nexch
		frmt += "{:< 1.5e} | {:< 1.5e}"
		for irow in range(1,nrows):
			line = frmt.format(irow*self.flowdt, *b[irow, :])
			print(line)

	def dump_hdbal(self, outfile, domain=None, lmpint=True, lmpbnd=True):
		"""
		Prints formatted water balance.

		See self.hdbal() for meaning of arguments.
		"""
		if domain is None:
			domain = [i+1 for i in range(self.noseg)]
		elif isinstance(domain, int):
			domain = [domain]
		inthdr = self._hdbal_hdr_internal(domain, lmpint)
		bndhdr = self._hdbal_hdr_boundary(domain, lmpbnd)
		nint = len(inthdr) * 2
		nbnd = len(bndhdr) * 2
		hdr = 'timestep;err;vol;dvol'
		for h in self._hdbal_hdr_internal(domain, lmpint):
			hdr= hdr+ ';%s in;%s out'%(h,h)
		for h in self._hdbal_hdr_boundary(domain, lmpbnd):
			hdr= hdr+ ';%s in;%s out'%(h,h)
		gen = self._hdbal_gen(domain=domain, lmpint=lmpint, lmpbnd=lmpbnd)
		with open(outfile, 'w') as f:
			f.write(hdr)
			f.write('\n')
			for t, row in enumerate(gen):
				print("timestep: %i\r"%(t+1), end='')
				f.write("%i"%(t+1))
				frmt = ";{:e}" * row.shape[0]
				f.write(frmt.format(*row))
				f.write('\n')

	def hderr(self, segments=None, srtmax=False):
		"""
		Compute hydrodynamic continuity errors.

		*segments*	: list of segments or all if None
		*srtmax*    : if True, output sorted on maximum errors
		              if integer, first i segments with biggest errors
		"""
		# read data
		assert self.flow.ntimes == self.volume.ntimes
		ntimes = self.flow.ntimes
		print("reading flows"); print()
		f = self.flow.read()
		print("read volumes"); print()
		v = self.volume.read()
		if segments is None:
			segments = [i for i in range(1, self.noseg+1)]
		# init errs array
		errs = np.zeros( (ntimes, len(segments)), dtype=np.float )
		for iseg, seg in enumerate(segments):
			print('seg', seg)
			# get segment pointers
			sps = self.segment_pointers(seg)
			# init segment balance
			bal = np.zeros((ntimes, len(sps) + 1 + 1 + 1 + 1), dtype=np.float)
			# fill exchange flows
			for iptr, ptr in enumerate(sps):
				iq, from_seg, to_seg = ptr
				if to_seg == seg:
					bal[:, iptr] = f[:, iq]
				elif from_seg == seg:
					bal[:, iptr] = f[:, iq] * -1
				else:
					raise RuntimeError('Exchange pointer does not belong to segment!')
			# fill flow sum
			bal[:, -4] = bal[:,:-4].sum(axis=1)
			# fill volumes
			bal[:, -3] = v[:, iseg]
			# fill storage between t and t+1
			bal[:-1, -2] = v[1:, iseg]- v[0:-1, iseg]
			bal[ -1, -2] = np.nan
			bal[ : , -2] = bal[ : , -2] / self.flowdt
			# compute balance error (dvol - sum of flows) in m3/s
			bal[:, -1] = bal[:,-2] - bal[:, -4]
			# copy errors in errs array
			errs[:, iseg] = bal[:, -1]
			errs[-1, :]   = 0
		hdrs = segments
		if srtmax:
			maxes = errs.max(axis=0)
			mines = np.absolute(errs.min(axis=0))
			maxes = np.maximum(maxes, mines)
			srtmsk = np.argsort(maxes)
			srtmsk = srtmsk[::-1]
			errs = errs[:, srtmsk]
			hdrs = [hdrs[i] for i in srtmsk]
			if isinstance(srtmax, int):
				errs = errs[:, 0:srtmax]
				hdrs = hdrs[   0:srtmax]
		hdrs = ["seg %i"%seg for seg in hdrs]
		return hdrs, errs

	def dump_hderr(self, fileout, segments=None, srtmax=10):
		"""
		Write DelwaqRun.hderr to csv.
		"""
		hdrs, err = self.hderr(segments=segments, srtmax=srtmax)
		nrows, ncols = err.shape
		nexch = ncols-2
		with open(fileout, 'w') as f:
			# column headers
			frmt = "{}" + ncols * ";{}" + "\n"
			f.write(frmt.format('time', *hdrs))
			# data
			frmt = "{}" + ncols * ";{:e}" + "\n"
			for irow in range(nrows):
				# f.write(frmt.format(irow * self.flowdt, *b[irow, :]))
				f.write(frmt.format(irow * 1, *err[irow, :]))

	#---------------------------------------------------------------------------
	# DelwaqRun GUI functions
	#---------------------------------------------------------------------------
	def _gen_sub_file(self):
		"""Generate content of *.sub file"""
		raise NotImplementedError("TODO")

	def write_sub_file(self, filename):
		"""Write *.sub file for Delwaq GUI"""
		content = self._gen_sub()
		with open(filename, 'w') as f:
			f.write(content)

	def _gen_zero_file(self, config):
		"""
		Generate content of *.0 file.

		config: 'ECO' or 'WAQ'
		"""
		assert config in ['ECO', 'WAQ']
		raise NotImplementedError("TODO")


	def write_zero_file(self, filename):
		"""Write *.0 file for Delwaq GUI"""
		content = self._gen_sub()
		with open(filename, 'w') as f:
			f.write(content)


#-------------------------------------------------------------------------------
# Files
#-------------------------------------------------------------------------------
class _abstract_file(object):
	"""
	Parents class for file objects
	"""
	def __init__(self, filename):
		self._file = filename
		self._load()

	@property
	def file(self):
		return self._file

	@file.setter
	def file(self, filename):
		self._file = filename
		self._load()

	@abstractmethod
	def _load(self):
		"""
		Load meta data from file.
		"""
		if self._file is None:
			return
		self._loader() # this one must be implemented by inheriting classes


class kml(_abstract_file):
	"""
	Google Earth kml file.
	"""
	def __init__(self, filename=None):
		self.placemarks = [] # {'name': <name>, 'coordinates':(x,y,z)}
		self.paths      = [] # {'name': <name>, 'coordinates':[(x,y,z)]}
		_abstract_file.__init__(self, filename)

	def _loader(self):
		"""
		Load file.

		Currently, only reads placemark names and coordinates.
		"""
		_log('Loading kml file %s'%self._file)
		with open(self._file, 'r') as f:
			content = f.read()
		pat = '''
		<Placemark>.*?<name>(.*?)</name>.*?<coordinates>
		([^,]+),([^,]+),([^,]+)</coordinates>.*?</Placemark>
		'''
		for name,x,y,z in re.findall(pat, content, re.DOTALL|re.VERBOSE):
			self.placemarks.append({'name':name, 'coordinates':(float(x),float(y),float(z))})

	def write(self, filename):
		"""
		Write kml file
		"""
		with open(filename, 'w') as f:
			f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
			f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
			f.write('<Document>\n')
			for p in self.paths:
				f.write(self._render_path(p))
			f.write('</Document>\n')
			f.write('</kml>')

	def _render_path(self, path):
		r = ''
		r += ('<Placemark>\n')
		r += ('<name>%s</name>\n'%path['name'])
		r += ('\t<LineString>\n')
		r += ('\t\t<tessellate>1</tessellate>\n')
		r += ('\t\t<altitudeMode>clampToGround</altitudeMode>\n')
		r += ('\t\t<coordinates>\n')
		for c in path['coordinates']:
			r += ('\t\t%f,%f,%f\n'%(c[0], c[1], c[2]))
		r += ('\t\t</coordinates>\n')
		r += ('\t</LineString>\n')
		r += ('</Placemark>\n')
		return r

#-------------------------------------------------------------------------------
# Numpy
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# Coordinates
#-------------------------------------------------------------------------------
def rd2wgs(x, y):
	"""
    Convert RD New coordinates to WGS1984.

    Based on rd2wgs php code from http://www.god-object.com/2009/10/23/
        convert-rijksdriehoekscordinaten-to-latitudelongitude/
    """
	dX = (x - 155000) * math.pow(10, - 5)
	dY = (y - 463000) * math.pow(10, - 5)
	SomN = (3235.65389 * dY) + \
		(- 32.58297 * math.pow(dX, 2)) + \
		(- 0.2475   * math.pow(dY, 2)) + \
		(- 0.84978  * math.pow(dX, 2) * dY) + \
		(- 0.0655   * math.pow(dY, 3)) + \
		(- 0.01709  * math.pow(dX, 2) * math.pow(dY, 2)) + \
		(- 0.00738 * dX) + \
		(0.0053 * math.pow(dX, 4)) + \
		(- 0.00039 * pow(dX, 2) * math.pow(dY, 3)) + \
		(0.00033 * math.pow(dX, 4) * dY) + \
		(- 0.00012 * dX * dY)
	SomE = (5260.52916 * dX) + \
		(105.94684 * dX * dY) + \
		(2.45656 * dX * math.pow(dY, 2)) + \
		(- 0.81885 * math.pow(dX, 3)) + \
		(0.05594 * dX * math.pow(dY, 3)) + \
		(- 0.05607 * math.pow(dX, 3) * dY) + \
		(0.01199 * dY) + \
		(- 0.00256 * math.pow(dX, 3) * math.pow(dY, 2)) + \
		(0.00128 * dX * math.pow(dY, 4)) + \
		(0.00022 * math.pow(dY, 2)) + \
		(- 0.00022 * math.pow(dX, 2)) + \
		(0.00026 * math.pow(dX, 5));
	lat = 52.15517 + (SomN / 3600)
	lon = 5.387206 + (SomE / 3600)
	return (lon, lat)


#-------------------------------------------------------------------------------
# Ideas
#-------------------------------------------------------------------------------
class Monitoring(object):

	def __init__(self):
		raise NotImplementedError('')
		self.real_coordinates
		self.delwaq_coordinates
		self.delwaq_sements




################################################################################
#                                                                              #
#                                UNIT TESTS                                    #
#                                                                              #
################################################################################
def _np_arrays_equal(array_a, array_b):
	"""
	Return True if numpy arrays are equal.
	"""
	return np.all((array_a == array_b) | (np.isnan(array_a) & np.isnan(array_b)))

def _np_arrays_equal_rnd(array_a, array_b, dec=6):
	"""
	Return True if numpy arrays are equal up to the *dec* decimal.
	"""
	array_a = np.around(array_a, decimals=dec)
	array_b = np.around(array_b, decimals=dec)
	return np.all((array_a == array_b) | (np.isnan(array_a) & np.isnan(array_b)))

def mock_builtin_open(mock_dict):
	"""
	Replace builtin function open() with mocked object.

	*mock_dict*	: {file_name: file_content}
	"""
	class mock_open_class(object):

		def __init__(self, filename, mode):
			self.filename  = filename
			self.mode      = mode
			self.mock_dict = mock_dict
			self.data      = self.mock_dict[filename]
			self.pos       = 0

		def __enter__(self):
			return self

		def __exit__(self, type, value, traceback):
			pass

		def read(self, size=None):
			if size is None:
				prev_pos = self.pos
				self.pos = len(self.data)
				return self.data[prev_pos:]
			elif size > len(self.data) - self.pos:
				raise ValueError('Read size exceeds data size.')
			else:
				prev_pos  = self.pos
				self.pos += size
				return self.data[prev_pos:self.pos]

		def seek(self, offset, whence=0):
			"""
			Seek position in file.

			whence:
			 - 0 absolute position (default)
			 - 1 relative to current position
			 - 2 relative to end of file
			"""
			if   whence == 0:
				self.pos = offset
			elif whence == 1:
				self.pos += offset
			elif whence == 2:
				self.pos = len(self.data) - 1 - offset

		def close(self):
			pass

	__builtins__.__dict__['open'] = mock_open_class

def restore_builtin_open():
	""" Restore original builtin function open(). """
	__builtins__.__dict__['open'] = BUILTIN_FUNCTION_OPEN


class Test_File(unittest.TestCase):

	def setUp(self):
		self.f = _File()

	def test_fileinfo_current_dir(self):
		self.f.fullname = "filena.me"
		self.assertEqual(self.f.path, ".")

	def test_fileinfo_current_dir_no_ext(self):
		self.f.fullname = "filename"
		self.assertEqual(self.f.path, ".")

	def test_fileinfo_sub_dir(self):
		self.f.fullname = os.sep.join(["subdir", "filename"])
		self.assertEqual(self.f.path, "subdir")

	def test_fileinfo_subsub_dir(self):
		self.f.fullname = os.sep.join(["subdir", "subsubdir", "filename"])
		self.assertEqual(self.f.path, os.sep.join(["subdir", "subsubdir"]))

	def test_fileinfo_name(self):
		self.f.fullname = "filena.me"
		self.assertEqual(self.f.name, "filena.me")

	def test_fileinfo_ext(self):
		self.f.fullname = "filena.me"
		self.assertEqual(self.f.name_ext, "me")

	def test_fileinfo_ext_no_ext(self):
		self.f.fullname = "filename"
		self.assertEqual(self.f.name_ext, "")


class TestDelwaqRunParsing(unittest.TestCase):

	def setUp(self):
		self.dr = DelwaqRun()
		self.dr._tokens = deque()
		self.dr.comment = ';'

	def test_tokenize(self):
		test_line = "  test line with  'quoted tokens' and ; trailing comment\n"
		expected = ["test", "line", "with", "'quoted tokens'", "and"]
		com = self.dr._tokenize(test_line)
		self.assertEqual(com, expected)

	def test_tokenize_end_block(self):
		test_line = "#3 ; end of third block \n"
		expected = ["#3"]
		com = self.dr._tokenize(test_line)
		self.assertEqual(com, expected)

	def test_tokenize_point_between_words(self):
		test_line = "INCLUDE filename.ext\n"
		exp = ["INCLUDE", "filename.ext"]
		com = self.dr._tokenize(test_line)
		self.assertEqual(com, exp)

	def test_gettkn(self):
		self.dr._tokens = deque(['token1'])
		self.assertEqual(self.dr._gettkn(), 'token1')

	def test_gettkn_include_statement(self):
		mock_builtin_open({'input.inc':'token1\ntoken2  token3\n'})
		self.dr._tokens = deque(['INCLUDE', 'input.inc'])
		try:
			self.assertEqual(self.dr._gettkn(), 'token1')
			self.assertEqual(self.dr._tokens, deque(['token2', 'token3']))
		finally:
			restore_builtin_open()

	def test_gettkn_nested_include_statements(self):
		mock_builtin_open({'inp1.inc':'INCLUDE inp2.inc', 'inp2.inc':'tkn1 tkn2'})
		self.dr._tokens = deque(['INCLUDE', 'inp1.inc'])
		try:
			self.assertEqual(self.dr._gettkn(), 'tkn1')
			self.assertEqual(self.dr._tokens, deque(['tkn2']))
		finally:
			restore_builtin_open()

	def test_puttkn(self):
		self.dr._tokens = deque(['token2'])
		self.dr._puttkn('token1')
		self.assertEqual(self.dr._tokens[0], 'token1')

	def test_parse_0_first_line(self):
		test_line = "  512   80   ';'  \n"
		self.dr._parse_0_first_line(test_line)
		self.assertEqual(self.dr.mxlnln_inp, 512)
		self.assertEqual(self.dr.mxlnln_dia, 80)
		self.assertEqual(self.dr.comment, ';')

	def test_parse_0_delwaq_version(self):
		test_line = ";DELWAQ_VERSION_4.910   ; Delwaq version number"
		self.dr._parse_0_delwaq_version(test_line)
		self.assertEqual(self.dr.version, "4.910")

	def test_parse_0_print_output_option(self):
		test_line = ";PRINT_OUTPUT_OPTION_9  ; Debug level"
		self.dr._parse_0_print_output_option(test_line)
		self.assertEqual(self.dr.print_opt, "9")

	def test_parse_1_masspm2(self):
		test_line = 'Random comment string            MASS/M2'
		self.dr._parse_1_masspm2(test_line)
		self.assertTrue(self.dr.masspm2)

	def test_parse_1_t0(self):
		# common case
		test_line = 'T0: 2020.01.02 03:40:52  (scu=       1s)'
		self.dr._parse_1_t0(test_line)
		self.assertEqual(self.dr.t0, datetime.datetime(2020, 1, 2, 3, 40, 52))
		self.assertEqual(self.dr.systimer, 1)
		# negative system timer
		test_line = 'T0: 2020.01.02 03:40:52  (scu=      -5s)'
		self.dr._parse_1_t0(test_line)
		self.assertEqual(self.dr.systimer, -5)

	def test_parse_1_title(self):
		self.dr._tokens.extend([
			"'Water quality calculation'",
			"' '",
			"' '",
			"'T0: 2000.01.01 00:00:00  (scu=       1s)'"])
		expected = [
			'Water quality calculation',
			' ',
			' ',
			'T0: 2000.01.01 00:00:00  (scu=       1s)']
		self.dr._parse_1_title()
		self.assertEqual(self.dr.title, expected)

	def test_parse_1_number_of_substances(self):
		self.dr._tokens.extend(["3", "5"])
		self.dr._parse_1_number_of_substances()
		self.assertEqual(self.dr.nasub, 3)
		self.assertEqual(self.dr.npsub, 5)

	def test_parse_1_substances_no_multiplier(self):
		self.dr._tokens.extend( ["2", "sub2", "3", "sub3", "1", "sub1", "token"] )
		self.dr.nasub = 2
		self.dr.npsub = 1
		self.dr._parse_1_subtances()
		self.assertEqual(self.dr.substances, ("sub1","sub2","sub3"))

	def test_parse_1_substances_with_multiplier(self):
		self.dr._tokens.extend( ["2", "sub2", "*4", "3", "sub3", "1", "sub1", "token"] )
		self.dr.nasub = 2
		self.dr.npsub = 1
		expected = ("sub1","sub201","sub202","sub203","sub204","sub3")
		self.dr._parse_1_subtances()
		self.assertEqual(self.dr.substances, expected)

	def test_parse_assert_block_end(self):
		self.dr._tokens = deque(["#2", "token"])
		self.dr._parse_assert_block_end(2)
		self.assertEqual(self.dr._tokens, deque(["token"]))

	def test_parse_2_timer_settings(self):
		self.dr._tokens = deque(["86400", "sysformat", "procformat"])
		self.dr._parse_2_timer_settings()
		self.assertEqual(self.dr.timer_factor, 86400)
		self.assertEqual(self.dr.timer_strings, ("sysformat", "procformat") )

	def test_parse_2_integration(self):
		self.dr._tokens = deque(["15.73", "NO-FORESTER", "BAL_NOLUMPLOADS",
			"PARTICLE_TRACKING", "mdp_filename", "OTHER"])
		self.dr._parse_2_integration()
		self.assertEqual(self.dr.int_opt, '15')
		self.assertEqual(self.dr.int_subopt, '73')
		self.assertEqual(self.dr.int_kwrds, ["NO-FORESTER", "BAL_NOLUMPLOADS"])
		self.assertEqual(self.dr.mdp, "mdp_filename")
		self.assertEqual(self.dr._tokens, deque(['OTHER']))

	def test_parse_2_integration_timers_switch_0(self):
		self.dr._tokens = deque(["0123000", "25123000", "0", "0000500", "OTHER"])
		self.dr._parse_2_integration_timers()
		self.assertEqual(self.dr.start_str, "0123000")
		self.assertEqual(self.dr.stop_str, "25123000")
		self.assertEqual(self.dr.dt_option, 0)
		self.assertEqual(self.dr.dt_str, "0000500")
		self.assertEqual(self.dr._tokens, deque(['OTHER']))

	def test_parse_2_integration_timers_switch_1(self):
		self.dr._tokens = deque(["0123000", "25123000", "1", "2",
			"T1", "DT1", "T2", "DT2", "OTHER"])
		self.dr._parse_2_integration_timers()
		self.assertEqual(self.dr.start_str, "0123000")
		self.assertEqual(self.dr.stop_str, "25123000")
		self.assertEqual(self.dr.dt_option, 1)
		self.assertEqual(self.dr.dt_str, [("T1", "DT1"), ("T2", "DT2")])
		self.assertEqual(self.dr._tokens, deque(['OTHER']))

	def test_parse_2_monitoring_locations(self):
		self.dr._tokens = deque(["2", "Area1", "1", "124",
			"Area2", "NO_BALANCE", "3", "501", "502", "503",
			"1", "Trans1", "3", "2", "1", "5", "OTHER"])
		self.dr._parse_2_monitoring_locations()
		self.assertEqual(self.dr.mon_nareas, 2)
		self.assertEqual(self.dr.mon_areas, [
			{'name':"Area1", 'segments':tuple([124]), 'balance':True},
			{'name':"Area2", 'segments':tuple([501, 502, 503]), 'balance':False}])
		self.assertEqual(self.dr.mon_ntrans, 1)
		self.assertEqual(self.dr.mon_trans, [{'name':'Trans1',
			                                  'option':3,
			                                  'exchanges':tuple([1,5])}])
		self.assertEqual(self.dr._tokens, deque(['OTHER']))

	def test_parse_2_output_timers(self):
		self.dr._tokens = deque(['0121000','25121000','0100000',
								 '0122000','25122000','0200000',
								 '0123000','25123000','0300000'])
		self.dr._parse_2_output_timers()
		self.assertEqual(self.dr.mon_timer, {'start':'0121000',
			'stop':'25121000', 'step':'0100000'})
		self.assertEqual(self.dr.map_timer, {'start':'0122000',
			'stop':'25122000', 'step':'0200000'})
		self.assertEqual(self.dr.his_timer, {'start':'0123000',
			'stop':'25123000', 'step':'0300000'})

	def test_parse_3_noseg(self):
		self.dr._tokens = deque(["142673", "token"])
		self.dr._parse_3_noseg()
		self.assertEqual(self.dr.noseg, 142673)

	def test_parse_3_grid(self):
		pass

	def test_parse_7_constants_single(self):
		self.dr._tokens = deque(["'CST_A'", "DATA", "1.0"])
		self.dr._parse_7_constants()
		exp = OrderedDict()
		exp["CST_A"] = 1.0
		self.assertEqual(self.dr.constants, exp)

	def test_parse_7_constants_multi(self):
		self.dr._tokens = deque(["'CST_A'", "'CST_B'", "DATA", "1.0", "2.0"])
		self.dr._parse_7_constants()
		exp = OrderedDict()
		exp["CST_A"] = 1.0
		exp["CST_B"] = 2.0
		self.assertEqual(self.dr.constants, exp)


class TestDelwaqRunQMask(unittest.TestCase):

	def setUp(self):
		dm = DelwaqRun()
		dm.noseg = 2
		dm.noq1=3
		dm.noq2=0
		dm.noq3=0
		dm.pointers = np.array([[-1,  1, 0, 0],
			                    [ 1,  2, 0, 0],
			                    [ 2, -2, 0, 0]], dtype=np.int)
		dm.bnd_types = ('Inflow', 'Outflow')
		dm.bnd_itypes = np.array([0, 1], dtype=np.int)
		dm.bnd_iqs = np.array([0, 2], dtype=np.int)
		self.dm = dm

	def test_seg_value_asserts(self):
		self.assertRaises(AssertionError, self.dm.qmask, seg=-1)
		self.assertRaises(AssertionError, self.dm.qmask, seg=self.dm.noseg+1)

	def test_fto_value_asserts(self):
		self.assertRaises(AssertionError, self.dm.qmask, seg=1, fto='dummy')

	def test_bnd_value_asserts(self):
		self.assertRaises(AssertionError, self.dm.qmask, bnd='dummy')

	def test_combination_asserts(self):
		self.assertRaises(AssertionError, self.dm.qmask, seg=None, fto='from', bnd=False)
		self.assertRaises(AssertionError, self.dm.qmask, seg=1   , fto='from', bnd=False)
		self.assertRaises(AssertionError, self.dm.qmask, seg=None, fto='from', ext=False)
		self.assertRaises(AssertionError, self.dm.qmask, seg=1   , fto='from', ext=False)
		self.assertRaises(AssertionError, self.dm.qmask, seg=1   , fto='from', ext=False, bnd=False)

	def test_seg_int_filter(self):
		com = self.dm.qmask(seg=1)
		exp = np.array([1, 1, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_seg_list_filter(self):
		com = self.dm.qmask(seg=[1,2])
		exp = np.array([1, 1, 1])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_bnd_true_filter(self):
		com = self.dm.qmask(bnd=True)
		exp = np.array([1, 0, 1])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_bnd_false_filter(self):
		com = self.dm.qmask(bnd=False)
		exp = np.array([0, 1, 0])
		# print(com)
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_bnd_type_filter(self):
		com = self.dm.qmask(bnd='Outflow')
		exp = np.array([0, 0, 1])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_seg_fto_filter(self):
		com = self.dm.qmask(seg=1, fto='from')
		exp = np.array([0, 1, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_seg_bnd_filter(self):
		com = self.dm.qmask(seg=1, bnd=True)
		exp = np.array([1, 0, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )
		com = self.dm.qmask(seg=1, bnd=False)
		exp = np.array([0, 1, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_fto_bnd_filter(self):
		com = self.dm.qmask(fto='from', bnd=True)
		exp = np.array([0, 0, 1])
		self.assertTrue( _np_arrays_equal(com, exp) )
		com = self.dm.qmask(fto='to', bnd=True)
		exp = np.array([1, 0, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_seg_fto_bnd_filter(self):
		com = self.dm.qmask(seg=1, fto='from', bnd=True)
		exp = np.array([0, 0, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )
		com = self.dm.qmask(seg=1, fto='to', bnd=True)
		exp = np.array([1, 0, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_seg_ext_true(self):
		com = self.dm.qmask(seg=[1,2], ext=True)
		exp = np.array([1, 0, 1])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_seg_ext_false(self):
		com = self.dm.qmask(seg=[1,2], ext=False)
		exp = np.array([0, 1, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )

	def test_seg_fto_ext_bnd(self):
		com = self.dm.qmask(seg=1, fto='from', ext=True, bnd=False)
		exp = np.array([0, 1, 0])
		self.assertTrue( _np_arrays_equal(com, exp) )


class TestDelwaqRunSMask(unittest.TestCase):
	pass


class TestDelwaqRunHDBalance(unittest.TestCase):

	def setUp(self):
		"""
		Create a mock DelwaqRun.

		B1 ---> S1 ---> S2 ---> S4  ---> B3
		        ^         |      ^
		        |         |      |
		        B2        -----> S3

		B : boundary
		S : segment
		"""
		# mock DelwaqRun
		self.dr = DelwaqRun()
		self.dr.noseg = 4
		self.dr.noq1, self.dr.noq2, self.dr.noq3 = 7, 0, 0
		self.dr.flowdt = 10 # seconds
		self.dr.pointers = np.array([
			[-1,  1,  0,  0],
			[-2,  1,  0,  0],
			[ 1,  2,  0,  0],
			[ 2,  3,  0,  0],
			[ 2,  4,  0,  0],
			[ 3,  4,  0,  0],
			[ 4, -3,  0,  0]], dtype=np.int)
		self.dr.bnd_types  = ['Bnd_2', 'Bnd_3', 'Bnd_1']
		self.dr.bnd_itypes = np.array([2, 0, 1])
		self.dr.bnd_iqs    = np.array([0, 1, 8])
		# mock volume file
		self.dr.volume = DelwaqHDFile(None, noseg=4)
		self.dr.volume._fullname = "volume.dat"
		self.dr.volume._dim = 4
		self.dr.volume._ntimes = 3
		self.volume_values = [[  1.0, 1.0,  1.0, 1.0],
							  [151.0, 1.0,  1.0, 1.0],
							  [ 76.0, 1.0, 30.0, 1.0]]
		volume_bytes = bytes()
		for t, values in enumerate(self.volume_values):
			volume_bytes += struct.pack('i', t)
			volume_bytes += struct.pack('ffff', *values)
		# mock flow file
		self.dr.flow = DelwaqHDFile(None, noq=8)
		self.dr.flow._fullname = "flow.dat"
		self.dr.flow._dim = 7
		self.dr.flow._ntimes = 3
		self.flow_values = [[  1.0 , 2.0, 1.5, 0.6, 0.7,  0.6, 1.5],
							[ -0.25, 0.0, 0.5, 0.2, 0.3, -0.1, 0.2],
							[  1.0 , 1.0, 1.0, 0.5, 0.5,  1.0, 1.0]]
		flow_bytes = bytes()
		for t, values in enumerate(self.flow_values):
			flow_bytes += struct.pack('i', t)
			flow_bytes += struct.pack('fffffff', *values)
		# mock builtin function open
		mock_dict = {"volume.dat":volume_bytes, "flow.dat":flow_bytes}
		mock_builtin_open(mock_dict)

	def tearDown(self):
		restore_builtin_open()

	def test_gen_storage_single(self):
		domain = [1]
		gen = self.dr._hdbal_gen_storage(domain)
		for t, (vol, dvol) in enumerate(gen):
			t = t+1
			_vol  = self.volume_values[t][0]
			_dvol = (_vol - self.volume_values[t-1][0]) / self.dr.flowdt
			_vol, _dvol = np.float(_vol), np.float(_dvol)
			self.assertEqual(vol, _vol)
			self.assertEqual(dvol, _dvol)

	def test_gen_storage_multi(self):
		domain = [1,4]
		gen = self.dr._hdbal_gen_storage(domain)
		for t, (vol, dvol) in enumerate(gen):
			t = t+1
			_vol  = self.volume_values[t  ][0] + self.volume_values[t  ][3]
			_volb = self.volume_values[t-1][0] + self.volume_values[t-1][3]
			_vol, _volb = np.float(_vol), np.float(_volb)
			_dvol = (_vol - _volb) / self.dr.flowdt
			_dvol = np.float(_dvol)
			self.assertEqual(vol, _vol)
			self.assertEqual(dvol, _dvol)

	def test_gen_internal_single(self):
		domain = [1]
		lump   = False
		gen = self.dr._hdbal_gen_internal(domain, lump)
		self.assertTrue(
			_np_arrays_equal(next(gen), np.array([[0.0, -1.5]], dtype=np.float)))
		self.assertTrue(
			_np_arrays_equal(next(gen), np.array([[0.0, -0.5]], dtype=np.float)))
		self.assertRaises(StopIteration, next, gen)
		# test headers
		headers = self.dr._hdbal_hdr_internal(domain, lump)
		self.assertEqual(headers, ['2'])

	def test_gen_internal_single_lumped(self):
		domain = [1]
		lump   = True
		gen = self.dr._hdbal_gen_internal(domain, lump)
		self.assertTrue(
			_np_arrays_equal(next(gen), np.array([[0.0, -1.5]], dtype=np.float)))
		self.assertTrue(
			_np_arrays_equal(next(gen), np.array([[0.0, -0.5]], dtype=np.float)))
		self.assertRaises(StopIteration, next, gen)
		# test headers
		headers = self.dr._hdbal_hdr_internal(domain, lump)
		self.assertEqual(headers, ['Internal'])

	def test_gen_internal_multi(self):
		domain = [4,2]
		lump   = False
		gen = self.dr._hdbal_gen_internal(domain, lump)
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[1.5, 0.0], [0.6, -0.6]], dtype=np.float)))
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[0.5, 0.0], [0.0, -0.3]], dtype=np.float)))
		self.assertRaises(StopIteration, next, gen)
		# test headers
		headers = self.dr._hdbal_hdr_internal(domain, lump)
		self.assertEqual(headers, ['1', '3'])

	def test_gen_internal_multi_lumped(self):
		domain = [4,2]
		lump   = True
		gen = self.dr._hdbal_gen_internal(domain, lump)
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[2.1, -0.6]], dtype=np.float)))
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[0.5, -0.3]], dtype=np.float)))
		self.assertRaises(StopIteration, next, gen)
		# test headers
		headers = self.dr._hdbal_hdr_internal(domain, lump)
		self.assertEqual(headers, ['Internal'])

	def test_gen_boundary_single(self):
		domain = [1]
		lump   = False
		gen = self.dr._hdbal_gen_boundary(domain, lump)
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[1.0,  0.0 ], [2.0, 0.0]], dtype=np.float)))
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[0.0, -0.25], [0.0, 0.0]], dtype=np.float)))
		self.assertRaises(StopIteration, next, gen)
		# test headers
		headers = self.dr._hdbal_hdr_boundary(domain, lump)
		self.assertEqual(headers, ['-1', '-2'])

	def test_gen_boundary_single_lumped(self):
		domain = [1]
		lump   = True
		gen = self.dr._hdbal_gen_boundary(domain, lump)
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[3.0,  0.0 ]], dtype=np.float)))
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[0.0, -0.25]], dtype=np.float)))
		self.assertRaises(StopIteration, next, gen)
		# test headers
		headers = self.dr._hdbal_hdr_boundary(domain, lump)
		self.assertEqual(headers, ['Boundary'])

	def test_gen_boundary_multi(self):
		domain = [4,2,1]
		lump   = False
		gen = self.dr._hdbal_gen_boundary(domain, lump)
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[1.0,  0.0 ], [2.0, 0.0], [0.0, -1.5 ]], dtype=np.float)))
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[0.0, -0.25], [0.0, 0.0], [0.0, -0.2 ]], dtype=np.float)))
		self.assertRaises(StopIteration, next, gen)
		# test headers
		headers = self.dr._hdbal_hdr_boundary(domain, lump)
		self.assertEqual(headers, ['-1', '-2', '-3'])

	def test_gen_boundary_multi_lumped(self):
		domain = [4,2,1]
		lump   = True
		gen = self.dr._hdbal_gen_boundary(domain, lump)
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[3.0, -1.5 ]], dtype=np.float)))
		self.assertTrue(
			_np_arrays_equal_rnd(next(gen), np.array([[0.0, -0.45]], dtype=np.float)))
		self.assertRaises(StopIteration, next, gen)
		# test headers
		headers = self.dr._hdbal_hdr_boundary(domain, lump)
		self.assertEqual(headers, ['Boundary'])

	def test_gen_single(self):
		domain = [1]
		lump   = False
		gen = self.dr._hdbal_gen(domain=domain, lmpbnd=False, lmpint=False)
		exp = np.array([13.5 , 151.0, 15.0, 0.0, -1.5, 1.0,  0.0 , 2.0, 0.0], dtype=np.float)
		self.assertTrue(_np_arrays_equal_rnd(next(gen), exp))
		tmp = next(gen)
		exp = np.array([ -6.75,  76.0,  -7.5, 0.0, -0.5, 0.0, -0.25, 0.0, 0.0], dtype=np.float)
		self.assertTrue(_np_arrays_equal_rnd(tmp, exp))
		self.assertRaises(StopIteration, next, gen)


class TestDelwaqHDFile(unittest.TestCase):

	def setUp(self):
		# mock HDFile
		self.hdfile = DelwaqHDFile(None, noseg=2)
		self.hdfile._fullname = 'volume.dat'
		self.hdfile._dim    = 2
		self.hdfile._ntimes = 3
		self.times = [10, 20, 30]
		self.values = [[3.2,  1.4],
					   [2.8,  7.6],
					   [100, -1.2]]
		# mock builtin function open
		buff = bytes()
		for t, vals in enumerate(self.values):
			buff+= struct.pack('i', self.times[t])
			buff+= struct.pack('ff', *vals)
		mock_dict = {'volume.dat':buff}
		mock_builtin_open(mock_dict)

	def tearDown(self):
		restore_builtin_open()

	def test_read(self):
		com = self.hdfile.read()
		exp = np.array(self.values, dtype=np.float32)
		self.assertTrue(_np_arrays_equal(com, exp))

	def test_iter(self):
		for i, items in enumerate(self.hdfile):
			t, vals = items
			com = vals
			exp = np.array(self.values[i], dtype=np.float32)
			self.assertTrue(_np_arrays_equal(com, exp))
			self.assertEqual(t, self.times[i])

	def test_iter_times(self):
		gen = self.hdfile.iter_times()
		for i, t in enumerate(gen):
			self.assertEqual(t, self.times[i])


def _run_unittests():
	global BUILTIN_FUNCTION_OPEN
	BUILTIN_FUNCTION_OPEN = __builtins__.__dict__['open']
	restore_builtin_open()
	unittest.main()

if __name__ == '__main__':
	_run_unittests()

