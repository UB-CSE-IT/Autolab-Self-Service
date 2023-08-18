<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to people" color="primary" :to="{name: 'grader-assignment-tool-people'}"/>
    </div>

    <ApiFetchContentContainer :api-data-loader="personLoader" loading-text="Loading person details">

      <h4 class="q-mb-sm">{{ personLoader.state.data.user.display_name }}</h4>
      <p class="text-h5 text-grey-8"> {{ state.isGrader ? 'Grader' : 'Student' }} in
        {{ personLoader.state.data.course.display_name }}
      </p>

      <q-markup-table>
        <thead>
        <tr style="text-align: left">
          <th>Name</th>
          <th>Email Address</th>
          <th v-if="personLoader.state.data?.user.is_grader">Hours</th>
        </tr>
        </thead>
        <tbody>
        <PersonRow v-if="personLoader.state.data"
                   :user="personLoader.state.data.user"
                   :show-hours="personLoader.state.data?.user.is_grader"
                   :show-conflicts="false"
        />
        </tbody>
      </q-markup-table>

      <ApiFetchContentContainer :api-data-loader="peopleLoader" loading-text="Loading conflicts of interest">
        <h5 class="q-mb-sm">Conflicts of Interest</h5>
        <p>Please checkmark the {{ !state.isGrader ? 'graders' : 'students' }} who have a
          conflict of interest with this {{ state.isGrader ? 'grader' : 'student' }}.</p>

        <q-markup-table>
          <thead>
          <tr style="text-align: left">
            <th>Name</th>
            <th>Email Address</th>
            <th>Conflict with {{ personLoader.state.data.user.display_name }}</th>
          </tr>
          </thead>
          <tbody>
          <template v-if="personLoader.state.data && peopleLoader.state.data">
            <ConflictOfInterestRow
              v-for="user in state.roster" :key="user.email"
              :current-user="personLoader.state.data.user"
              :course="personLoader.state.data.course"
              :target-user="user"
              :initially-conflict-of-interest="state.conflictsOfInterest.includes(user.email)"
            />
          </template>
          </tbody>
        </q-markup-table>
      </ApiFetchContentContainer>
    </ApiFetchContentContainer>

    <div style="height: 200px;"></div>

  </q-page>
</template>

<script setup lang="ts">

import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import {GatCoursePersonResponse, GatCourseUser, GatCourseUsersResponse} from 'src/types/GradingAssignmentToolTypes'
import {useRoute} from 'vue-router'
import {reactive} from 'vue'
import ConflictOfInterestRow from 'components/GraderAssignmentTool/ConflictOfInterestRow.vue'
import PersonRow from 'components/GraderAssignmentTool/PersonRow.vue'

const courseName = useRoute().params.courseName
const userEmailAddress = useRoute().params.user
const state = reactive({
  roster: [] as GatCourseUser[],
  isGrader: false,
  conflictsOfInterest: [] as string[],
})

const personLoader = new PortalApiDataLoader<GatCoursePersonResponse>(`/portal/api/gat/course/${courseName}/users/${userEmailAddress}/`)
const peopleLoader = new PortalApiDataLoader<GatCourseUsersResponse>(`/portal/api/gat/course/${courseName}/users/`)
personLoader.fetch()
  .then((() => {
    if (!personLoader.state.data) {
      return
    }
    state.conflictsOfInterest = personLoader.state.data.conflicts_of_interest

    peopleLoader.fetch()
      .then((() => {
        if (!peopleLoader.state.data) {
          return
        }

        state.isGrader = personLoader.state.data?.user.is_grader ?? false

        if (state.isGrader) {
          state.roster = peopleLoader.state.data.students
        } else {
          state.roster = peopleLoader.state.data.graders
        }
      }))
  }))

</script>
