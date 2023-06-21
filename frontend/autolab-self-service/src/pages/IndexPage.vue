<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>Welcome, {{ userStore.userData.firstName }}!</h3>
    <h6>What would you like to do today?</h6>

    <div class="flex">

      <div>
        <div class="autolab-card">
          <div class="header">
            Everybody
          </div>
          <a href="https://autolab.cse.buffalo.edu/">
            <div class="element" role="link" @click="navigate">
              Return to Autolab
            </div>
          </a>
          <div class="element">
            I wish there was something more fun to do than log out.
          </div>
          <div class="actions">
            <form method="POST" action="/portal/api/logout/">
              <q-btn label="Log out" color="primary" flat type="submit"/>
            </form>
          </div>
        </div>
      </div>

      <div>
        <div class="autolab-card">
          <div class="header">
            Instructors
          </div>
          <router-link :to="{name: 'create-course'}" v-slot="{ navigate }">
            <div class="element" role="link" @click="navigate">
              Create a course
            </div>
          </router-link>
          <!--          <div class="actions">-->
          <!--          </div>-->
        </div>
      </div>

      <div>
        <div class="autolab-card">
          <div class="header">
            Administrators
          </div>
          <router-link :to="{name: 'create-course'}" v-slot="{ navigate }">
            <div class="element" role="link" @click="navigate">
              Become an administrator
            </div>
          </router-link>
        </div>
      </div>

    </div>
  </q-page>
</template>

<script setup lang="ts">
import {useUserStore} from 'stores/UserStore';
import {useRouter} from "vue-router";

const userStore = useUserStore()

const router = useRouter()

</script>
