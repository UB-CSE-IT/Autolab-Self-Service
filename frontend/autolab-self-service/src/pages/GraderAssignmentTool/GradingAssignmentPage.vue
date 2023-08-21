<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to course" color="primary" :to="{name: 'grader-assignment-tool-course'}"/>
    </div>

    <ApiFetchContentContainer :api-data-loader="assignmentLoader" loading-text="Loading grading assignments">


      <h4>{{ assignmentLoader.state.data.grading_assignment.course.display_name }} Grading Assignment</h4>

      <GradingAssignmentListElement
          v-if="assignmentLoader.state.data?.grading_assignment"
          :grading-assignment="assignmentLoader.state.data.grading_assignment"
          :detail="true"
          :show-archive-checkbox="true"
      />

      <template
          v-for="assignment in assignmentLoader.state.data?.grading_assignment_pairs"
          :key="assignment.grader.email"
      >
        <h5>{{ assignment.grader.display_name }}
          <YouBadge v-if="currentUserEmail === assignment.grader.email"/>
        </h5>

        <p>Assigned {{ assignment.submissions }}</p>


      </template>
    </ApiFetchContentContainer>

    <div style="height: 200px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import {GatGradingAssignmentResponse} from 'src/types/GradingAssignmentToolTypes'
import YouBadge from 'components/YouBadge.vue'
import {useUserStore} from 'stores/UserStore'
import GradingAssignmentListElement from 'components/GraderAssignmentTool/GradingAssignmentListElement.vue'

const courseName = useRoute().params.courseName
const assignmentId = useRoute().params.assignmentId
const currentUserEmail = useUserStore().userData.email

const assignmentLoader = new PortalApiDataLoader<GatGradingAssignmentResponse>(`/portal/api/gat/course/${courseName}/grading-assignments/${assignmentId}/`)
assignmentLoader.fetch()

</script>
