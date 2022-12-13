<template>
  <q-page class="flex flex-center">
    <div>
    <img
      alt="Novela ink"
      src="~assets/logo-3.png"
      style="width: 400px; display:block;"
    >
    <div class="center">
    <hr/>
    <p class="text-h2">novela.ink</p>
    <p>Your friendly AI assistent for <span class="text-h6 colored changing"></span> </p>
    
  </div>
  </div>
  </q-page>
</template>
<style>
.center {
  text-align: center;
}

.changing::before {
    content: "novels";
    animation: animate infinite 5s;
}

@keyframes animate {
    10% {
        content: "stories";
    }
    20% {
        content: "dramas";
    }
    30% {
        content: "prose";
    }
    40% {
        content: "poetry";
    }
    50% {
        content: "epics";
    }
    60% {
        content: "chronicles";
    }
    70% {
        content: "poems";
    }
    80% {
        content: "guidebooks";
    }
    90% {
        content: "bestsellers";
    }

}
.colored
{
  background-image: linear-gradient(
    -225deg,
    #0e6975 0%,
    #0277bd 29%,
    #9a0033 67%,
    #000000 100%
  );
  background-size: auto auto;
  background-clip: border-box;
  background-size: 100% auto;
  color: #fff;
  background-clip: text;
  text-fill-color: transparent;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}


</style>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'IndexPage',
  data() {
    return {
    }
  }
})
</script>
