response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"system","content":system_prompt}, {"role":"user","content":user_message}]
)
bot_reply = response.choices[0].message.content
