<template>
  <div>
    <FullWidthLoading v-if="apiDataLoader?.state.loading">
      <p>{{ loadingText }}</p>
    </FullWidthLoading>
    <FullWidthError v-else-if="apiDataLoader?.state.error">
      <p>{{ apiDataLoader.state.error }}</p>
    </FullWidthError>
    <slot v-else-if="apiDataLoader?.state.loaded"/>
    <slot v-else name="before-load"/>
  </div>
</template>

<script setup lang="ts">
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import FullWidthLoading from 'components/FullWidthLoading.vue'
import FullWidthError from 'components/FullWidthError.vue'

defineProps({
  apiDataLoader: {
    type: PortalApiDataLoader,
  },
  loadingText: {
    type: String,
    default: 'Loading...',
  },
})

</script>
