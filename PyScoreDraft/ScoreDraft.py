import os
ScoreDraftPath= os.path.dirname(__file__)

if os.name == 'nt':
	os.environ["PATH"]+=";"+ScoreDraftPath
elif os.name == "posix":
	os.environ["PATH"]+=":"+ScoreDraftPath

import PyScoreDraft
import types 

from PyScoreDraft import TellDuration
'''
TellDuration(seq) takes in a single input "seq"
It can be a note-sequence, a beat-sequence, or a singing-sequence, 
anything acceptable by Instrument.play(), Percussion.play(), Singer.sing()
as the "seq" parameter
The return value is the total duration of the sequence as an integer
'''

PyScoreDraft.ScanExtensions(ScoreDraftPath)

def ObjectToId(obj):
	'''
	Utility only used intenally. User don't use it.
	'''
	if type(obj) is list:
		return [ObjectToId(sub_obj) for sub_obj in obj]
	else:
		return obj.id

class TrackBuffer:
	'''
	Basic data structure storing waveform.
	The content can either be generated by "play" and "sing" calls or by mixing track-buffer into a new one
	'''
	def __init__ (self):
		self.id= PyScoreDraft.InitTrackBuffer()
	def __del__(self):
		PyScoreDraft.DelTrackBuffer(self.id)

	def setVolume(self,volume):
		'''
		Set the volume of the track. This value is used as a weight when mixing tracks.
		volume -- a float value
		'''
		PyScoreDraft.TrackBufferSetVolume(self.id, volume)

class Instrument:
	'''
	Structure to define an instrument object 
	An instrument object can be used to play note-sequences to a track-buffer object
	'''
	def __init__ (self, clsId):
		'''
		clsId -- an integer recognized by PyScoreDraft to indicate an instrument class.
		User don't know about clsIds, so don't initialize an instrument directly.
		Instead use one of the instrument intializer function generated by the "exec" below, 
		they are able to pass a proper clsId value to initialize an instance of Instrument.
		'''
		self.id=PyScoreDraft.InitInstrument(clsId)

	def __del__ (self):
		PyScoreDraft.DelInstrument(self.id)

	def tune(self, cmd):
		'''
		Sending a tuning command to an instrument.
		cmd -- A string to be parsed by the instrument.
		       Different instrument can support different sets of tuning commands.
		       A command common to all instruments is "volume", example: 
		       inst.tune("volume 0.5")
		'''
		PyScoreDraft.InstrumentTune(self.id, cmd)

	def play(self, buf, seq, tempo=80, refFreq=264.0):
		'''
		buf -- An instance of TrackBuffer, the result of play will be appended to the buffer.
		seq -- A list of notes [note1, note2, ... ]. Each of the notes is a tuple (freq, duration)
		       freq: a floating point frequency multiplier relative to a reference frequency "refFreq".
		             The physical frequency of the generated note is freq*refFreq in Hz.
		       duration: an integer that defines the duration of the note. 1 beat = 48, 1/2 beat =24 etc.

		       When "freq" is negative and "duration" is positive, a silent time period is defined, which 
		       occupies the "duration" but does not make any sound.
		       When "freq" is negative and "duration" is also negative, a "backspace" is generated. The 
		       cursor of note-sequence play will be brought backwards by "duration". In this way, the new 
		       notes can be overlapped with old ones, so that harmonies and chords can be generated.

		       Utility functions are provided in ScoreDraftNotes.py to simplify the computation of "freq".
		       For example "do(5,48)" will return a tuple with "freq" set to 1.0, which is "do" at octave "5".

		       Tuning commands can also be mixed in the list to tune the instrument on the fly, example:
		        [do(5,48),re(5,48), "volume 2.0", mi(5,48)... ]
		tempo -- an integer defining the tempo of play in beats/minute.
		refFreq  --  a floating point defining the reference-frequency in Hz.

		'''
		PyScoreDraft.InstrumentPlay(buf.id, self.id, seq, tempo, refFreq)


