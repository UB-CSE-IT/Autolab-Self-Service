<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>Create an Autolab Course</h3>

    <div v-if="userStore.userData.isAdmin" class="admin-info">
      <p>As an admin, you can manage courses for any instructor.</p>
      <q-form @submit="loadCourses">
        <q-input v-model="state.username" label="Instructor username">
          <q-btn icon="east" color="primary" type="submit"/>
        </q-input>
      </q-form>
      {{ state }}
    </div>

    <div v-if="state.loadingCourses">
      Loading...
    </div>
    <div v-else-if="state.errorLoadingCourses">
      Error loading courses: {{ state.errorMessage }}
    </div>
    <div v-else>
      <div v-if="state.stage === 0">
        <h4>Step 1: Choose a Course</h4>
        <p>Here are all the current and upcoming courses you're scheduled to teach. If you don't see the course you'd
          like, <a target="_blank" href="https://autolab.cse.buffalo.edu/contact">contact us</a> to create a custom one
        </p>

        <div class="flex">

          <div v-for="course in state.data.data.courses" :key="course.uniqueIdentifier">
            <div class="autolab-card">
              <div class="header">
                {{ course.suggestedName }}
              </div>
              <div class="element">
                {{ course.term }}
              </div>
              <div class="element">
                "{{ course.technicalName }}"
              </div>
              <div class="actions">
                <q-btn label="Create this course" color="white" text-color="primary" flat @click="state.stage = 1"/>
              </div>

            </div>

          </div>

        </div>


      </div>

    </div>


  </q-page>
</template>

<script setup lang="ts">
import {reactive, ref} from 'vue';
import {useUserStore} from 'stores/UserStore';
import {MyCoursesResponse} from "src/types/MyCoursesResponse";

const userStore = useUserStore()

// Stage 0 is picking the course, 1 is choosing the name, 2 is the final confirmation

const state = reactive({
  stage: 0,
  data: [] as MyCoursesResponse[],
  loadingCourses: false,
  errorLoadingCourses: false,
  errorMessage: '',
  // username: userStore.userData.username,
  username: "hartloff",  // TODO remove after debugging
})

function loadCourses() {
  // fetch(`/portal/api/my-courses/${state.username}/`)
  state.stage = 0
  state.data = [] as MyCoursesResponse[]
  state.loadingCourses = true
  state.errorLoadingCourses = false
  state.errorMessage = ''
  fetch(`/portal/api/my-courses/${state.username}/`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        state.data = data;
        state.loadingCourses = false
      } else {
        return Promise.reject(data)
      }
    })
    .catch(error => {
      state.errorLoadingCourses = true
      state.loadingCourses = false
      state.errorMessage = error.error
    })
}

loadCourses()

</script>

<style scoped lang="scss">
.admin-info {
  border-left: 6px solid $admin;
  border-right: 6px solid $admin;
  background: $admin-bg;
  padding: 15px;
  border-radius: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
}

.autolab-card {
  margin: 30px;
  width: 400px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
  transition-duration: .3s;
}

.autolab-card:hover {
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

.autolab-card > .header {
  background: $primary;
  color: white;
  font-size: 24px;
  padding: 20px;
}

.autolab-card > .element {
  padding: 10px 20px;
  border-bottom: 1px solid lightgray;
}

.autolab-card > .element:hover {
  background-color: lightgray;
}

.autolab-card > .actions {
  padding: 10px;
}

</style>
