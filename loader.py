#GraML (Graphics Markup Language)
#version 0.1.
'''A markup language designed for making graphical user interfaces. It comes with features such a button, widgets, shaders (OpenGL), input, etc.
#Example:
==========
	<GraML>
		#$This is a comment
		<begin widgets>
			<button>
				text: "An example showcase";
			</button>
		<end widgets>
	</GraML>

This will produce a button with text "An example showcase" at the bottom left of the screen.'''

import kivy
import kivymd
from kivymd.theming import ThemeManager
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import *
import kivy.graphics as graphics
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.animation import Animation	
##print(dir(graphics))
from kivy.app import App
from kivy.lang import Builder
import re
import sys

load_config = lambda file:Builder.load_file(file)
#load_config("config.kv")
setInterval = lambda callback, interv: Clock.schedule_interval(callback, interv)
 
def capitalize(string):
	return string[0].upper()+string[1:]


class ParserError(SyntaxError): pass

class MainUI(Widget):
	def __init__(self, *args, **kws):
		super().__init__(*args, **kws)
		self.size = Window.size
		self.size_hint = None, None
		
class WidgetsParser(object):
	def __init__(self, gramlstring: str):
		self.gramlstring = gramlstring 
		self._parse()
		#self.singularTypes = ["Button", "Image", "Label", ""]

	def _parse(self):
		widbody = re.search("< *?begin *widgets *?>(.*?)< *end *widgets *?>", self.gramlstring, re.DOTALL)
		if widbody:
			self.widgetBody = widbody.group(1)
			all_widget_tags = re.findall("<.*?widget.+?>.+?<.*?/.*?widget.*?>", self.widgetBody, re.DOTALL)
			if all_widget_tags:
				for groups in all_widget_tags:
					self.parseWidgetTag(groups)
			otherTags = re.findall("<(.+)?>.*?</.+?>", widbody.group(1), re.DOTALL)
			for tag in otherTags:
				if not re.search("<.*?widget.+?>.+?<.*?/.*?widget.*?>", tag, re.DOTALL):
					body.add_widget(self.parseNonNested(tag))
						
	def parseNonNested(self, string):
		ptrn = "<(.+?)>(.*?)< *?/(.+?)>"
		match = re.search(ptrn, string, re.DOTALL)
		if match:
			split1 = match.group(2).split(";")
			split2 = [i.split(":") for i in split1]
			if split2[-1][0].replace(" ","").replace("\n","").replace("\t","") == "":
				split2.remove(split2[-1])
			for i in range(len(split2)):
				try:
					if "text" in split2[i][0]:
						split2[i][0] = "text"
						s = re.search(" *?'(.+?)' *", split2[i][1], re.DOTALL)
						if s:
							split2[i][1] = s.group(1)
					else:
						split2[i][0] = split2[i][0].replace(" ","").replace("\n","").replace("\t", "")
						split2[i][1] = split2[i][1].replace(" ","").replace("\n","").replace("\t", "")
						split2[i][1] = eval(split2[i][1])
				except:
					split2[i][1] = str(split2[i][1])
			attr = dict(split2)
			tag = capitalize(match.group(1).replace(" ","").replace("\n","").replace("\t",""))
			klass = eval("Factory."+tag)
			if tag == capitalize(match.group(3).replace(" ","").replace("\n","").replace("\t","")):
				return klass(**attr)
			else: return 0
			
	def parseWidgetTag(self, widgetTag):
		#I need the pattern to match whitespaces within tags too.					
		ptrn = "< *widget(.*?)>(.*?)< *?/ *widget *?>"
		ptrn2 = "<(.+?)>(.*?)< *?/(.+?)>"
		nesWidgetmatch = re.search(ptrn, widgetTag, re.DOTALL)
		options ={}
		if nesWidgetmatch:
			inline_attr = nesWidgetmatch.group(1)
			inline_attr = inline_attr.replace(" ","").replace("\n", "").replace("\t","").split(';')
			expandedInlineAttr = [i.split("=") for i in inline_attr]
			inlineOptions = dict(expandedInlineAttr)
			nestedTags = re.findall("<.+?>.*?< */.+?>", nesWidgetmatch.group(2), re.DOTALL)
			if nestedTags:
				explicitOptions = nesWidgetmatch.group(2)
				for i in nestedTags:
					explicitOptions = explicitOptions.replace(i, "")
				explicitOptions = explicitOptions.replace("\n","").replace(" ","").replace("\t","").split(";")
				if "" in explicitOptions:
					explicitOptions.remove("")
			else:
				explicitOptions = match.group(2).replace("\n","").replace(" ","").replace("\t","").split(";")
			opts = [i.split(":") for i in explicitOptions]
			for i in range(len(opts)):
				try:
					opts[i][1] = eval(opts[i][1])
				except:
					pass
			explicitOpts = dict(opts)
			options = inlineOptions
			options.update(explicitOpts)
			parwid = Widget(**options)
			if "id" in options:
				body.ids[options["id"]] = parwid
			for tags in nestedTags:
				m1=re.match(ptrn, tags, re.DOTALL)
				m2=re.match(ptrn2, tags, re.DOTALL)
				if (m1 and m2) or m1:
					self.parseWidgetTag(tags)
				elif m2 and not m1:
					child = self.parseNonNested(tags)
					if child:
						parwid.add_widget(child)
						try:
							parwid.ids[child.id] = child
						except AttributeError: pass
			body.add_widget(parwid)
			
