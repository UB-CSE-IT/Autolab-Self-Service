<template>
  <router-view />
</template>

<script setup lang="ts">
import {useUserStore} from "stores/user-store";

const userStore = useUserStore()
userStore.loadUserData()
</script>
