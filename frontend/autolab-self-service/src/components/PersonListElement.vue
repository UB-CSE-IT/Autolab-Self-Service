<template>
  <div class="container">
    <p><b>{{ props.user.display_name }}</b> ({{ props.user.email }})
      <span class="you-badge" v-if="props.user.is_current_user">Me!</span>
      <RouterLink :to="{name: 'grader-assignment-tool-person', params: {user: props.user.email}}">
          <span>
          <q-tooltip anchor="top middle" self="center middle">Manage conflicts of interest</q-tooltip>
          COI
          <q-icon color="primary" name="sports_martial_arts"/>
          </span>
      </RouterLink>
      <span v-if="state.updatedHoursSuccessfully" class="text-green">
          <q-tooltip anchor="top middle" self="center middle">Hours updated successfully!</q-tooltip>
          Hours: {{ serverHours }}
          <q-icon name="check"/>
    </span>
      <span v-else-if="state.updatedHoursError" class="text-red-10">
          <q-tooltip anchor="top middle" self="center middle">{{ state.updatedHoursError }}</q-tooltip>
          Error (hover)
          <q-icon name="error"/>
      </span>
    </p>


    <span v-if="props.user.is_grader">

    <q-input label="Hours" :loading="hoursLoader.state.loading" debounce="1000" v-model="hours"
             style="width: 50px;"/>
    </span>

  </div>
</template>


<script setup lang="ts">
import {GatCourseUser} from "src/types/GradingAssignmentToolTypes";
import {PropType, reactive, ref, watch} from "vue";
import {PortalApiDataLoader} from "src/utilities/PortalApiDataLoader";
import {useRoute} from "vue-router";

const courseName = useRoute().params.courseName

const props = defineProps({
  user: {
    type: Object as PropType<GatCourseUser>,
    required: true
  }
})
const hours = ref(props.user.grading_hours?.toString() ?? '')
const serverHours = ref(null as number | null)
const state = reactive({
  updatedHoursSuccessfully: false,
  updatedHoursError: null as string | null
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

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';

.container {
  padding: 2px;
  margin: 1px;

  p {
    margin: 0;
  }

  &:hover {
    background-color: $hover;
  }

  .you-badge {
    background-color: $primary;
    color: white;
    padding: 4px 8px;
    border-radius: 8px;
    margin-left: 4px;
  }

}

</style>