##################################
class GraphicsParser(object):
	def __init__(self, gramlstring: str):
		self.graml = gramlstring
		self.parseGraphicsTree()
		
	def parseGraphicsTree(self):
		content = re.search("< *graphics(.*?)>(.*)< */ *graphics>", self.graml, re.DOTALL)
		if content:
			self.content = content.group(2)
			option = content.group(1).replace(" ","").split("=")
			if option[0] == "useShader" and eval(option[1]):
				body.canvas = RenderContext(
					use_parent_modelview = True,
					use_parent_projection = True
					)
				self.getShader(self.graml)
			else: body.canvas = Canvas()
			self.getColor()
			self.getOthers()
			
	def getColor(self):
		values = re.search("< *color(.+?)/>", self.graml, re.DOTALL)
		if values:
			values= values.group(1)
		color = (0,0,0,1)
		mode = "rgb"
		tokens = [i.split("=") for i in [i for i in values.split(";")]]
		tokens = dict(tokens)
		for attr in tokens:
			#Need to remove unwanted spaces to prevent errors or unwanted behaviours
			if attr.replace(" ", "") == "value":
				color = tokens[attr]
			if attr.replace(" ", "") == "mode":
				mode = tokens[attr]
		color = eval(color)
		body.canvas.add(Color(*color, mode=mode))
		#Remove the color tag from self.content
		self.content = re.search("< *color.*?/>(.*)", self.content, re.DOTALL)
		if self.content:
			self.content = self.content.group(1)
			
	def getOthers(self):
		'''Function to parse and add other graphics instructions like Line, Rectangle, Quad, etc.'''
		notUsed = ["Fbo", "RenderContext", "Canvas", "Callback", "GraphicException"]+[i for i in dir(graphics) if i.startswith("_") or i[0].islower()]
		#global here is not really necessary for the program to be successful, but was added here for users to be able to reference the available tags for use.
		global availableGraphicsTags
		#
		availableGraphicsTags = [i for i in dir(graphics) if i not in notUsed]
		if self.content:
			'''First get a list of tags accordingly as they are in the markup and then add them accordingly'''
			#I only need to find the beginning tags
			for group in re.findall("<.+?>.*?< */.+?>", self.content, re.DOTALL):
				match = re.search("<(.+?)>(.*?)<", group, re.DOTALL)
				if match:
					fullcontent = match.group().replace("\n","").replace(" ","")
					subContent = match.group(2)
					tag = match.group(1).replace(" ","")
					if capitalize(tag) in availableGraphicsTags:
						attrs = self.breakTokens(subContent)
						if "color" in attrs:
							body.canvas.add(Color(*attrs["color"]))
						Class = eval("%s"%capitalize(tag))
						ch = Class(**attrs)
						body.canvas.add(ch)
					
	def breakTokens(self, string) -> dict:
		'''Returns a dict of attributes and values within a particular tag'''
		tokens = string.split(";")
		for part in tokens:
			#I need to raise this error now to prevent further errors due to the tokens not being split properly
			if ":" not in part: raise ParserError
			parsed = [i.replace("\n","").replace("\t","").split(":") for i in tokens]
			#Well, for some reason I need this line.
			parsed.remove([""])
			output = dict(parsed)
			for prop in output: #property in output
				try:
					output[prop] = eval(output[prop])
				except NameError:
					output[prop] = str(output[prop])
				except:
					output[prop] = {}
			return output
		else: return {}
		
	def getShader(self, source: str) -> None:
		'''Gets and applies the canvas's shaders'''
		#Single out the fragment shader string
		print(source)
		fshaderTag = re.search("< *fshader(.*?)>(.*?)< *?/ *fshader *?>", source, re.DOTALL)
		print("here1: ", fshaderTag)
		if fshaderTag:
			options = fshaderTag.group(1)
			options = options.split(";")[0] if ";" in options else options.replace(" ","")
			parts = options.split("=")
			if parts[0] == "source":
				if str(parts[1]) == "string":
					fshaderString = fshaderTag.group(2)
					body.canvas.shader.fs =fshaderString
					#vertex shader   fragment shader
				else:
					fshaderString = open(parts[1]).read()
					body.canvas.shader.fs = fshaderString

