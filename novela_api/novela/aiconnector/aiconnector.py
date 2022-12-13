
import openai
import requests
import uuid
from ..config.config import STATICPREFIX

class AIConnector:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.api_key = api_key
        self.imageClient = None
        self.storyCompletor = None
        self.summarizer = None
        self.initializeClients()

    def initializeClients(self):
        self.storyCompletor = AIStoryCompletor(self.api_key)
        self.summarizer = AiSummarizer(self.api_key)
        self.imageClient = AIImagerClient(self.api_key, self.summarizer)



class AIImagerClient:
    def __init__(self, api_key, summarizer):
        self.api_key = api_key
        self.client = openai.Image()
        self.summarizer = summarizer

    def saveImage(self, fromWhat):
        returnUrls = []
        for item in fromWhat["data"]:
            urlOf = item["url"]
            saveId = str(uuid.uuid4()) + ".png"
            savePath = STATICPREFIX + saveId
            retrieved = requests.get(urlOf)
            with open(savePath, "wb") as toSave:
                toSave.write(retrieved.content)
            returnUrls.append(saveId)
        return returnUrls


    def getImageForSummary(self, summary, size="256x256", withStyle = None):
        whatIsThat = self.summarizer.whatIsThatAbout(summary)
        if(not withStyle):
            withStyle = ""
        else:
            withStyle = f", {withStyle} style"
        return self.getImageForSentence(whatIsThat["choices"][0]["text"], size, withStyle)


    
    def getImageForSentence(self, sentence, size="256x256", withStyle = None):
        style = ""
        if(withStyle):
            style = ", " + withStyle
        generated = self.client.create(**{
            "prompt": sentence + style,
            "n": 1,
            "size": size,
        })
        urls = self.saveImage(generated)
        return urls

class AIStoryCompletor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = "text-davinci-003"
        self.client = openai.Completion()

    def completeStory(self, forWhat, temperature = 0.3, max_tokens=2048, suffix = None, action = "", n = 1):
        forWhat = f"Find a {action} continue for:\n" + forWhat
        print(forWhat)
        req = {
            "model": self.model,
            "prompt": forWhat,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "n": n
        }
        if suffix:
            req["suffix"] = suffix
        completed = self.client.create(**req)
        return completed



class AiSummarizer:

    def __init__(self, api_key):
        self.api_key = api_key
        self.model = "text-davinci-003"
        self.client = openai.Completion()

    def whatIsThatAbout(self, content, max_tokens=256):
        req = {
            "model": self.model,
            "prompt": "Generate a short one sentence summary that could be applicable as DALEE2 input in english that has max 12 words, about this: \n" + content,
            "max_tokens": max_tokens,
            "temperature": 0.8,
            "n": 1
        }
        answer = self.client.create(**req)
        return answer