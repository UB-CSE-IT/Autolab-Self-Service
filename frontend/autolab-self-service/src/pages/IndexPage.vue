<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>Welcome, {{ userStore.userData.firstName }}!</h3>
    <h6>What would you like to do today?</h6>

    <q-btn label="Create a course" color="primary" :to="{name: 'create-course'}"/>

    <form method="POST" action="/portal/api/logout/">
      <q-btn label="Log out" color="primary" type="submit"/>
    </form>

  </q-page>
</template>

<script setup lang="ts">
import {useUserStore} from 'stores/UserStore';

const userStore = useUserStore()

</script>
