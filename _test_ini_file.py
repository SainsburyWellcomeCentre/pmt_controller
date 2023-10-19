import ujson as json

data={"name": "Peter", "car": "renault", "id": 452}

def write_file(data):
    with open("/store.ini", "w") as f:
        s = json.dumps(data)
        f.write(s)
        
def read_file():
    with open("/store.ini", "r") as f:
        data = json.load(f)
        return data

write_file(data)

data = read_file()
print(data)
