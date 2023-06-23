<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>Become an Admin</h3>
    <q-btn icon="west" label="Back to portal home" color="primary" to="/"/>

    <p class="q-mt-lg">If you're a system-wide administrator on Autolab, you can sync that status to the self-service
      portal.</p>

    <div v-if="userStore.userData.isAdmin">
      <h5 class="text-green">
        <q-icon name="sentiment_satisfied"/>
        The front-end believes you're already an administrator.
      </h5>
    </div>
    <div v-else>
      <h5 class="text-red">
        <q-icon name="sentiment_dissatisfied"/>
        The front-end believes you're not an administrator.
      </h5>
    </div>

    <q-btn label="Sync admin status!" color="primary" @click="syncAdminStatus"/>

    <div v-if="state.loading">
      <q-spinner-pie class="q-mt-lg" size="100"/>
    </div>
    <div v-else-if="state.error">
      <h4 class="text-red">
        <q-icon name="sentiment_dissatisfied"/>
        Admin Sync Failed!
      </h4>
      <p>{{ state.message }}</p>
    </div>
    <div v-else-if="state.success">
      <h4 class="text-green">
        <q-icon name="sentiment_satisfied"/>
        Admin Sync Successful!
      </h4>
      <p>{{ state.message }}</p>
    </div>


    <div style="height: 100px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {reactive} from 'vue';
import {useUserStore} from 'stores/UserStore';
import {useRouter} from "vue-router";

const userStore = useUserStore()
const router = useRouter()

// Stage 0 is picking the course, 1 is choosing the name, 2 is the final confirmation, 3 is after confirmation

const state = reactive({
  loading: false,
  error: false,
  success: false,
  message: '',
})

function syncAdminStatus() {
  state.loading = true
  fetch('/portal/api/admin-update/', {
    method: 'POST',
  }).then(resp => resp.json())
    .then(data => {
      if (data.success) {
        state.error = false
        state.success = true
        state.message = data.message
        if (data.isAdmin !== undefined) {
          userStore.userData.isAdmin = data.isAdmin
        }
      } else {
        state.error = true
        state.success = false
        state.message = data.error
      }
    })
    .finally(() => {
      state.loading = false
    })
}


</script>

<style scoped>


</style>
