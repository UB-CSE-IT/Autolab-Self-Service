<template>
  <div class="element row transition-colors"
       :class="{archived: archived, detail: detail}"
  >
    <div class="left col-grow">
      <q-badge rounded color="primary" label="Archived" v-if="archived"/>

      <p class="text-h5">
        {{ props.gradingAssignment.assessment_display_name }}
        <span class="text-h6 text-grey-8">({{ props.gradingAssignment.assessment_name }})</span>
      </p>
      <p>Created by {{ props.gradingAssignment.created_by_display_name }}
        <span v-if="detail"> ({{ props.gradingAssignment.created_by_email }}) </span>
        on {{ isoDateToLocaleString(props.gradingAssignment.created_at) }}
      </p>
      <template v-if="detail">
        <p>Assignment ID: {{ props.gradingAssignment.id }}</p>
        <p>Autolab assessment: <a :href="autolabAssessmentUrl" target="_blank">{{ autolabAssessmentUrl}}</a></p>
      </template>
    </div>
    <div class="right col-shrink">
      <template v-if="props.showArchiveCheckbox">
        <InstantCheckbox
            v-model="archived"
            :checked-api-data-loader="archiveLoader"
            :unchecked-api-data-loader="unarchiveLoader"
        >
          Archive
        </InstantCheckbox>
      </template>
    </div>
  </div>
</template>


<script setup lang="ts">

import {computed, PropType, ref} from 'vue'
import {GatGradingAssignment} from 'src/types/GradingAssignmentToolTypes'
import {isoDateToLocaleString} from 'src/utilities/DataFormatter'
import InstantCheckbox from 'components/InstantCheckbox.vue'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'

const props = defineProps({
  gradingAssignment: {
    type: Object as PropType<GatGradingAssignment>,
    required: true,
  },
  detail: {
    // Shows more detail, used for the assignment page and successful creation page (not lists)
    type: Boolean,
    default: false,
  },
  showArchiveCheckbox: {
    type: Boolean,
    default: false,
  },
})

const archiveLoader = new PortalApiDataLoader(`/portal/api/gat/course/${props.gradingAssignment?.course.name}/grading-assignments/${props.gradingAssignment.id}/archive/`, 'POST')
const unarchiveLoader = new PortalApiDataLoader(`/portal/api/gat/course/${props.gradingAssignment?.course.name}/grading-assignments/${props.gradingAssignment.id}/archive/`, 'DELETE')
const archived = ref(props.gradingAssignment.archived)
const autolabAssessmentUrl = computed(() =>
    `/courses/${props.gradingAssignment?.course.name}/assessments/${props.gradingAssignment?.assessment_name}`)

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

  &:hover:not(.detail) {
    background-color: $hover;
  }

  .right {
    min-width: 220px;
  }

}

</style>
