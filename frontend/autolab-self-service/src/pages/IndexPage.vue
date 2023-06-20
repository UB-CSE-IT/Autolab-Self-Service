<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>Welcome, {{ userStore.userData.firstName }}!</h3>
    <h6>What would you like to do today?</h6>

    <form method="POST" action="/portal/api/logout/">
      <q-btn label="Log out" color="primary" type="submit"/>
    </form>

  </q-page>
</template>

<script setup lang="ts">
import {ref} from "vue";
import {useUserStore} from "stores/user-store";

const userStore = useUserStore()

const todos = ref<Todo[]>([
  {
    id: 1,
    content: 'ct1'
  },
  {
    id: 2,
    content: 'ct2'
  },
  {
    id: 3,
    content: 'ct3'
  },
  {
    id: 4,
    content: 'ct4'
  },
  {
    id: 5,
    content: 'ct5'
  }
]);
const meta = ref<Meta>({
  totalCount: 1200
});
</script>