def parseScript(source):
	fullContent = re.search("< *?GraML *?>(.+?)< *?/ *GraML.*?>", source, re.DOTALL)
	if fullContent:
		sc = fullContent.group(1)
		sc = re.search("< *script(.*?)>(.*?)< */ *script *?>", sc, re.DOTALL)
		if sc:
		#For almost every tag that i evaluate I must take into consideration spaces, tabs, and newlines to increase flexibility of the markup language.
			sourcelink = sc.group(1).replace("\t","").replace("\n","").replace(" ","")
			if sourcelink != "" and "=" not in sourcelink:
				raise ParserError("Invalid statement in script tag")
			if "=" in sourcelink:
				source_attr = sourcelink.split("=")[0]
				link = sourcelink.split("=")[1]
				if source_attr != "src": return
				if link != "":
					try:
						exec(open("".join(i for i in link if (i not in ("'", '"')))).read())
					except Exception as error:
						print(error, file=sys.stderr)
			script = sc.group(2)
			if script.replace(" ","").replace("\t","").replace("\n","") == "":
				return
			else:
				try:
					exec(script)
				except Exception as error:
					print(error, file=sys.stderr)
			
			
body = MainUI()
class Loader(object):
	@staticmethod
	def loadFile(source):
		source = open(source).read()
		Loader.removeCommentsAndEvaluate(source)
		return body
	
	@staticmethod
	def loadString(string):
		Loader.removeCommentsAndEvaluate(string)
		return body
		
	@staticmethod
	def removeCommentsAndEvaluate(source):
		'''Any line that starts with #:: will be treated as a comment and be exempted from further evaluation'''
		allComments = re.findall("#::.*", source)
		for comments in allComments:
			#Removing all comments in the code to prevent them interfering with the parsing.
			source = source.replace(comments, "")
		#Ok, now I am done removing comments. Do others now.
		GraphicsParser(source)
		WidgetsParser(source)
		parseScript(source)

if __name__ == "__main__":
	class MainApp(App):
		theme_cls = ThemeManager()
		def build(self):
			return Loader.loadFile("test.gml")
			print(body.ids)
		
	MainApp().run()