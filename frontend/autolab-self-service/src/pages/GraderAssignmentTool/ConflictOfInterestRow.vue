<template>
  <tr>
    <td>{{ targetUser.display_name }}</td>
    <td>{{ targetUser.email }}</td>
    <td>
      <q-checkbox v-model="state.conflictOfInterest"
                  :disable="conflictLoader.state.loading"
                  style="width: 150px"
                  @update:modelValue="updateConflictOfInterest($event)">

        <div>
          <span v-if="conflictLoader.state.loading"><q-icon name="upload" class="q-mr-sm"/>Saving...</span>
          <span v-else-if="state.updated">
          <span v-if="state.success" class="text-green"><q-icon name="done" class="q-mr-sm"/>Saved!</span>
            <span v-else class="text-red-10">
              <q-tooltip anchor="top middle" self="center middle">{{ conflictLoader.state.error }}</q-tooltip>
              <q-icon name="error" class="q-mr-sm"/>
              Error (hover)
            </span>
          </span>
        </div>
      </q-checkbox>

    </td>
  </tr>
</template>

<script setup lang="ts">

import {GatConflictOfInterestResponse, GatCourse, GatCourseUser} from 'src/types/GradingAssignmentToolTypes'
import {PropType, reactive} from 'vue'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'

const props = defineProps({
  targetUser: {
    // This is the user whose details are being displayed
    type: Object as PropType<GatCourseUser>,
    required: true,
  },
  currentUser: {
    // This is the user who is listing their conflicts of interest (may not be currently logged-in user)
    type: Object as PropType<GatCourseUser>,
    required: true,
  },
  initiallyConflictOfInterest: {
    type: Boolean,
    required: true,
  },
  course: {
    type: Object as PropType<GatCourse>,
    required: true,
  },
})

const state = reactive({
  conflictOfInterest: props.initiallyConflictOfInterest,
  updated: false,
  success: false,
})

const conflictLoader = new PortalApiDataLoader<GatConflictOfInterestResponse>('')

if (props.currentUser?.is_grader) {
  conflictLoader.endpoint = `/portal/api/gat/course/${props.course.name}/users/${props.currentUser?.email}/conflict-of-interest/${props.targetUser.email}/`
} else {
  conflictLoader.endpoint = `/portal/api/gat/course/${props.course.name}/users/${props.targetUser?.email}/conflict-of-interest/${props.currentUser.email}/`
}

function updateConflictOfInterest(isConflict: boolean) {
  conflictLoader.method = isConflict ? 'POST' : 'DELETE'
  conflictLoader.fetch()
    .then(() => {
      state.updated = true
      state.success = !conflictLoader.state.error
      if (!state.success) {
        state.conflictOfInterest = !isConflict
      }
    })
}
</script>
