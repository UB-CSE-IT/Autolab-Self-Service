<template>
  <BannerWithIcon v-if="userStore.developerMode" icon="developer_mode" theme="debug">
    <slot/>
    <p class="q-pt-sm text-italic text-grey-8">* This is only displayed in developer mode.</p>
  </BannerWithIcon>
</template>

<script setup lang="ts">
import BannerWithIcon from 'components/BannerWithIcon.vue'
import {useUserStore} from 'stores/UserStore'

const userStore = useUserStore()

</script>
