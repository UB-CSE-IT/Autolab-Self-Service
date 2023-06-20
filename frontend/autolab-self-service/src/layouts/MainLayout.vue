<template>
  <q-layout view="hHh lpR fFf">

    <q-header class="bg-primary text-white" height-hint="98">
      <q-toolbar align="center">
        <q-toolbar-title>
          <q-avatar>
            <img src="/portal/icons/autolab.svg" alt="Autolab Logo">
          </q-avatar>
          Autolab Self-Service Portal
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view v-if="userStore.loggedIn"/>
      <div v-else>
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
        </q-page>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import {useUserStore} from "stores/user-store";

const userStore = useUserStore()
</script>
