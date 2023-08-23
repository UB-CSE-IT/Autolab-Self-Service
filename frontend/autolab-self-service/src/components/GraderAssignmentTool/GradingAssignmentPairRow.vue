<template>
  <tr :class="{'complete': complete}" class="transition-colors">
    <td>{{ pair.student_display_name }}</td>
    <td>{{ pair.student_email }}</td>
    <td>
      <a :href="pair.submission_url" target="_blank">Version {{ pair.submission_version }}
        <q-icon class="q-pl-sm" name="open_in_new" size="16px"/>
      </a>
    </td>
    <td>
      <InstantCheckbox
          v-model="complete"
          :checked-api-data-loader="completeLoader"
          :unchecked-api-data-loader="incompleteLoader"
          @update:modelValue="completeUpdated(complete)"
      />
    </td>
  </tr>
</template>

<script setup lang="ts">
import {PropType, ref} from 'vue'
import {GatGradingAssignment, GatGradingAssignmentPairSubmission} from 'src/types/GradingAssignmentToolTypes'
import InstantCheckbox from 'components/InstantCheckbox.vue'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'

const props = defineProps({
  pair: {
    type: Object as PropType<GatGradingAssignmentPairSubmission>,
    required: true,
  },
  assignment: {
    type: Object as PropType<GatGradingAssignment | undefined>,
    required: true,
  },
})

const emits = defineEmits(['completeUpdated'])

const complete = ref(props.pair?.completed ?? false)

function completeUpdated(complete: boolean) {
  emits('completeUpdated', complete)
}

const completeLoader = new PortalApiDataLoader(`/portal/api/gat/course/${props.assignment?.course.name}/
grading-assignments/${props.assignment?.id}/pairs/${props.pair?.pair_id}/complete/`, 'POST')
const incompleteLoader = new PortalApiDataLoader(`/portal/api/gat/course/${props.assignment?.course.name}/
grading-assignments/${props.assignment?.id}/pairs/${props.pair?.pair_id}/complete/`, 'DELETE')

</script>

<style scoped lang="scss">

.complete {
  background-color: lightgrey;
}

</style>
