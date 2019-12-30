#::Any tag that falls within the graphics tag cannot have any other tag nested within it.
#::This is a typical example of a comment
#::For widgets like Button which have "text" attributes, it's not necessary to enclose the text values in quotation marks.
#::Example:
	#::This piece of code still works even though the text value isn't enclosed in quotation marks
#::	<widget>
#::		<button>
#::			text: this is a button;
#::		</button>
#::	</widget>
 
#:: As at writing this note, the shader tags aren’t working yet- 30/12/2019   18:13
<GraML>
	<begin widgets>
		<widget id=box>
			size: 100,100;
			pos: 300,200;
			<button>
				id: btnstupid;
				text: "stupid";
				pos: 200,200;
			</button>
			<button>
				pos: 100, Window.center[1]-50;
			</button>
			<TextInput>
				text: "hehehe";
				pos: 0, 600
			</TextInput>
			<MDTextField>
				id: textinput;
				text: "beans";
				pos: 200, 600;
				size: 200, 80;
			</MDTextField>
			<MDRoundFlatIconButton>
			#::This should be a comment
				icon: "settings";
				pos: 400,400;
			</MDRoundFlatIconButton>
			<button>
				text: "233"; size: 10, 300;
			</button>
		</widget>
		<widget id=yy>
			<button>
				text: "[color=#aaaeee][size=20]Text[/size][/color]";
				pos: 0,0;
				markup: True;
			</button>
			<label>
				text: "[size=45]me and you[/size]";
				pos: 30, 200;
				color: 0, .3, .7, 1.;
				markup: True;
			</label>
		</widget>
		<button>
			pos: 200,0;
		</button>
	<end widgets>
	<script src="script.py">
print("Blah blah blah")
print(availableGraphicsTags)
	</script>
#::Graphics tag contains all other drawing instructions like rectangle, ellipse, etc.
	<graphics useShader=False>
		<color mode="rgb"; value=(.5, 1, .7)/>
		<fshader source=string>
		#ifdef GL_ES
			precision highp float;
		#else
			precision mediump float;
		#endif
		varying vec4 frag_color;
		void main(){
			float x = gl_FragCoord.x;
			float y = gl_FragCoord.y;
			if (y*y - x*x >=400){gl_FragColor = vec4(.5, .6, .7, .9);}
		}
		</fshader>
		<line>
			points: (40,40, 200,200);
			width: 3;
		</line>
		<line>
			width: 20;
			points: (0,0, 300,300);
		</line>
		<rectangle>
			size: 150, 150;
			pos: 200,200;
		</rectangle>
		<ellipse>
			size: 400,400;
			pos: Window.width -410, 60;
			color: 1, .3, .6;
		</ellipse>
		<ellipse>
			size: 50,50;
			pos: 400, 700;
		</ellipse>
	</graphics>
</GraML>
		