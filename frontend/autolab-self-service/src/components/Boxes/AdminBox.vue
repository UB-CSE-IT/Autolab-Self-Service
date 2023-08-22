<template>
  <BannerWithIcon v-if="userStore.userData.isAdmin || userStore.developerMode" icon="shield" theme="admin">
    <slot style="width: 100%;"/>
    <p class="q-pt-sm text-italic text-grey-8">* Only administrators can see this.
      <span v-if="userStore.developerMode && !userStore.userData.isAdmin">
        Although you're not an administrator, developer mode is enabled, so you can see it too.
      </span>
    </p>
  </BannerWithIcon>
</template>

<script setup lang="ts">
import BannerWithIcon from 'components/BannerWithIcon.vue'
import {useUserStore} from 'stores/UserStore'

const userStore = useUserStore()
</script>
