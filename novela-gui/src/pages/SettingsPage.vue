<template>
  <q-page padding>
    <div class="row justify-center center-items">
      <div class="col-md-10 col-sm-12">
        <q-card>
          <q-toolbar class="bg-secondary text-white q-pa-sm">
            Basic application settings
          </q-toolbar>
          <div class="q-pa-md">
            <q-input v-model="api_key" label="New OpenAPI Key" type="password"></q-input>
            <q-btn @click="setApiKey" color="accent" label="Set new API Key"></q-btn>
          </div>
        </q-card>

      </div>
    </div>
  </q-page>
</template>

<style>
.inputek {
  width: 300px;
  margin: 6px;
}

.coloredbutton {
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
  methods: {
    async setApiKey() {
      this.loading = true
      let data = await this.$novelaAPI.setApiKey({
        api_key: this.api_key
      })
      this.q.notify({
        message: "Config saved",
        color: "positive"
      })
      this.loading = false
    }

  },
  data() {
    return {
      inspiration: ref({
        fullAuto: true
      }),
      q: useQuasar(),
      loading: ref(false),
      loaded: ref({}),
      api_key: ref("")
    }
  }
  // name: 'PageName',
}
</script>
