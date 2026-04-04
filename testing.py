import requests

url = "http://127.0.0.1:8000/extract"
files = {"file": open("./kumaresan-resume.pdf", "rb")}  # rb = read binary
response = requests.post(url, files=files)

print(response.json())
