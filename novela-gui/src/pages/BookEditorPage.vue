<template>
  <q-page padding>

    <div class="q-pa-md q-gutter-sm fit full-height" style="height: 88vh!important;">
      <div class="q-pa-md row">
      <q-btn label="Save (ctrl + s)" @click="save" color="accent" icon="save"></q-btn>
      <q-btn label="Undo (ctrl + z)" @click="undo" color="accent" icon="undo"></q-btn>
      <q-btn v-if="revision < 0" :label="`Redo (ctrl + y) revision: ${revision}`" @click="redo" color="accent"
        icon="redo"></q-btn>
        <q-space></q-space>
      <q-btn label="PDF" @click="downloadPDF" color="accent" icon="download"></q-btn>
      <q-btn label="MD" @click="downloadMD" color="accent" icon="download"></q-btn>
    </div>
      <q-splitter v-model="splitterModel" class="full-height">

        <template v-slot:before>
          <div class="q-pa-md">
            <q-input ref="maineditor" v-model="markdown" rows="40" type="textarea" class="fit q-pa-sm">
              <q-menu touch-position context-menu>

                <q-list dense style="min-width: 100px">
                  <q-item @click="storyProposition('')" clickable v-close-popup>
                    <q-item-section>Find a story proposition here</q-item-section>
                  </q-item>
                  <q-item @click="storyProposition('full of action')" clickable v-close-popup>
                    <q-item-section>Find a full of action proposition here</q-item-section>
                  </q-item>
                  <q-item @click="storyProposition('crazy')" clickable v-close-popup>
                    <q-item-section>Find a crazy proposition here</q-item-section>
                  </q-item>
                  <q-item @click="storyProposition('sad')" clickable v-close-popup>
                    <q-item-section>Find a sad proposition here</q-item-section>
                  </q-item>
                  <q-item @click="storyProposition('funny')" clickable v-close-popup>
                    <q-item-section>Find a funny proposition here</q-item-section>
                  </q-item>
                  <q-item @click="storyProposition('unexpected')" clickable v-close-popup>
                    <q-item-section>Find a unexpected proposition here</q-item-section>
                  </q-item>
                  <q-item @click="storyProposition(bookInfo.kind)" clickable v-close-popup>
                    <q-item-section>Find a "{{bookInfo.kind}}" proposition here</q-item-section>
                  </q-item>
                  <q-separator />
                  <q-item @click="insertImage" clickable v-close-popup>
                    <q-item-section>Generate an image as summary (for chapter or selected selection)</q-item-section>
                  </q-item>
                  <q-item @click="insertImageForSentence" clickable v-close-popup>
                    <q-item-section>Generate an image for selected sentence</q-item-section>
                  </q-item>
                  <q-separator />
                  <q-item clickable v-close-popup>
                    <q-item-section>Quit menu</q-item-section>
                  </q-item>
                </q-list>

              </q-menu>

              <q-inner-loading :showing="loading">
                <q-spinner-ball size="50px" class="coloredloader" />
              </q-inner-loading>
            </q-input>
          </div>
        </template>

        <template v-slot:after>
          <div class="q-pa-md full-height">
            <q-markdown :src="markdown" class="fit bordered q-pa-sm">
            </q-markdown>
          </div>
        </template>
      </q-splitter>

    </div>

  </q-page>
</template>

<style>
.coloredloader {
  color: #000;
  animation: color-change 3s infinite;
}

@keyframes color-change {
  0% {
    color: red;
  }

  25% {
    color: blue;
  }

  50% {
    color: green;
  }

  75% {
    color: purple;
  }

  100% {
    color: red;
  }
}
</style>

<script>

import { ref } from "vue";
import { useQuasar } from 'quasar'

