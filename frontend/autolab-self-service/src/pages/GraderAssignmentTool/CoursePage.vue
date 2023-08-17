<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to courses" color="primary" :to="{name: 'grader-assignment-tool'}"/>
    </div>

    <ApiFetchContentContainer :api-data-loader="courseLoader" loading-text="Loading course details">
      <h4>{{ courseLoader.state.data.course.display_name }}</h4>
      <div class="button-row q-my-lg">
        <q-btn icon="add" label="Create New Grading Assignment" color="primary"
               :to="{name: 'grader-assignment-tool-new-assignment'}"/>
        <q-btn icon="people" label="Manage People" color="secondary" :to="{name: 'grader-assignment-tool-people'}"/>
        <q-btn icon="sports_martial_arts" label="My Conflicts of Interest" color="secondary"
               :to="{name: 'grader-assignment-tool-person', params: {user: userStore.userData.email}}"/>
      </div>

      <h5>Grading Assignments</h5>

      <GradingAssignmentListElement :grading-assignment="assignment"
                                    v-for="assignment in courseLoader.state.data.grading_assignments"
                                    :key="assignment.id"/>

      <div v-if="courseLoader.state.data.grading_assignments.length === 0">
        <BannerWithIcon icon="sentiment_dissatisfied">
          <p>No grading assignments have been created yet.</p>
        </BannerWithIcon>
      </div>

    </ApiFetchContentContainer>
    <div style="height: 200px;"></div>

  </q-page>
</template>

<script setup lang="ts">

import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import {GatGradingAssignmentsResponse} from 'src/types/GradingAssignmentToolTypes'
import {useUserStore} from 'stores/UserStore'
import GradingAssignmentListElement from 'components/GraderAssignmentTool/GradingAssignmentListElement.vue'
import BannerWithIcon from 'components/BannerWithIcon.vue'

const courseName = useRoute().params.courseName
const userStore = useUserStore()

const courseLoader = new PortalApiDataLoader<GatGradingAssignmentsResponse>(`/portal/api/gat/course/${courseName}/grading-assignments/`)
courseLoader.fetch()

</script>
