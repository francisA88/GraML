#from itertools import cycle

def func(dt):
	from itertools import cycle
	data = cycle(range(200))
	print(body.ids)
	body.ids.box.children[0].text = str(next(data))
	
Clock.schedule_once(func, .5)
print("\nscript executed here!!!\n")