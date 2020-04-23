'''Make sure Kivy is installed before usage'''
try: import kivy
except ImportError:
    raise ImportError("Kivy is needed to use GraML")
    exit()