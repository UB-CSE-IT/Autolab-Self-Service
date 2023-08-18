<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">

    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to Autolab Assessments" color="primary"
             :to="{name: 'grader-assignment-tool-autolab-assessments'}"/>
    </div>

    <template v-if="confirmed">
      <ApiFetchContentContainer :api-data-loader="createAssessmentLoader" loading-text="Creating grading assignment">
        <h4 class="q-mb-sm">Success!</h4>
        <p>Here's your new grading assignment.</p>

        <GradingAssignmentListElement
            v-if="createAssessmentLoader.state.data"
            :grading-assignment="createAssessmentLoader.state.data.grading_assignment"
        />
      </ApiFetchContentContainer>
    </template>
    <template v-else>
      <h4>Confirmation</h4>
      <p>Please confirm you want to create a new grading assignment for "<b>{{ assessmentName }}</b>".</p>
      <q-btn label="Confirm" icon="check" color="primary" @click="confirm"/>
    </template>

    <div style="height: 200px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import {GatCreateGradingAssignmentResponse} from 'src/types/GradingAssignmentToolTypes'
import {ref} from 'vue'
import GradingAssignmentListElement from 'components/GraderAssignmentTool/GradingAssignmentListElement.vue'

const courseName = useRoute().params.courseName
const assessmentName = useRoute().params.assessmentName
const confirmed = ref(false)

const createAssessmentLoader = new PortalApiDataLoader<GatCreateGradingAssignmentResponse>(`/portal/api/gat/course/${courseName}/create-grading-assignment/${assessmentName}/`, 'POST')

function confirm() {
  confirmed.value = true
  createAssessmentLoader.fetch()
}

</script>
