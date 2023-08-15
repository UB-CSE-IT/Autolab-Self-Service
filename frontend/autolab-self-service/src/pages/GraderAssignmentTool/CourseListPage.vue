<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>GAT Course List</h3>

    <p>TODO: Show current courses, offer to show Autolab courses to create a new one</p>

    <q-btn @click="loadMyCourses" label="Load My Courses"/>
    {{ courseLoader.state }}

    <ApiFetchContentContainer :api-data-loader="courseLoader" loading-text="Loading your courses">
      Content:
      {{courseLoader.state.data}}
      <div v-for="course in courseLoader.state.data" :key="course.name">
        {{ course.name }}
      </div>
    </ApiFetchContentContainer>

  </q-page>
</template>

<script setup lang="ts">

import {PortalApiDataLoader} from "src/utilities/PortalApiDataLoader"
import ApiFetchContentContainer from "components/ApiFetchContentContainer.vue"

const courseLoader = new PortalApiDataLoader('/portal/api/gat/my-courses/')

function loadMyCourses() {
  courseLoader.fetch()
  console.log(courseLoader.state)
}


</script>
