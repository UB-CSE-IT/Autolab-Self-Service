<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="row items-center full-width">
      <h3 class="row"><span>Welcome,&nbsp;</span><span v-if="!editName">{{ userStore.userData.firstName }}!
        <span>
          <q-btn v-if="!editName"
                 class="q-ml-sm"
                 dense
                 size="12px"
                 flat
                 color="primary"
                 icon="edit"
                 aria-label="Edit name"
                 @click="editName = !editName"/>
        </span>
        </span>
      </h3>
      <PreferredNameBox v-if="editName" :shown="editName" @close="editName=false"/>
    </div>
    <h6>What would you like to do today?</h6>

    <div class="flex">

      <div>
        <div class="autolab-card">
          <div class="header">
            Everybody
          </div>
          <router-link :to="{name: 'tango-statistics'}" v-slot="{ navigate }">
            <div class="element" role="link" @click="navigate">
              View Tango Statistics
            </div>
          </router-link>
          <div class="actions">
            <q-btn href="/" label="Return to Autolab" color="primary" flat/>
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
              Create a Course
            </div>
          </router-link>
          <router-link :to="{name: 'grader-assignment-tool'}" v-slot="{ navigate }">
            <div class="element" role="link" @click="navigate">
              Grader Assignment Tool (GAT)
            </div>
          </router-link>
          <router-link :to="{name: 'course-sections'}" v-slot="{ navigate }">
            <div class="element" role="link" @click="navigate">
              Manage Course Sections
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
          <router-link :to="{name: 'become-admin'}" v-slot="{ navigate }">
            <div class="element" role="link" @click="navigate">
              Become an Administrator
            </div>
          </router-link>
        </div>
      </div>

    </div>
  </q-page>
</template>

<script setup lang="ts">
import {useUserStore} from 'stores/UserStore'
import PreferredNameBox from 'components/PreferredNameBox.vue'
import {ref} from 'vue'

const userStore = useUserStore()
const editName = ref(false)

</script>
