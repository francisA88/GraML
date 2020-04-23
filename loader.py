from xml.etree.ElementTree import ElementTree as ET

from kivy.factory import Factory
from kivy.base import runTouchApp
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import *
from kivy.core.window import Window as window
from kivy.clock import Clock

import re
import sys
import os

class UnknownTagError(Exception):pass
class InvalidStartError(Exception):pass
class InvalidFileError(ValueError): pass

Builder.load_string('<Body@FloatLayout>:')
		
class Loader(object):
	def __init__(self, source:str, use_md=False): #set use_md to True to enable kivymd usage
		et = ET(file=source)
		if et.getroot().tag != "GraML":
			raise InvalidStartError("Missing tag 'GraML'")
		if os.path.splitext(source)[1] not in [".xml",".graml"]:
			raise InvalidFileError("Source file could be an invalid file type")
		self.loaded = False
		global space; space=self
		self.lroot = et.getroot()
		self.root = self.lroot.find("Body")
		self.shader = self.lroot.find("Shader")
		self.canvas = self.lroot.find("Canvas")
		self.pyscript = self.lroot.find("Script")
		if use_md:
			import kivymd
			from kivymd.app import MDApp as App
		self.body = self.retrieve_parent(self.root)
		#Try to get which one comes first, Script or Body?
		children = et.getroot().getchildren()
		k =[]
		maps = {
			"Script": self.executeScript,
			"Body": (lambda: self.handle_children(self.root, self.body))
		}
		bodytags = 0
		for ch in children:
			#k.append([ch,ch.tag])
			if bodytags ==2 and ch.tag =="Body":
				continue
			else: k.append([ch, ch.tag])
			bodytags+=1
		for i in k:
			if i[1] == "Script":
				#self.pyscript = i[0]
				maps[i[1]](i[0], i[0].text)
			elif i[1] == "Body":
				maps[i[1]]()
		
		#if there is no body, then there is no widget to which the shader is applied
		#if self.body != None:
		self.handle_shader()
		self.handle_canvas()
		
	def handle_children(self, parenttag, parent_wid):
		'''Method to add all children to the Body'''
		if self.body == None: return
		for child in parenttag.getchildren():
			wid_child = eval("Factory.%s"%child.tag)()
			
			opts = child.items()+self.get_opts_from_text(child.text if child.text!=None else "")
			for op in opts:
				if op[0].startswith("on_"):
					setattr(wid_child, op[0],eval(op[1]))
					continue
				try:
					setattr(wid_child, op[0], op[1])
				except ValueError:
					try:
						setattr(wid_child, op[0], eval(op[1]))
					except Exception as real_error:
						print("Invalid option attribute value in tag %s"%child.tag, file=sys.stderr)
			parent_wid.add_widget(wid_child)
			self.handle_children(child, wid_child)
			self.loaded = True
		
	def get_opts_from_text(self, text):
		options = re.findall("([a-zA-Z]+[0-9]*?):(.*?);", text, re.DOTALL)
		options = list(map(list, options))
		for i in range(len(options)):
			options[i][1] = options[i][1].lstrip().rstrip()
		options = list(map(tuple, options))
		return options
		
	def retrieve_parent(self, parenttag):
		'''Get a widget as parent from a single tag. Doesn't handle its children'''
		if parenttag ==None: return None
		parent = eval("Factory.%s"%parenttag.tag)()
		for opts in parenttag.items():
			try:
				setattr(parent, opts[0], opts[1])
			except ValueError:
				setattr(parent, opts[0], eval(opts[1]))
		return parent
		
	def handle_shader(self):
		if not self.shader: return
		if self.shader.text.replace(" ","") =="":
			return
		canv = RenderContext(
			use_parent_projection=True,
			use_parent_modelview=True)
		if self.body: self.body.canvas = canv
		else: window.canvas = canv
		self.vs = self.shader.find("Vertex")
		self.fs = self.shader.find("Fragment")
		if self.vs is not None:
			if self.vs.text.strip():
				canv.shader.vs = self.vs.text
			for opt in self.vs.items():
				if opt[0]=="src" or opt[0]=="source":
					try:
						canv.shader.vs = canv.shader.vs.join(open(opt[1]).read())
					except Exception as error:
						print(repr(error), file=sys.stderr)
		if self.fs is not None:
			if self.fs.text.strip():
				canv.shader.fs = self.fs.text
			for opt in self.fs.items():
				if opt[0]=="src" or opt[0]=="source":
					try:
						canv.shader.fs =canv.shader.fs.join(open(opt[1]).read())
					except Exception as error:
						print(repr(error), file=sys.stderr)
					
	def handle_canvas(self):
		#Handle the Canvas tag and instructions.
		'''Note: The XML or GraML file expects only one Canvas tag'''
		if not self.canvas: return
		for instruction in self.canvas.getchildren():
			klass = eval(instruction.tag)()
			text = instruction.text
			for opt in instruction.items()+self.get_opts_from_text(text if text!=None else ""):
				try:
					setattr(klass, opt[0], opt[1])
				except (ValueError, TypeError) as e:
					try:
						setattr(klass, opt[0], eval(opt[1]))
					except Exception as real_error:
						print("Invalid option attribute value in tag %s"%instruction.tag, file=sys.stderr)
			if self.body:
				self.body.canvas.add(klass)
			else:
				window.canvas.add(klass)
				
	def executeScript(self, sTag, script):
		for opt in sTag.items():
			if opt[0] in ["src", "source"]:
				exec(open(opt[1]).read())
		exec(script)
	
	def onBodyLoaded(self, callback):
		#Event listener for when all Body widgets are fully loaded
		def func(dt):
			while True:
				if self.loaded:
					callback()
					break
					ev.cancel()
		ev = Clock.schedule_once(func, .0001)
		
	def run(self):
		'''Use this method only if you do not wish to customize your subclass of App.'''
		class AppInstance(App):
			def build(other):
				return self.body
		AppInstance().run()

def defineAlias(name, type="Widget"):
	Builder.load_string("<{0}@{1}>:".format(name, type))
	
if __name__ == '__main__':
	loader = Loader("example.xml", 0)
	loader.run()