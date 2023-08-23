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

          <span class="q-ml-lg">
            <span v-if="totalCompleteGradingAssignmentsPerGrader[assignment.grader.email] ===
            totalGradingAssignmentsPerGrader[assignment.grader.email]"
                  class="text-green"
            >
              <q-icon class="q-mr-sm" name="done" size="28px"/>
              Complete! ({{ totalCompleteGradingAssignmentsPerGrader[assignment.grader.email] ?? 0 }})
            </span>
            <span v-else class="text-grey-8">
              {{ totalCompleteGradingAssignmentsPerGrader[assignment.grader.email] ?? 0 }} /
              {{ totalGradingAssignmentsPerGrader[assignment.grader.email] ?? 0 }}
            </span>
          </span>
        </h5>

        <q-markup-table>
          <thead>
          <tr style="text-align: left"
              class="transition-colors"
              :class="{'bg-grey': totalCompleteGradingAssignmentsPerGrader[assignment.grader.email]
                  === totalGradingAssignmentsPerGrader[assignment.grader.email]}"
          >
            <th>Student Name</th>
            <th>Student Email</th>
            <th>Autolab Link</th>
            <th>Complete</th>
          </tr>
          </thead>
          <tbody>
          <GradingAssignmentPairRow v-for="pair in assignment.submissions"
                                    :key="pair.pair_id"
                                    :pair="pair"
                                    :assignment="assignmentLoader.state.data?.grading_assignment"
                                    @complete-updated="gradingAssignmentPairUpdated(pair, $event)"
          />
          </tbody>
        </q-markup-table>

      </template>
    </ApiFetchContentContainer>

    <div style="height: 200px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import {
  GatGradingAssignmentPairSubmission,
  GatGradingAssignmentResponse,
} from 'src/types/GradingAssignmentToolTypes'
import YouBadge from 'components/YouBadge.vue'
import {useUserStore} from 'stores/UserStore'
import GradingAssignmentListElement from 'components/GraderAssignmentTool/GradingAssignmentListElement.vue'
import GradingAssignmentPairRow from 'components/GraderAssignmentTool/GradingAssignmentPairRow.vue'
import {computed} from 'vue'

const courseName = useRoute().params.courseName
const assignmentId = useRoute().params.assignmentId
const currentUserEmail = useUserStore().userData.email

const totalGradingAssignmentsPerGrader = computed(() => {
  const map: { [key: string]: number } = {}
  for (const graderSubmissions of assignmentLoader.state.data?.grading_assignment_pairs ?? []) {
    map[graderSubmissions.grader.email] = graderSubmissions.submissions.length
  }
  return map
})

const totalCompleteGradingAssignmentsPerGrader = computed(() => {
  const map: { [key: string]: number } = {}
  for (const graderSubmissions of assignmentLoader.state.data?.grading_assignment_pairs ?? []) {
    map[graderSubmissions.grader.email] = graderSubmissions.submissions
        .filter((submission: GatGradingAssignmentPairSubmission) => submission.completed)
        .length
  }
  return map
})


const assignmentLoader = new PortalApiDataLoader<GatGradingAssignmentResponse>(`/portal/api/gat/course/${courseName}/grading-assignments/${assignmentId}/`)
assignmentLoader.fetch()

function gradingAssignmentPairUpdated(pair: GatGradingAssignmentPairSubmission, complete: boolean) {
  pair.completed = complete
}

</script>
