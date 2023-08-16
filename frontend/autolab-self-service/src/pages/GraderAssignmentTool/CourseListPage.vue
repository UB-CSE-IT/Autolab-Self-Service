<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>Grader Assignment Tool</h3>

    <ApiFetchContentContainer :api-data-loader="courseLoader" loading-text="Loading your courses">
      <h4 class="q-mb-sm">Your Courses</h4>
      <p>These courses have already been imported from Autolab.</p>
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

  </q-page>
</template>

<script setup lang="ts">
import {PortalApiDataLoader} from "src/utilities/PortalApiDataLoader"
import ApiFetchContentContainer from "components/ApiFetchContentContainer.vue"
import {GradingAssignmentToolCourse} from "src/types/GradingAssignmentToolTypes";
import BannerWithIcon from "components/BannerWithIcon.vue";

const courseLoader = new PortalApiDataLoader<GradingAssignmentToolCourse[]>('/portal/api/gat/my-courses/')
courseLoader.fetch()
</script>

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';

.course-box {
  border: 2px solid $primary;
  border-radius: 8px;
  padding: 16px;
  margin: 8px 0;
  color: $primary;

  p {
    margin: 0;
  }

  .subtext {
    color: gray;
  }

  &:hover {
    background-color: #eef5ff;
  }

}
</style>
