from fastapi import FastAPI, Depends
from .aiconnector.aiconnector import AIConnector
from pydantic import BaseModel
from fastapi.responses import FileResponse
from .config.config import STATICPREFIX, STARTING_API_KEY,DB_URL, DB_PASS, DB_USER, DB_NAME
from .bookclient import BookClient, NewBookRequest, BookShort
import uuid
import json
import os
import asyncio
from starlette.background import BackgroundTask


app = FastAPI(title = "Novela API", version = "0.1.0")

loadedConfig = None

@app.on_event("startup")
async def startup():
    global loadedConfig
    bookClient = getBookClient()
    configVal = bookClient.client.get(b"CONFIG")
    if(configVal and configVal.value):
        loadedConfig = ConfigRequest.parse_raw(configVal.value)
    else:
        loadedConfig = ConfigRequest(api_key=STARTING_API_KEY)

async def getAIClient() -> AIConnector:
    connector = AIConnector(loadedConfig.api_key)
    return connector

def getBookClient() -> BookClient:
    client = BookClient(DB_URL)
    client.client.login(DB_USER.encode("utf-8"), DB_PASS.encode("utf-8"), DB_NAME.encode("utf-8"))
    return client


class CreateImageReq(BaseModel):
    sentence: str


class CreateCompletionReq(BaseModel):
    storyStart: str
    storyEnd: str = None
    length: int = 1024
    actionType: str = ""

class CreateInspirationReq(BaseModel):
    somethingAbout: str = None
    fullAuto: bool = False
    length: int = 4096
    kind: str = ""

class BookSaveRequest(BaseModel):
    content: str

class BookUndoRequest(BaseModel):
    undo: int

class ConfigRequest(BaseModel):
    api_key: str

@app.get("/api/v1/images/get/{uid}")
async def get_image(uid):
    return FileResponse(STATICPREFIX + str(uid))

@app.post("/api/v1/config")
async def setConfig(req: ConfigRequest, dbClient: BookClient = Depends(getBookClient)):
    global loadedConfig
    dbClient.client.set(b"CONFIG", req.json().encode("utf-8"))
    loadedConfig = req
    return True


@app.post("/api/v1/book/create")
async def create_book(req: NewBookRequest, dbClient: BookClient = Depends(getBookClient), connector: AIConnector = Depends(getAIClient)):
    newuuid = str(uuid.uuid4())
    imageForSentence = connector.imageClient.getImageForSentence(req.description, "512x512", f", {req.kind} style")
    firstImage = imageForSentence[0]
    bookShort = BookShort(title = req.title, kind = req.kind, author = req.author, description=req.description, image = firstImage, uid = newuuid)
    dbClient.addNewBook(bookShort)
    return bookShort

@app.get("/api/v1/book/list")
async def list_books(dbClient: BookClient = Depends(getBookClient), connector: AIConnector = Depends(getAIClient)):
    return dbClient.getBookList()

@app.post("/api/v1/book/{uid}/save")
async def save_book(uid: str, req: BookSaveRequest, dbClient: BookClient = Depends(getBookClient)):
    return dbClient.saveBookContent(uid, req.content)

@app.delete("/api/v1/book/{uid}/delete")
async def delete_book(uid: str, dbClient: BookClient = Depends(getBookClient)):
    return dbClient.deleteBook(uid)


@app.get("/api/v1/book/{uid}/info")
async def get_book(uid: str, dbClient: BookClient = Depends(getBookClient)):
    try:
        return dbClient.getBookShort(uid)
    except:
        return None

@app.get("/api/v1/book/{uid}/get")
async def get_book(uid: str, revision: int = 0, dbClient: BookClient = Depends(getBookClient)):
    try:
        return dbClient.getBookContent(uid, revision)
    except:
        return None

def cleanup(fileToSave, pdfPath):
    def clean():
        os.remove(fileToSave)
        if(pdfPath):
            os.remove(pdfPath)
    return clean

