import os, json, requests as req

MODEL = "llama3.2-vision:11b"

def collect(lines):
  out = ""
  for line in lines:
    #line = next(lines)
    chunk = json.loads(line.decode("UTF-8"))
    out +=  chunk.get("message", {}).get("content", "")
  return out

class Vision:
  def __init__(self, args):
    host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
    auth = args.get("AUTH", os.getenv("AUTH"))
    self.url = f"https://{auth}@{host}/api/chat"

  def decode(self, img):
    msg = {
      "model": MODEL,
      "messages": [ {
        "role": "user",
        "content": "describe the image",
        "images": [img]
      },
      ],
      "stream": False
    }
    lines = req.post(self.url, json=msg, stream=True).iter_lines()
    res = req.post(self.url, json=msg)
    return collect(lines)

