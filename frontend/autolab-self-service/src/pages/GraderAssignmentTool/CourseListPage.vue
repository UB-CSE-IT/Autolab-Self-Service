<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to portal home" color="primary" :to="{name: 'index'}"/>
    </div>

    <h3>Grader Assignment Tool</h3>
    <h4 class="q-mb-sm">Your Courses</h4>

    <p>Here are the courses that have already been imported from Autolab. You can only view courses where you're an
      instructor or course assistant.</p>
    <ApiFetchContentContainer :api-data-loader="courseLoader" loading-text="Loading your courses">
      <BannerWithIcon theme="error" icon="error" v-if="courseLoader.state.data.length === 0">
        <p>You don't belong to any courses. You can import one from Autolab below.</p>
      </BannerWithIcon>
      <div v-else v-for="course in courseLoader.state.data" :key="course.name">
        <RouterLink :to="{name: 'grader-assignment-tool-course', params: {courseName: course.name}}">
          <div class="course-box">
            <p class="text-h5">{{ course.display_name }}</p>
            <p class="text-h6 subtext">({{ course.name }})</p>
          </div>
        </RouterLink>
      </div>
    </ApiFetchContentContainer>

    <h4 class="q-mb-sm">Import from Autolab</h4>
    <p>Here are the courses you're enrolled in on Autolab. You can import a course to the portal if you're an instructor
      or course assistant in it. This data is cached aggressively, so it may take a few minutes to update.</p>
    <ApiFetchContentContainer :api-data-loader="autolabCourseLoader" loading-text="Loading your Autolab courses">
      <BannerWithIcon theme="error" icon="error" v-if="autolabCourseLoader.state.data.length === 0">
        <p>You aren't in any courses on Autolab.</p>
      </BannerWithIcon>
      <div v-else v-for="course in autolabCourseLoader.state.data.courses" :key="course.name">
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
import BannerWithIcon from 'components/BannerWithIcon.vue'
import AutolabCourseListElement from 'components/AutolabCourseListElement.vue'

const courseLoader = new PortalApiDataLoader<GatCourse[]>('/portal/api/gat/my-courses/')
courseLoader.fetch()

const autolabCourseLoader = new PortalApiDataLoader<GatAutolabCoursesResponse>('/portal/api/gat/my-autolab-courses/')
autolabCourseLoader.fetch()

function courseImported(course: GatCourse) {
  courseLoader.state.data?.push(course)
}

</script>

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';

:deep(.course-box) {
  // Deep applies to subcomponents (AutolabCourseListElement)
  border: 2px solid $primary;
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

  &:hover {
    background-color: $hover;
  }

}
</style>
