<template>
  <RouterLink :to="{name: 'grader-assignment-tool-assignment', params: {assignmentId: gradingAssignment.id}}">

    <div class="element" :class="props.gradingAssignment.archived ? 'archived': ''">
      <q-badge rounded color="primary" label="Archived" v-if="gradingAssignment.archived"/>

      <p class="text-h5">{{ props.gradingAssignment.assessment_display_name }}
        <span class="text-h6 text-grey-8">({{ props.gradingAssignment.assessment_name }})</span>
      </p>
      <p>Created by {{ props.gradingAssignment.created_by_display_name }} on
        {{ isoDateToLocaleString(props.gradingAssignment.created_at) }}
      </p>
    </div>
  </RouterLink>
</template>


<script setup lang="ts">

import {PropType} from "vue";
import {GatGradingAssignment} from "src/types/GradingAssignmentToolTypes"
import {isoDateToLocaleString} from "../utilities/DataFormatter";

const props = defineProps({
  gradingAssignment: {
    type: Object as PropType<GatGradingAssignment>,
    required: true
  }
})


</script>

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';

.element {
  border: 2px solid $primary;
  border-radius: 8px;
  padding: 16px;
  margin: 10px 0;
  color: black;

  p {
    margin: 0;
  }

  &.archived {
    background-color: lightgray;
  }

  &:hover {
    background-color: $hover;
  }

}

</style>