export default {
  data() {
    return {
      q: useQuasar(),
      splitterModel: 50,
      revision: ref(0),
      autoSave: ref(-1),
      loading: ref(false),
      markdown: ref(``),
      bookInfo: ref({})

    }
  },
  mounted() {
    this.loadBookInfo()
    this.loadContent()
    this.autoSave = setInterval(this.autoSaveFunction, 60000)
    document.addEventListener('keydown', this.keyboardListener);
  },
  beforeUnmount() {
    clearInterval(this.autoSave)
    document.removeEventListener("keydown", this.keyboardListener)
  },
  methods: {
    keyboardListener(event) {
      if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        this.save()
      } else if(event.ctrlKey && event.key === 'z' && !this.loading) {
        event.preventDefault();
        this.undo()

      } else if(event.ctrlKey && event.key === 'y' && this.revision < 0 && !this.loading) {
        event.preventDefault();
        this.redo()

      }

    },
    insertInto(index, what) {
      if (index > 0) {
        this.markdown = this.markdown.substring(0, index) + what + this.markdown.substr(index);
      }
      else {
        this.markdown = what + this.markdown;

      }


    },
    async downloadPDF() {
      window.open(window.location.origin + "/api/v1/book/" + this.$route.params.id + "/pdf", "_blank")

    },
    async downloadMD() {
      window.open(window.location.origin + "/api/v1/book/" + this.$route.params.id + "/md", "_blank")

    },
    async loadBookInfo() {
      let data = await this.$novelaAPI.getBookInfo(this.$route.params.id)
      this.bookInfo = data.data

    },
    async loadContent() {
      this.loading = true
      let data = await this.$novelaAPI.getContent(this.$route.params.id, this.revision)
      if (data.data) {
        this.markdown = data.data.value
      }
      this.loading = false
    },
    async autoSaveFunction() {
      if(this.revision == 0) {
        
        let data = await this.$novelaAPI.save(this.$route.params.id, this.markdown)
        this.revision = 0
        this.q.notify({
          message: "Content saved",
          color: "positive",
          timeout: 100
        })
      }

    },
    async save() {
      let data = await this.$novelaAPI.save(this.$route.params.id, this.markdown)
      this.revision = 0
      this.q.notify({
        message: "Content saved",
        color: "positive",
        timeout: 100
      })

    },
    async undo() {
      this.revision = this.revision - 1
      await this.loadContent()
      this.q.notify({
        message: "Content undoed. Ctrl + s to save!",
        color: "positive"
      })

    },
    async redo() {
      this.revision = this.revision + 1
      await this.loadContent()
      this.q.notify({
        message: "Content redoed. Ctrl + s to save!",
        color: "positive"
      })

    },

    async storyProposition(action) {
      this.loading = true
      await this.save()
      let currentMarkdown = this.markdown
      let starts = this.$refs.maineditor.nativeEl.selectionStart
      let ends = this.$refs.maineditor.nativeEl.selectionEnd

      if (ends > starts) {
        let textToComplete = ""
        textToComplete = currentMarkdown.substring(starts, ends)
        let data = await this.$novelaAPI.getStoryCompletion(this.$route.params.id, textToComplete, undefined, action)
        this.insertInto(ends, `${data.data.text}`)
      } else {
        let textBefore = starts - 500
        let textAfter = starts + 500
        let textBeforeText = currentMarkdown.substring(textBefore, starts)
        let chapterStart = textBeforeText.lastIndexOf("# ")
        if (chapterStart >= 0) {
          textBeforeText = textBeforeText.substring(chapterStart + 2)

        }
        let textAfterText = currentMarkdown.substring(starts, textAfter)
        let newChapter = textAfterText.indexOf("# ")
        if (newChapter >= 0) {
          textAfterText = currentMarkdown.substring(0, newChapter)
        }
        let data = await this.$novelaAPI.getStoryCompletion(this.$route.params.id, textBeforeText, textAfterText, action)
        this.insertInto(starts, data.data.text)
      }
      await this.save()
      this.loading = false

    },
    async insertImage() {
      this.loading = true
      await this.save()
      let currentMarkdown = this.markdown
      let starts = this.$refs.maineditor.nativeEl.selectionStart
      let ends = this.$refs.maineditor.nativeEl.selectionEnd
      if(starts > ends && ends != -1) {
        let tempStarts = starts
        starts = ends
        ends = tempStarts
      }

      let textToSummary = ""
      if (ends > starts) {
        textToSummary = currentMarkdown.substring(starts, ends)
        let data = await this.$novelaAPI.getSummaryImage(this.$route.params.id, textToSummary)
        this.insertInto(ends + "\n", `![summary](/api/v1/images/get/${data.data[0]})`)
      } else {
        let textBefore = starts - 500
        let textAfter = starts + 500
        let textBeforeText = currentMarkdown.substring(textBefore, starts)
        let chapterStart = textBeforeText.lastIndexOf("# ")
        if (chapterStart >= 0) {
          textBeforeText = textBeforeText.substring(chapterStart + 2)

        }
        let textAfterText = currentMarkdown.substring(starts, textAfter)
        let newChapter = textAfterText.indexOf("# ")
        if (newChapter >= 0) {
          textAfterText = currentMarkdown.substring(0, newChapter)
        }

        textToSummary = textBeforeText + "\n" + textAfterText
        let data = await this.$novelaAPI.getSummaryImage(this.$route.params.id, textToSummary)
        this.insertInto(starts, `![summary](/api/v1/images/get/${data.data[0]})`)
      }
      await this.save()
      this.loading = false
    },
    async insertImageForSentence() {
      this.loading = true
      await this.save()

      let currentMarkdown = this.markdown
      let starts = this.$refs.maineditor.nativeEl.selectionStart
      let ends = this.$refs.maineditor.nativeEl.selectionEnd
      if(starts > ends && ends != -1) {
        let tempStarts = starts
        starts = ends
        ends = tempStarts
      }

      let textToSummary = ""
      if (ends > starts) {
        textToSummary = currentMarkdown.substring(starts, ends)
        let data = await this.$novelaAPI.getSentenceImage(this.$route.params.id, textToSummary)
        this.insertInto(ends + "\n", `![sentence](/api/v1/images/get/${data.data[0]})`)
      } else {
        this.q.notify({
          message: "Select content or choose summary image",
          color: "negative",
          timeout: 100
        })
        
      }

      this.loading = false

    }
  }
}
</script>
