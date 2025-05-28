<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to portal home" color="primary" to="/"/>
      <q-btn icon="description" label="Read the Docs" color="primary"
             href="https://napps.cse.buffalo.edu/docs/autolab/UB%20course%20sections"
             target="_blank"/>
    </div>
    <h3>Manage Course Sections</h3>
    <p>Choose one of your Autolab courses to manage lecture and section times. You must be an
      instructor in the course to use this feature.</p>

    <ApiFetchContentContainer :api-data-loader="autolabCourseLoader" loading-text="Loading your Autolab courses">
      <ul>
        <li v-for="course in autolabCourseLoader.state.data?.courses" :key="course.name">
          <RouterLink :to="{name: 'course-sections-course', params: {courseName: course.name}}">
            {{ course.display_name }} ({{ course.name }})
          </RouterLink>
        </li>
      </ul>
    </ApiFetchContentContainer>

    <div style="height: 100px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import {GatAutolabCoursesResponse} from 'src/types/GradingAssignmentToolTypes'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'

const autolabCourseLoader = new PortalApiDataLoader<GatAutolabCoursesResponse>('/portal/api/gat/my-autolab-courses/')
autolabCourseLoader.fetch()

</script>
