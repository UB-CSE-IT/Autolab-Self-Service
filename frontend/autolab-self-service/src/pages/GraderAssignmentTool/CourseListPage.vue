<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to portal home" color="primary" :to="{name: 'index'}"/>
      <q-btn icon="description" label="Read the Docs" color="primary"
             href="https://napps.cse.buffalo.edu/docs/autolab/Grader%20Assignment%20Tool"
             target="_blank"/>
    </div>

    <h3>Grader Assignment Tool</h3>
    <h4 class="q-mb-sm">Your Courses</h4>

    <p>Here are the courses that have already been imported from Autolab. You can only view courses where you're an
      instructor or course assistant.</p>
    <ApiFetchContentContainer :api-data-loader="courseLoader" loading-text="Loading your courses">
      <InfoBox v-if="courseLoader.state.data?.length === 0">
        <p>You don't belong to any courses using the Grader Assignment Tool. You may be able to import one from Autolab
          below.</p>
      </InfoBox>


      <div class="flex" v-else>
        <div v-for="course in courseLoader.state.data" :key="course.name">
          <RouterLink :to="{name: 'grader-assignment-tool-course', params: {courseName: course.name}}">
            <div class="autolab-card">
              <div class="header">
                {{ course.display_name }}
              </div>
              <div class="element text-black">
                ({{ course.name }})
              </div>
              <div class="actions">
                <q-btn label="Open" flat/>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>

    </ApiFetchContentContainer>

    <ApiFetchContentContainer :api-data-loader="autolabCourseLoader" loading-text="Loading your Autolab courses">
      <template #before-load>
        <q-btn
            class="q-mt-xl"
            v-if="!autolabCourseLoader.state.loaded"
            label="Import from Autolab"
            color="primary"
            @click="autolabCourseLoader.fetch()"
            icon="download"
        />
      </template>

      <h4 class="q-mb-sm">Import from Autolab</h4>
      <p>Here are the courses you're enrolled in on Autolab. You can import a course to the portal if you're an
        instructor or course assistant in it. This data is cached, so it may take a few minutes to update.</p>
      <InfoBox v-if="autolabCourseLoader.state.data?.courses.length === 0">
        <p>You aren't enrolled in any courses on Autolab.</p>
      </InfoBox>
      <div
          class="q-mb-md"
          v-else
          v-for="course in autolabCourseLoader.state.data?.courses"
          :key="course.name"
      >
        <AutolabCourseListElement @courseImported="courseImported" :course="course"/>
      </div>
    </ApiFetchContentContainer>

    <div style="height: 200px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import {GatAutolabCoursesResponse, GatCourse} from 'src/types/GradingAssignmentToolTypes'
import AutolabCourseListElement from 'components/GraderAssignmentTool/AutolabCourseListElement.vue'
import InfoBox from 'components/Boxes/InfoBox.vue'

const courseLoader = new PortalApiDataLoader<GatCourse[]>('/portal/api/gat/my-courses/')
courseLoader.fetch()

const autolabCourseLoader = new PortalApiDataLoader<GatAutolabCoursesResponse>('/portal/api/gat/my-autolab-courses/')

function courseImported(course: GatCourse) {
  courseLoader.state.data?.push(course)
}

</script>

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';

:deep(.course-box) {
  // Deep applies to subcomponents (AutolabCourseListElement)
  border: 1px solid $primary;
  border-left: 12px solid $primary;
  border-radius: 8px;
  padding: 16px;
  margin: 8px 0;
  color: black;

  p {
    margin: 0;
  }

  .subtext {
    color: gray;
  }
}
</style>
