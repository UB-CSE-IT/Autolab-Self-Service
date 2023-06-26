<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div v-if="userStore.userDataLoading"
         class="absolute-center">
      <q-spinner-gears class="q-mb-lg" color="primary" size="100"/>
      <p>Loading profile</p>
    </div>
    <div v-else class="column items-center content-center">
      <h4>Welcome!</h4>
      <h5>You need to sign in to continue</h5>
      <form method="POST" action="/portal/api/login/">
        <q-btn label="Sign in with Shibboleth" color="primary" type="submit"/>
      </form>
    </div>
    <div v-if="userStore.developerMode">
      <q-banner class="q-my-lg bg-red-10 text-white">
        <template v-slot:avatar>
          <q-icon name="developer_mode"/>
        </template>
        Developer mode is enabled! This should not be running in production!
      </q-banner>

      <h4>Sign in as anybody</h4>
      <form method="post" action="/portal/api/login/dev/">
        <label>
          Username
          <input name="username" label="Username" type="text"/>
        </label>
        <button type="submit">Log in</button>
      </form>

    </div> <!-- End of developer mode options -->
  </q-page>
</template>


<script setup lang="ts">
import {useUserStore} from 'stores/UserStore';

const userStore = useUserStore()

</script>
