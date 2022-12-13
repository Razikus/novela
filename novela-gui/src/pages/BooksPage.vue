<template>


  <q-dialog v-model="addNewBook" persistent>
    <q-card>
      <q-card-section class="row items-center">
        <q-avatar icon="note" color="primary" text-color="white" />
        <span class="q-ml-sm">Fill the form and hit Create!</span>
      </q-card-section>
      <q-card-section class="row ">
        <q-input class="inputbook" v-model="newBook.title" label="Book name"></q-input>
        <q-input class="inputbook" v-model="newBook.author" label="Book author"></q-input>
        <q-input class="inputbook" v-model="newBook.description"
          label="Book short description (Small kid found his love on the moon)"></q-input>
        <q-input class="inputbook" v-model="newBook.kind" label="Book kind (fantasy, romance)"></q-input>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn flat label="Create" color="primary" @click="create" />
      </q-card-actions>
      <q-inner-loading :showing="loadingCreate">
        <q-spinner-ball size="50px" class="coloredloader" />
      </q-inner-loading>
    </q-card>
  </q-dialog>
  <q-page padding>
    <q-btn @click="addNewBook = true" label="Add new" color="accent" icon="add"></q-btn>
    <div class="row">
      <div class="col-md-4 col-sm-6 q-pa-md" v-for="book in books" v-bind:key="book.uid">
        <q-card class="my-card" >
          <img :src="`${imageApiPrefix}/${book.image}`" @click="$router.push(`/book/${book.uid}`)">

          <q-card-section>
            <div class="text-h6">{{ book.title }}</div>
            <div class="text-subtitle2">{{ book.author }}</div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            {{ book.description }}
          </q-card-section>
          <q-card-actions>
            <q-btn :disabled="book.uid == 'inspirationbook'" @click="remove(book.uid)" color="red" label="Remove" dense icon="delete"></q-btn>
            <q-space/>
            <q-btn :disabled="book.uid == 'inspirationbook'" @click="downloadPDF(book.uid)" color="secondary" label="PDF" dense icon="download"></q-btn>
            <q-btn :disabled="book.uid == 'inspirationbook'" @click="downloadMD(book.uid)" color="secondary" label="MD" dense icon="download"></q-btn>
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <q-inner-loading :showing="loading">
      <q-spinner-ball size="50px" class="coloredloader" />
    </q-inner-loading>
  </q-page>
</template>

<style>
.inputbook {
  margin: auto;
  width: 512px;
}
</style>

<script>
import { ref } from "vue";
import { useQuasar } from 'quasar'

export default {
  mounted() {
    this.loadBooks()
  },
  methods: {
    async loadBooks() {
      this.loading = true
      let data = await this.$novelaAPI.listBooks()
      this.books = data.data
      this.loading = false
    },
    async create() {
      this.loadingCreate = true
      let data = await this.$novelaAPI.addBook(this.newBook)
      this.q.notify({
        message: "Book created",
        color: "positive"
      })
      await this.loadBooks()
      this.addNewBook = false
      this.loadingCreate = false
    },
    async downloadPDF(uid) {
      window.open(window.location.origin + "/api/v1/book/" + uid+ "/pdf", "_blank")

    },
    async downloadMD(uid) {
      window.open(window.location.origin + "/api/v1/book/" + uid + "/md", "_blank")

    },
    async remove(uid) {
      this.loading = true
      await this.$novelaAPI.deleteBook(uid)
      setTimeout(this.loadBooks, 500)
    }
  },
  data() {
    return {
      books: ref([]),
      loading: ref(false),
      loadingCreate: ref(false),
      q: useQuasar(),
      imageApiPrefix: window.location.origin + "/api/v1/images/get",
      addNewBook: ref(false),
      newBook: ref({})
    }
  }
}
</script>
