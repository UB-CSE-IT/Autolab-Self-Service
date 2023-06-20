<template>
  <router-view />
</template>

<script setup lang="ts">
import {useUserStore} from 'stores/UserStore';

const userStore = useUserStore()
userStore.loadUserData()
</script>
