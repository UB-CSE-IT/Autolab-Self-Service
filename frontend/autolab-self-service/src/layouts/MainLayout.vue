<template>
  <q-layout view="hHh lpR fff">

    <q-header class="text-white" :class="headerClass" height-hint="98">
      <q-toolbar class="flex column content-center justify-center">
        <q-btn flat to="/" no-caps>
          <q-toolbar-title>
            <q-avatar>
              <img src="/portal/icons/autolab.svg" alt="Autolab Logo">
            </q-avatar>
            Autolab Portal{{ userStore.developerMode ? ' (Developer Mode)' : '' }}
          </q-toolbar-title>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view class="q-py-sm" v-if="userStore.loggedIn"/>
      <LoginPanel v-else/>
    </q-page-container>

    <q-footer class="bg-primary text-white q-mt-lg q-pa-md">
      <div class="flex justify-end">
        <div class="q-mx-lg">UB CSE Autolab Portal
          <span v-if="userStore.version !== undefined"> v. {{ userStore.version }}</span></div>
      </div>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import {useUserStore} from 'stores/UserStore'
import 'src/css/portal.scss'
import {computed} from 'vue'
import LoginPanel from 'layouts/LoginPanel.vue'

const userStore = useUserStore()

const headerClass = computed(() => {
  if (userStore.developerMode) {
    return 'bg-red-10'
  } else {
    return 'bg-primary'
  }
})

</script>
