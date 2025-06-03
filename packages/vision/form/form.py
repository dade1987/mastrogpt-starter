import os, requests as req
import vision2 as vision

USAGE = "Please upload a picture and I will tell you what I see"
FORM = [
  {
    "label": "Load Image",
    "name": "pic",
    "required": "true",
    "type": "file"
  },
]

def form(args):
  res = {}
  out = USAGE
  inp = args.get("input", "")

  if type(inp) is dict and "form" in inp:
    img = inp.get("form", {}).get("pic", "")
    print(f"uploaded size {len(img)}")
    vis = vision.Vision(args)
    out = vis.decode(img)
    res['html'] = f'<img src="data:image/png;base64,{img}">'
    
  res['form'] = FORM
  res['output'] = out
  return res
