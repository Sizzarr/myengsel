from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webapp.server:app", host="127.0.0.1", port=8765, reload=False)
