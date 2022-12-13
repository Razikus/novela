import { boot } from 'quasar/wrappers'
import axios from 'axios'

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({ baseURL: window.location.origin })

class NovelaAPIClient {
  constructor(apiClient) {
    this.apiClient = apiClient
  }
  async getStoryCompletion(uid, storyStart, storyEnds, action) {
    return await this.apiClient.post(`/api/v1/book/${uid}/ai/complete`, {
        storyStart: storyStart,
        storyEnd: storyEnds,
        actionType: action
    })
  }
  async getSummaryImage(uid, story) {
    return await this.apiClient.post(`/api/v1/book/${uid}/ai/summaryImage`, {
      sentence: story,
    })

  }
  async getSentenceImage(uid, story) {
    return await this.apiClient.post(`/api/v1/book/${uid}/ai/image`, {
      sentence: story,
    })
  }
  async save(uid, content) {
    return await this.apiClient.post(`/api/v1/book/${uid}/save`, {
        content: content,
    })
  }
  async getContent(uid, revision) {
    return await this.apiClient.get(`/api/v1/book/${uid}/get`, {
      params: {
        revision: revision
      }
    })
  }
  async setApiKey(config) {
    return await this.apiClient.post(`/api/v1/config`, config)
  }
  async getBookInfo(uid) {
    return await this.apiClient.get(`/api/v1/book/${uid}/info`)
  }
  async listBooks() {
    return await this.apiClient.get(`/api/v1/book/list`)
  }
  async addBook(book) {
    return await this.apiClient.post(`/api/v1/book/create`, book)
  }
  async deleteBook(uid) {
    return await this.apiClient.delete(`/api/v1/book/${uid}/delete`)
  }
  async createInspiration(req) {
    return await this.apiClient.post(`/api/v1/inspire`, req)
  }

}

const novelaAPI = new NovelaAPIClient(api)

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  app.config.globalProperties.$novelaAPI = novelaAPI
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
})

export { api, novelaAPI }
