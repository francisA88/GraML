# GraML
Graphical Markup Language.
A markup language made specifically for making graphical user interfaces.
It is intended to simplify making GUIs being written in Python itself using Kivy library.

To run the example "example.graml", run loader.py.
Other examples can be loaded by changing the file name in loader.py to the example file name.

GraML files can also be loaded by importing the loader.py and doing:
loader.Loader("pathtoyourgrmfile.graml") #extensions can also be in .xml

GraML files should be in this format:
<GraML>
  <Body>other Widget tags here</Body>
  <Script>Python script here. Preserve Python's indentation
  </Script>
  <Canvas>
   Canvas tags here
  </Canvas>
  <Shader>
    <Fragment>fragment shader here</Fragment>
    <Vertex> vertex shader here</Vertex>
  </Shader>
</GraML>

For a list of tags that can be nested in these base tags, visit kivy.org
For example, Widget tags include Widget itself, Button, FloatLayout, GridLayout, etc.
Canvas tags include Rectangle, Ellipse, etc.
