<template>
  <tr>
    <td :class="{'text-red-10': checked}">{{ targetUser.display_name }}
      <YouBadge v-if="isCurrentUser"/>
    </td>
    <td :class="{'text-red-10': checked}">{{ targetUser.email }}</td>
    <td>
      <InstantCheckbox v-model="checked"
                       :checked-api-data-loader="addConflictLoader"
                       :unchecked-api-data-loader="removeConflictLoader"
      />
    </td>
  </tr>
</template>

<script setup lang="ts">

import {GatConflictOfInterestResponse, GatCourse, GatCourseUser} from 'src/types/GradingAssignmentToolTypes'
import {PropType, ref} from 'vue'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import {useUserStore} from 'stores/UserStore'
import YouBadge from 'components/YouBadge.vue'
import InstantCheckbox from 'components/InstantCheckbox.vue'

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

const checked = ref(props.initiallyConflictOfInterest)

const userStore = useUserStore()
const isCurrentUser = userStore.userData.email === props.targetUser.email

const addConflictLoader = new PortalApiDataLoader<GatConflictOfInterestResponse>('', 'POST')
const removeConflictLoader = new PortalApiDataLoader<GatConflictOfInterestResponse>('', 'DELETE')


if (props.currentUser?.is_grader) {
  addConflictLoader.endpoint = `/portal/api/gat/course/${props.course.name}/users/${props.currentUser?.email}/conflict-of-interest/${props.targetUser.email}/`
  removeConflictLoader.endpoint = `/portal/api/gat/course/${props.course.name}/users/${props.currentUser?.email}/conflict-of-interest/${props.targetUser.email}/`
} else {
  addConflictLoader.endpoint = `/portal/api/gat/course/${props.course.name}/users/${props.targetUser?.email}/conflict-of-interest/${props.currentUser.email}/`
  removeConflictLoader.endpoint = `/portal/api/gat/course/${props.course.name}/users/${props.targetUser?.email}/conflict-of-interest/${props.currentUser.email}/`
}

</script>