@app.get("/api/v1/book/{uid}/pdf")
async def get_pdf(uid, dbClient: BookClient = Depends(getBookClient)):
    book = dbClient.getBookShort(uid)
    content = dbClient.getBookContent(uid, 0)
    if content and content.value:
        uuidOf = str(uuid.uuid4())
        fileToSave = "/tmp/" + uuidOf + ".md"
        pdfPath = "/tmp/" + uuidOf + ".pdf"
        with open(fileToSave, "w") as toWrite:
            decoded = content.value.decode("utf-8")
            decoded = decoded.replace("/api/v1/images/get/", "http://localhost:8000/api/v1/images/get/")
            toWrite.write(decoded)

        proc = await asyncio.create_subprocess_shell(
            f"mdpdf {fileToSave} {pdfPath}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return FileResponse(pdfPath, background=BackgroundTask(cleanup(fileToSave, pdfPath)))
    return None


@app.get("/api/v1/book/{uid}/md")
async def get_pdf(uid, dbClient: BookClient = Depends(getBookClient)):
    book = dbClient.getBookShort(uid)
    content = dbClient.getBookContent(uid, 0)
    if content and content.value:
        uuidOf = str(uuid.uuid4())
        fileToSave = "/tmp/" + uuidOf + ".md"
        with open(fileToSave, "wb") as toWrite:
            toWrite.write(content.value)

        return FileResponse(fileToSave, background=BackgroundTask(cleanup(fileToSave, None)))
    return None
        


@app.post("/api/v1/book/{uid}/ai/complete")
async def complete_it(uid, req: CreateCompletionReq, dbClient: BookClient = Depends(getBookClient),  connector: AIConnector = Depends(getAIClient)):
    story = connector.storyCompletor.completeStory(req.storyStart, suffix = req.storyEnd, action = req.actionType)
    dbClient.setLastAIAction(uid, json.dumps(story).encode("utf-8"))
    firstChoice = story["choices"][0]["text"]
    return {"text": firstChoice}

@app.post("/api/v1/book/{uid}/ai/summaryImage")
async def generateSummaryImage(uid: str, req: CreateImageReq, dbClient: BookClient = Depends(getBookClient), connector: AIConnector = Depends(getAIClient)):
    book = dbClient.getBookShort(uid)
    story = connector.imageClient.getImageForSummary(req.sentence, size = "512x512", withStyle = book.kind)
    dbClient.setLastAIAction(uid, json.dumps(story).encode("utf-8"))
    return story


@app.post("/api/v1/book/{uid}/ai/image")
async def genereateImage(uid: str, req: CreateImageReq, dbClient: BookClient = Depends(getBookClient), connector: AIConnector = Depends(getAIClient)):
    book = dbClient.getBookShort(uid)
    story = connector.imageClient.getImageForSentence(req.sentence, size = "512x512", withStyle = book.kind)
    dbClient.setLastAIAction(uid, json.dumps(story).encode("utf-8"))
    return story

@app.post("/api/v1/inspire")
async def inspire_me(req: CreateInspirationReq, dbClient: BookClient = Depends(getBookClient),  connector: AIConnector = Depends(getAIClient)):
    inspirationbook = "inspirationbook"
    book = dbClient.getBookShort(inspirationbook)
    if(book == None):
        image = connector.imageClient.getImageForSentence("Bowl of tousands of thoughs and mist, fantasy digital art", size = "512x512", withStyle = "fantasy")
        dbClient.addNewBook(BookShort(
            uid = inspirationbook,
            title  = "Book of inspirations",
            kind = "fantasy",
            author = "Everyone",
            description = "Contains every inspiration that you created",
            image = image[0]
        ))
        
    if(req.fullAuto):
        about = ""
        if(req.somethingAbout and req.somethingAbout != ""):
            about = "about " + req.somethingAbout

        story = connector.storyCompletor.completeStory(f"Geneate a creative {req.kind} story or novel or poem or text {about}", temperature=0.8, max_tokens=req.length)
        dbClient.setLastAIAction("INSPIRATIONS", json.dumps(story).encode("utf-8"))
        firstChoice = story["choices"][0]["text"]
        dbClient.saveBookContent(inspirationbook, firstChoice)
        image = connector.imageClient.getImageForSummary(firstChoice, size = "512x512", withStyle = req.kind)
        dbClient.saveBookContent(inspirationbook, firstChoice + "\n" + f"![summary](/api/v1/images/get/{image[0]})")
        return {"text": firstChoice, "image": image[0]}
    else:

        story = connector.storyCompletor.completeStory(req.somethingAbout, temperature=0.8, max_tokens=req.length)
        dbClient.setLastAIAction("INSPIRATIONS", json.dumps(story).encode("utf-8"))
        firstChoice = story["choices"][0]["text"]
        dbClient.saveBookContent(inspirationbook, firstChoice)
        image = connector.imageClient.getImageForSummary(firstChoice, size = "512x512", withStyle = req.kind)
        dbClient.saveBookContent(inspirationbook, firstChoice + "\n" + f"![summary](/api/v1/images/get/{image[0]})")


        return {"text": firstChoice, "image": image[0]}