class Percussion:
	'''
	Structure to define an percussion object 
	An percussion object can be used to play beat-sequences to a track-buffer object
	'''
	def __init__(self, clsId):
		'''
		clsId -- an integer recognized by PyScoreDraft to indicate an percussion class.
		User don't know about clsIds, so don't initialize an percussion directly.
		Instead use one of the percussions intializer function generated by the "exec" below, 
		they are able to pass a proper clsId value to initialize an instance of Percussion.
		'''
		self.id=PyScoreDraft.InitPercussion(clsId)

	def __del__ (self):
		PyScoreDraft.DelPercussion(self.id)	

	def tune(self, cmd):
		'''
		Sending a tuning command to an percussion.
		cmd -- A string to be parsed by the percussion.
		       Different percussions can support different sets of tuning commands.
		       A command common to all percussions is "volume", example: 
		       perc.tune("volume 0.5")
		'''
		PyScoreDraft.PercussionTune(self.id, cmd)

	@staticmethod
	def play(percList, buf, seq, tempo=80):
		'''
		Typically, multiple percussions are used when playing a beat sequence, so here "play()" is defined as static.
		buf -- An instance of TrackBuffer, the result of play will be appended to the buffer.
		seq -- A list of beats [beat1, beat2, ... ]. Each of the beats is a tuple (index, duration)
		       index: a integer. When it is non-negative, it references a percussion in a percussion list, which is used to make the noise.
		       duration: the same as the "duration" of a note.

		       Negative "index" values are used in the same way as negative "freq" values of notes to define silent time periods and backspaces.

		       Tuning commands can also be mixed in the list to tune the percussions on the fly, example:
		         [(0,48), (1,48), (0,"volume 2.0"), (1,"volume 3.0"), (0,48), (1,48)... ]

		       In the beat sequence case, an index need to be provided to choose which persecussion the command is sent to.

		tempo -- an integer defining the tempo of play in beats/minute.		
		'''
		PyScoreDraft.PercussionPlay(buf.id, ObjectToId(percList), seq, tempo)

class Singer:
	'''
	Structure to define an singer object 
	An singer object can be used to sing singing-sequences to a track-buffer object
	'''
	def __init__(self, clsId):
		'''
		clsId -- an integer recognized by PyScoreDraft to indicate an singer class.
		User don't know about clsIds, so don't initialize an singer directly.
		Instead use one of the singer intializer function generated by the "exec" below, 
		they are able to pass a proper clsId value to initialize an instance of Singer.
		'''
		self.id=PyScoreDraft.InitSinger(clsId)

	def __del__ (self):
		PyScoreDraft.DelSinger(self.id)		

	def tune(self, cmd):
		'''
		Sending a tuning command to an singer.
		cmd -- A string to be parsed by the singer.
		       Different singers can support different sets of tuning commands.
		       A command common to all singers is "volume", example: 
		       singer.tune("volume 0.5")
		       Another command common to all singers is "default_lyric", example: 
		       singer.tune("default_lyric la")
		       This will make the singer to sing "la" when an empty lyric "" is recieved
		'''
		PyScoreDraft.SingerTune(self.id, cmd)

	def sing(self, buf, seq, tempo=80, refFreq=264.0):
		'''
		buf -- An instance of TrackBuffer, the result of play will be appended to the buffer.
		seq -- A list of singing-segments [seg1, seg2, ... ]. Each of the seg is a tuple 
					(lyric1, note1, note2, lyric2, note3, ...)
		       lyrics: they are strings, telling the singer what lyric to sing
		       notes: they are the same kind of notes used in instrument play. 

		       In many cases, there is only 1 note following a lyric.
		       When there are more than 1 notes follwoing a lyric, all these notes will split the duration of that lyric.
		       All lyrics and notes in the same tuple are intended to be sung continuously.
			   However, when there are silence notes/backapsaces, the singing-segment will be broken into multiple 
			   segments to sing.
		      
		       Raw notes can be mixed with singing-segments in the list. They will be sung using the default lyric.
		       Vice-versa, if you pass a singing-sequence to an instrument, the notes contained in the sequence will
		       get played, and lyrics ignored. We aim to provide maximum compatibility between the two.
		       Tuning commands can also be mixed in the list to tune the singer on the fly, example:
		        [("ha",do(5,48),re(5,48)), ("la",mi(5,48)), "volume 2.0", "default_lyric ba", fa(5,48)... ]

		       seq can also contain rapping segments like:
		       (lyric1, duration1, freq_start1, freq_end1, lyric2, duration2, freq_start2, freq_end2...)
		       freq_starts and freq_ends are used to define the tones syllables.
		       They are relative frequencies. The physical frequencies will be freq_starts*refFreq and freq_ends*refFreq

		tempo -- an integer defining the tempo of singing in beats/minute.
		refFreq  --  a floating point defining the reference-frequency in Hz.
		'''
		PyScoreDraft.Sing(buf.id, self.id, seq, tempo, refFreq)


