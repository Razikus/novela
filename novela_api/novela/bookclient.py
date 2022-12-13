from immudb import ImmudbClient
from immudb.datatypes import DeleteKeysRequest
from immudb.rootService import PersistentRootService 
from pydantic import BaseModel
from .config.config import STATEFILE
from typing import List



class BookLong(BaseModel):
    title: str
    kind: str
    image: str
    content: str
    author: str
    uid: str

class BookSave(BaseModel):
    uid: str
    content: str



class BookShort(BaseModel):
    title: str
    kind: str
    author: str
    description: str

    image: str
    uid: str

class BookList(BaseModel):
    books: List[BookShort]
    

class NewBookRequest(BaseModel):
    title: str
    kind: str
    author: str
    description: str


class BookClient:
    def __init__(self, url):
        self.url = url
        if(STATEFILE != None):
            self.client = ImmudbClient(url, rs = PersistentRootService(STATEFILE), max_grpc_message_length=1024*32*1024)
        else:
            self.client = ImmudbClient(url, max_grpc_message_length=1024*32*1024)

    def _getBookContentKey(self, uid: str):
        return f"BOOKCONTENT:{uid}".encode("utf-8")
    
    def _getBookDescriptionKey(self, uid: str):
        return f"BOOKDESCRIPTION:{uid}".encode("utf-8")
    
    def _getBookLastActionKey(self, uid: str):
        return f"BOOKAILASTACTION:{uid}".encode("utf-8")

    def _getDefaultBookContent(self, title: str, author: str, image: str):
        return f"""# {title}""".encode("utf-8")    

    def addNewBook(self, bookShort: BookShort):
        self.client.set(self._getBookDescriptionKey(bookShort.uid), bookShort.json().encode("utf-8"))
        self.client.set(self._getBookContentKey(bookShort.uid), self._getDefaultBookContent(bookShort.title, bookShort.author, bookShort.image))
        return True

    def getBookShort(self, uid: str) -> BookShort:
        try:
            val = self.client.get(self._getBookDescriptionKey(uid))
            if(val and val.value):
                return BookShort.parse_raw(val.value)
            else:
                return None
        except:
            return None


    def setLastAIAction(self, uid: str, action: bytes):
        self.client.set(self._getBookLastActionKey(uid), action)
        return True


    def getBookList(self):
        prepared = []
        scanned = self.client.scan(None, b'BOOKDESCRIPTION:', True, 100)
        while scanned:
            last = None
            for key, value in scanned.items():
                last = key
                prepared.append(BookShort.parse_raw(value))
            scanned = self.client.scan(last, b'BOOKDESCRIPTION:', True, 100)
        return prepared 

    def getBookContent(self, uid: str, revision: int):
        val = self.client.verifiedGet(self._getBookContentKey(uid), revision)
        return val

    def deleteBook(self, uid: str):
        self.client.delete(DeleteKeysRequest(keys = [self._getBookContentKey(uid), self._getBookDescriptionKey(uid)]))

    def saveBookContent(self, uid: str, value: str):
        setted = self.client.streamVerifiedSetFullValue(self._getBookContentKey(uid), value.encode("utf-8"))
        return True

        
        