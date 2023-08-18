<template>
  <tr>
    <td v-if="showName">{{ user.display_name }}
      <YouBadge v-if="isCurrentUser"/>
    </td>
    <td v-if="showEmail">{{ user.email }}</td>
    <td v-if="showHours" class="row no-wrap content-center items-center" style="min-width: 200px;">
      <q-input dense
               hide-bottom-space
               :loading="hoursLoader.state.loading"
               debounce="1000"
               v-model="hours"
               class="q-mr-sm"
               style="width: 50px;"
      />
      <span v-if="state.updatedHoursSuccessfully" class="text-green">
        <q-icon name="check"/>
        Saved! ({{ serverHours }})
      </span>
      <span v-else-if="state.updatedHoursError" class="text-red-10">
        <q-tooltip anchor="top middle" self="center middle">{{ state.updatedHoursError }}</q-tooltip>
        <q-icon name="error"/>
        Error (hover)
      </span>
    </td>
    <td v-if="showConflicts">
      <RouterLink :to="{name: 'grader-assignment-tool-person', params: {user: user.email}}">
        <span>
          COI
          <q-icon color="primary" name="sports_martial_arts"/>
        </span>
      </RouterLink>
    </td>
  </tr>
</template>

<script setup lang="ts">

import {GatCourseUser} from 'src/types/GradingAssignmentToolTypes'
import {computed, PropType, reactive, ref, watch} from 'vue'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import {useRoute} from 'vue-router'
import {useUserStore} from 'stores/UserStore'
import YouBadge from 'components/YouBadge.vue'

const courseName = useRoute().params.courseName
const userStore = useUserStore()

const props = defineProps({
  user: {
    type: Object as PropType<GatCourseUser>,
    required: true,
  },
  showName: {
    type: Boolean,
    default: true,
  },
  showEmail: {
    type: Boolean,
    default: true,
  },
  showHours: {
    type: Boolean,
    default: true,
  },
  showConflicts: {
    type: Boolean,
    default: true,
  },
})

const isCurrentUser = computed(() => userStore.userData.email == props.user.email)

const hours = ref(props.user.grading_hours?.toString() ?? '')
const serverHours = ref(null as number | null)
const state = reactive({
  updatedHoursSuccessfully: false,
  updatedHoursError: null as string | null,
})

const hoursLoader = new PortalApiDataLoader<GatCourseUser>('', 'POST')

function updateHours() {
  if (isNaN(+hours.value)) {
    // Don't submit if the value is not a number
    return
  }
  hoursLoader.endpoint = `/portal/api/gat/course/${courseName}/users/${props.user.email}/set-grader-hours/${hours.value}/`
  hoursLoader.fetch()
    .then(() => {
      if (!hoursLoader.state.error) {
        // If the hours were successfully updated, update the serverHours value
        serverHours.value = hoursLoader.state.data?.grading_hours ?? 0
        state.updatedHoursSuccessfully = true
        state.updatedHoursError = null
      } else {
        state.updatedHoursSuccessfully = false
        state.updatedHoursError = `Failed to update hours to ${hours.value}: ${hoursLoader.state.error}`
      }
    })
}

watch(hours, updateHours)

</script>
