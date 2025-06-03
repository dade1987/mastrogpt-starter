import vision
import vdb
import bucket
import base64


USAGE = f"""Welcome to the Vector DB Loader.
Write text to insert in the DB. 
Use `@[<coll>]` to select/create a collection and show the collections.
Use `*<string>` to vector search the <string>  in the DB.
Use `#<limit>`  to change the limit of searches.
Use `!<substr>` to remove text with `<substr>` in collection.
Use `!![<collection>]` to remove `<collection>` (default current) and switch to default.
Use `$<img>` to load an image from S3 (eg. s3path),  empty to list available images on S3
"""

def loader(args):
  #print(args)
  # get state: <collection>[:<limit>]
  collection = "default"
  limit = 30
  sp = args.get("state", "").split(":")
  if len(sp) > 0 and len(sp[0]) > 0:
    collection = sp[0]
  if len(sp) > 1:
    try:
      limit = int(sp[1])
    except: pass
  print(collection, limit)

  out = f"{USAGE}Current collection is {collection} with limit {limit}"
  db = vdb.VectorDB(args, collection)
  buc = bucket.Bucket(args)
  vis= vision.Vision(args)

  inp = str(args.get('input', ""))

  print(inp)

  # select collection
  if inp.startswith("@"):
    out = ""
    if len(inp) > 1:
       collection = inp[1:]
       out = f"Switched to {collection}.\n"
    out += db.setup(collection)
  # set size of search
  elif inp.startswith("#"):
    try: 
       limit = int(inp[1:])
    except: pass
    out = f"Search limit is now {limit}.\n"
  # run a query
  elif inp.startswith("*"):
    search = inp[1:]
    if search == "":
      search = " "
    res = db.vector_search(search, limit=limit)
    if len(res) > 0:
      out = f"Found:\n"
      for i in res:
        out += f"({i[0]:.2f}) {i[1]}\n"
    else:
      out = "Not found"
  # remove a collection
  elif inp.startswith("!!"):
    if len(inp) > 2:
      collection = inp[2:].strip()
    out = db.destroy(collection)
    collection = "default"
  # remove content
  elif inp.startswith("!"):
    count = db.remove_by_substring(inp[1:])
    out = f"Deleted {count} records."    
  elif inp.startswith("$"):
    if len(inp) > 1:
      img = inp[1:].strip()
      img = buc.find(inp[1:])
      
      if len(img) > 0:
        key = img[0]
        out = f"Looking at {key}, I see:\n"
        data = buc.read(key)
        img = base64.b64encode(data).decode("utf-8")
        out += vis.decode(img)
    else:
      print("Listing images in bucket")
      ls = buc.find("")
      out = "Found:\n"
      for item in ls:
        out += f"- {item}\n"
    
  elif inp != '':
    out = "Inserted "
    lines = [inp]
    if args.get("options","") == "splitlines":
      lines = inp.split("\n")
    for line in lines:
      if line == '': continue
      res = db.insert(line)
      out += "\n".join([str(x) for x in res.get("ids", [])])
      out += "\n"

  return {"output": out, "state": f"{collection}:{limit}"}
  
