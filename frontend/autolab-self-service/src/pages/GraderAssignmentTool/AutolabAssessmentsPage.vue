<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">

    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to course" color="primary" :to="{name: 'grader-assignment-tool-course'}"/>
    </div>

    <ApiFetchContentContainer :api-data-loader="assessmentsLoader" loading-text="Loading Autolab assessments">
      <h4>{{ assessmentsLoader.state.data.course.display_name }} Assessments</h4>
      <h5 class="q-mb-sm">Create a New Grading Assignment</h5>
      <p>Choose an assessment from Autolab to generate a grading assignment based on the current roster.</p>

      <BannerWithIcon v-if="assessmentsLoader.state.data?.assessments.length === 0" icon="info">
        This course doesn't have any Autolab assessments yet.
      </BannerWithIcon>

      <q-markup-table v-else>
        <thead>
        <tr style="text-align: left">
          <th>Assessment Name</th>
          <th>Autolab Link</th>
          <th>Action</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="assessment in assessmentsLoader.state.data?.assessments" :key="assessment.name">
          <td>{{ assessment.display_name }}</td>
          <td><a target="_blank" :href="assessment.url">{{ assessment.name }}</a></td>
          <td>
            <RouterLink
              :to="{name: 'grader-assignment-tool-create-new-assignment', params: {assessmentName: assessment.name}}">
              Create
            </RouterLink>
          </td>
        </tr>
        </tbody>
      </q-markup-table>
    </ApiFetchContentContainer>
    <div style="height: 200px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import {GatAutolabAssessmentsResponse} from 'src/types/GradingAssignmentToolTypes'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import BannerWithIcon from 'components/BannerWithIcon.vue'

const courseName = useRoute().params.courseName

const assessmentsLoader = new PortalApiDataLoader<GatAutolabAssessmentsResponse>(`/portal/api/gat/course/${courseName}/autolab-assessments/`)
assessmentsLoader.fetch()

</script>
