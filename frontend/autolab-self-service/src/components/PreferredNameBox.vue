<template>
  <form @submit.prevent="savePreferredName">

    <q-input style="max-width: 400px; min-width: 200px;"
             maxlength="30"
             class="text-h3"
             v-model="preferredName"
             autofocus>
      <template v-slot:after>
        <q-btn dense
               flat
               color="primary"
               icon="done"
               aria-label="Save"
               :loading="preferredNameUpdater.state.loading"
               @click="savePreferredName"/>
        <q-btn dense
               flat
               color="red"
               icon="close"
               aria-label="Cancel"
               @click="cancel"/>
      </template>
    </q-input>
  </form>

  <ErrorBox class="full-width" v-if="preferredNameUpdater.state.error">
    {{ preferredNameUpdater.state.error }}
  </ErrorBox>
</template>

<script setup lang="ts">

import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import {UserData} from 'src/types/UserData'
import {ref} from 'vue'
import {useUserStore} from 'stores/UserStore'
import ErrorBox from 'components/Boxes/ErrorBox.vue'

const emits = defineEmits(['close'])
const props = defineProps(
    {
      shown:
          {
            type: Boolean,
            required: true,
          },
    },
)

const userStore = useUserStore()
const preferredNameUpdater = new PortalApiDataLoader<UserData>('/portal/api/userinfo/preferred-name/', 'POST')

const preferredName = ref('')
resetPreferredName()

function resetPreferredName() {
  preferredName.value = userStore.userData.firstName
}

function savePreferredName() {
  preferredNameUpdater.fetch({preferredName: preferredName.value})
      .then(() => {
        if (!preferredNameUpdater.state.error && preferredNameUpdater.state.data) {
          userStore.updateName(preferredNameUpdater.state.data.firstName)
          emits('close')
        }
      })
}

function cancel() {
  resetPreferredName()
  emits('close')
}

</script>

<style scoped lang="scss">

</style>
