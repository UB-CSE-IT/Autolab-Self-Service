<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to courses" color="primary" :to="{name: 'grader-assignment-tool'}"/>
    </div>

    <ApiFetchContentContainer :api-data-loader="courseLoader" loading-text="Loading course details">
      <h4>{{ courseLoader.state.data.course.display_name }}</h4>
      <div class="button-row q-my-lg">
        <q-btn icon="add" label="Create New Grading Assignment" color="primary"
               :to="{name: 'grader-assignment-tool-autolab-assessments'}"/>
      </div>
      <div class="button-row q-my-lg">
        <q-btn icon="people" label="Manage People" color="secondary" :to="{name: 'grader-assignment-tool-people'}"/>
        <q-btn icon="sports_martial_arts" label="My Conflicts of Interest" color="secondary"
               :to="{name: 'grader-assignment-tool-person', params: {user: userStore.userData.email}}"/>
        <q-btn icon="open_in_new" label="Open in Autolab" color="secondary"
               :href="`/courses/${courseLoader.state.data?.course.name}`"
               target="_blank"/>
      </div>

      <h5 class="q-mb-sm">Grading Assignments</h5>

      <div v-if="courseLoader.state.data?.grading_assignments.length === 0">
        <BannerWithIcon icon="sentiment_dissatisfied">
          <p>No grading assignments have been created yet.</p>
        </BannerWithIcon>
      </div>

      <template v-else>
        <p>Showing {{ shownAssignments.length }} of {{ allAssignments.length }} assignments</p>

        <q-checkbox
            v-model="showArchived"
            label="Show archived grading assignments"
            class="q-mb-lg"
        />

        <div v-if="shownAssignments.length === 0" class="q-mt-sm">
          <BannerWithIcon icon="archive">
            <p>All grading assignments have been archived.</p>
          </BannerWithIcon>
        </div>

        <template v-for="assignment in shownAssignments">
          <RouterLink
              v-if="!assignment.archived || showArchived"
              :key="assignment.id"
              :to="{name: 'grader-assignment-tool-assignment', params: {assignmentId: assignment.id}}"
          >
            <GradingAssignmentListElement :grading-assignment="assignment"/>
          </RouterLink>
        </template>
      </template>
    </ApiFetchContentContainer>

    <div style="height: 200px;"></div>
  </q-page>
</template>

<script setup lang="ts">

import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import {GatGradingAssignment, GatGradingAssignmentsResponse} from 'src/types/GradingAssignmentToolTypes'
import {useUserStore} from 'stores/UserStore'
import GradingAssignmentListElement from 'components/GraderAssignmentTool/GradingAssignmentListElement.vue'
import BannerWithIcon from 'components/BannerWithIcon.vue'
import {computed, ref} from 'vue'

const courseName = useRoute().params.courseName
const userStore = useUserStore()
const showArchived = ref(false)
const shownAssignments = computed(() => {
  return courseLoader.state.data?.grading_assignments.filter((assignment: GatGradingAssignment) => {
    return !assignment.archived || showArchived.value
  })
})
const allAssignments = computed(() => {
  return courseLoader.state.data?.grading_assignments ?? []
})

const courseLoader = new PortalApiDataLoader<GatGradingAssignmentsResponse>(`/portal/api/gat/course/${courseName}/grading-assignments/`)
courseLoader.fetch()

</script>
