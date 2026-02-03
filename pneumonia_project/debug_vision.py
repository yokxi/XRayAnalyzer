from src.tools.vision import VisionTool
import inspect

vt = VisionTool()
print(f"Attributes of VisionTool: {dir(vt)}")
if hasattr(vt, 'analyze'):
    print("SUCCESS: analyze method found via hasattr")
    print(f"Source: {inspect.getsource(vt.analyze)[:100]}...")
else:
    print("FAILURE: analyze method NOT found")
    print(f"File location: {inspect.getfile(VisionTool)}")
