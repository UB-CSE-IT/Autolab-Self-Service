<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to course" color="primary" :to="{name: 'grader-assignment-tool-course'}"/>
    </div>

    <ApiFetchContentContainer :api-data-loader="peopleLoader" loading-text="Loading course roster">
      <h4>{{ peopleLoader.state.data.course.display_name }} Roster</h4>
      <div class="button-row q-my-lg">
        <q-btn icon="sync"
               :loading="syncRosterLoader.state.loading"
               @click="syncRoster"
               label="Sync Roster from Autolab"
               color="primary"
        />
      </div>
      <BannerWithIcon v-if="syncRosterLoader.state.error" icon="error" theme="error">
        {{ syncRosterLoader.state.error }}
      </BannerWithIcon>
      <BannerWithIcon v-else-if="syncRosterLoader.state.loaded" icon="done" theme="success">
        Roster synced successfully.
      </BannerWithIcon>

      <h5>Graders</h5>
      <q-markup-table>
        <thead>
        <tr style="text-align: left">
          <th>Name</th>
          <th>Email Address</th>
          <th>Hours</th>
          <th>Conflicts</th>
        </tr>
        </thead>
        <tbody>
        <PersonRow v-for="user in peopleLoader.state.data?.graders"
                   :key="user.email"
                   :user="user"
        />
        </tbody>
      </q-markup-table>

      <h5>Students</h5>
      <q-markup-table>
        <thead>
        <tr style="text-align: left">
          <th>Name</th>
          <th>Email Address</th>
          <th>Conflicts</th>
        </tr>
        </thead>
        <tbody>
        <PersonRow
          v-for="user in peopleLoader.state.data?.students"
          :key="user.email"
          :user="user"
          :show-hours="false"
        />
        </tbody>
      </q-markup-table>

    </ApiFetchContentContainer>

    <div style="height: 200px;"></div>

  </q-page>
</template>

<script setup lang="ts">

import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import {GatCourseUsersResponse} from 'src/types/GradingAssignmentToolTypes'
import BannerWithIcon from 'components/BannerWithIcon.vue'
import PersonRow from 'components/GraderAssignmentTool/PersonRow.vue'

const courseName = useRoute().params.courseName

const peopleLoader = new PortalApiDataLoader<GatCourseUsersResponse>(`/portal/api/gat/course/${courseName}/users/`)
peopleLoader.fetch()

const syncRosterLoader = new PortalApiDataLoader(`/portal/api/gat/course/${courseName}/autolab-sync/`, 'POST')

function syncRoster() {
  syncRosterLoader.fetch()
    .then(() => {
      if (!syncRosterLoader.state.error) {
        peopleLoader.fetch()
      }
    })
}

</script>
