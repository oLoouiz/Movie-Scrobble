import http.client

conn = http.client.HTTPSConnection("netflix-movies-and-tv-shows1.p.rapidapi.com")

payload = "page=1&type=Movie&release_year=1975"

headers = {
    'x-rapidapi-key': "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxc",
    'x-rapidapi-host': "netflix-movies-and-tv-shows1.p.rapidapi.com",
    'Content-Type': "application/x-www-form-urlencoded"
}

conn.request("POST", "/list", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))