def MixTrackBufferList (targetbuf, bufferList):
	'''
	Function used to mix a list of track-buffers into another one
	targetbuf -- an instance of TrackBuffer to contain the result
	bufferList -- a list a track-buffers
	'''
	PyScoreDraft.MixTrackBufferList(targetbuf.id, ObjectToId(bufferList))

def WriteTrackBufferToWav(buf, filename):
	'''
	Function used to write a track-buffer to a .wav file.
	buf -- an instance of TrackBuffer
	filename -- a string
	'''
	PyScoreDraft.WriteTrackBufferToWav(buf.id, filename)

def GetPCMDataFromTrackBuffer(buf):
	'''
	Function used to get raw PCM data from the TrackBuffer
	the return value is a list of floats
	'''
	return PyScoreDraft.GetPCMDataFromTrackBuffer(buf.id)

# generate dynamic code
g_generated_code_and_summary=PyScoreDraft.GenerateCode()
exec(g_generated_code_and_summary[0])

def PrintGeneratedCode():
	'''
	To see the detail of the code inserted by the above "exec"
	The generated code contains intializer functions of instruments, percussions and singers.
	It also includes extented interface functions defined by extensions.
	The content is dynamically changes when different extensions are deployed in the "Extensions" directory
	'''
	print (g_generated_code_and_summary[0])

def PrintGeneratedCodeSummary():
	'''
	To see a summary of the available initializers of instruments, percussions and singers, also names of interface functions.
	'''
	print (g_generated_code_and_summary[1])

class Document:
	'''
	An utility class to simplify user-side coding.
	The class maintains a list of track-buffers and some shared states (tempo and reference-frequency)
	'''
	def __init__ (self):
		self.bufferList=[]
		self.tempo=80
		self.refFreq=264.0

	def getBuffer(self, bufferIndex):
		return self.bufferList[bufferIndex]

	def getTempo(self):
		return self.tempo

	def setTempo(self,tempo):
		self.tempo=tempo

	def getReferenceFrequency(self):
		return self.refFreq

	def setReferenceFreqeuncy(self,refFreq):
		self.refFreq=refFreq

	def newBuf(self):
		'''
		The created track-buffer will be added to the track-buffer list of the document
		The index of the new track-buffer is returned
		'''
		buf=TrackBuffer()
		self.bufferList.append(buf)
		return len(self.bufferList)-1

	def setTrackVolume(self, bufferIndex, volume):
		self.bufferList[bufferIndex].setVolume(volume)

	def playNoteSeq(self, seq, instrument, bufferIndex=-1):
		'''
		Play a note sequence in the context of a document.
		instrument -- An instance of Instrument
		When bufferIndex==-1, a new track-buffer will be returned. Otherwise, an existing track-buffer will 
		be used and result is appended.
		The index of the target track-buffer is returned.
		'''
		if bufferIndex==-1:
			bufferIndex= self.newBuf()		
		buf=self.bufferList[bufferIndex]
		instrument.play(buf, seq, self.tempo, self.refFreq)
		return bufferIndex	

	def playBeatSeq(self, seq, percList, bufferIndex=-1):
		'''
		Play a beat sequence in the context of a document.
		When bufferIndex==-1, a new track-buffer will be returned. Otherwise, an existing track-buffer will 
		be used and result is appended.
		The index of the target track-buffer is returned.
		'''
		if bufferIndex==-1:
			bufferIndex= self.newBuf()		
		buf=self.bufferList[bufferIndex]			
		Percussion.play(percList, buf, seq, self.tempo)
		return bufferIndex

	def sing(self, seq, singer, bufferIndex=-1):
		'''
		Sing a sequence in the context of a document.
		When bufferIndex==-1, a new track-buffer will be returned. Otherwise, an existing track-buffer will 
		be used and result is appended.
		The index of the target track-buffer is returned.
		'''
		if bufferIndex==-1:
			bufferIndex= self.newBuf()		
		buf=self.bufferList[bufferIndex]
		singer.sing( buf, seq, self.tempo, self.refFreq)
		return bufferIndex

	def trackToWav(self, bufferIndex, filename):
		WriteTrackBufferToWav(self.bufferList[bufferIndex], filename)

	def mix(self, targetBuf):
		'''
		Mix the track-buffers in the document to a target buffer.
		targetBuf -- An instance of TrackBuffer
		'''
		MixTrackBufferList(targetBuf,self.bufferList)

	def mixDown(self,filename):
		'''
		Mix the track-buffers in the document to a temporary buffer and write to a .wav file.
		filename -- a string
		'''
		targetBuf=TrackBuffer()
		self.mix(targetBuf)
		WriteTrackBufferToWav(targetBuf, filename)

