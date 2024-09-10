import ollama

resp = ollama.chat(
    model="llama3",
    messages=[
        {
            "role": "user",
            "content": "more details on lagaan",
        },
    ],
    stream=True,
)

for r in resp:
    print(r["message"]["content"])
