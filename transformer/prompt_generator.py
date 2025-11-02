def examples(meta):
    ex=[]
    d=meta["description"]; t=meta["title"]
    if d: ex.append({"instruction":"Summarize this bug in 1 sentence.",
                     "input":d[:2000],"output":t})
    for i,c in enumerate(meta["comments"][:2]):
        ex.append({"instruction":"Answer the question based on the bug.",
                   "input":f"Title: {t}\nDescription: {d[:1000]}\nQ: {c}",
                   "output":meta["comments"][i+1] if i+1<len(meta["comments"]) else "No reply."})
    ex.append({"instruction":"Predict final status (Open/In Progress/Resolved/Closed).",
               "input":f"Title: {t}\nDescription: {d[:1500]}","output":meta["status"]})
    return ex