import httpx

# resp = httpx.post("http://127.0.0.1:8001/v1/completions", json={})
# print(resp.text)

with httpx.stream("POST", "http://127.0.0.1:8001/v1/completions", json={}) as resp:
    for chunk in resp.iter_text():
        print(chunk, end="", flush=True)
        
print("\n\n Done")